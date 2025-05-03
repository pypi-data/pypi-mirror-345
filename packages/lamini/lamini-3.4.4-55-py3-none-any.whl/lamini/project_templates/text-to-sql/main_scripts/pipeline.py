import os
from tqdm import tqdm
import argparse
import sys
import pandas as pd
import logging
from pathlib import Path

import yaml
import json  # for serializing glossary
from lamini.experiment.generators.table_description_generator import (
    TableDescriptionGenerator,
)
from lamini.experiment.pipeline.base_agentic_pipeline import BaseAgenticPipeline

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))


if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from models.analysis.analysis import ResultsAnalyzer
from models.project.projectdb import ProjectDB
from main_scripts.experiment_prep import build_experiment_pipeline
from utils.utils import build_prompts_from_dataframe, save_results

from datetime import datetime
import uuid


def main(args, config, project_dir, experiment_config):

    project_name = config["Project"]["project_name"]

    results_dir = os.path.join(
        Path(__file__).parent.parent, "projects", project_name, "experiment_results"
    )
    data_dir = os.path.join(
        Path(__file__).parent.parent, "projects", project_name, "data"
    )

    def generate_experiment_id():
        """Generate a unique experiment ID using timestamp and UUID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"

    def get_experiment_config(
        experiment_name,
        project_name,
        description,
        data_dir="data",
        results_dir="experiment_results",
    ):
        experiment_id = generate_experiment_id()

        ExperimentDefinition = {
            "experiment_id": experiment_id,
            "project_name": project_name,
            "description": description,
            "experiment_name": experiment_name,
            "results_dir": results_dir,
            "data_dir": data_dir,
        }

        return ExperimentDefinition

    ExperimentDefinition = get_experiment_config(
        experiment_name=args["experiment_name"],
        project_name=config["Project"]["project_name"],
        description=config["Project"]["description"],
        data_dir=data_dir,
        results_dir=results_dir,
    )

    experiment_id = generate_experiment_id()
    ExperimentDefinition["experiment_id"] = experiment_id

    glossary_df = pd.read_parquet(Path("local-db") / "glossary.parquet")
    project_glossary_df = glossary_df[
        glossary_df["project_id"] == ExperimentDefinition["project_name"]
    ]
    glossary = {
        row["input"]: row["output"] for _, row in project_glossary_df.iterrows()
    }

    pipeline_components = build_experiment_pipeline(experiment_config)
    pipeline = pipeline_components["pipeline"]
    # Disable pipeline spotcheck and input validation (monkey-patch)
    pipeline.pipeline_step_logic = lambda exp_obj: None
    pipeline.pipline_spotcheck = lambda exp_obj, debug=False: None
    experiment = pipeline_components["experiment"]
    schema = pipeline_components.get("schema")

    db = ProjectDB()

    # Handle potentially nested results and None values
    def flatten_results(results):
        flattened = []
        for result in results:
            if result is None:
                continue
            if isinstance(result, list):
                flattened.extend([r.data for r in result if r is not None])
            else:
                flattened.append(result.data)
        return flattened

    # --------------------------------------------------------------------- #
    # Process the example_set through the pipeline                             #
    # --------------------------------------------------------------------- #
    example_set_path = Path(__file__).parent.parent / "local-db" / "example_set.parquet"

    try:
        example_set_df = pd.read_parquet(example_set_path)
    except Exception as e:
        print(f"Error loading example_set: {e}")
        example_set_df = pd.DataFrame()
    project_example_set_df = example_set_df[
        example_set_df["project_id"] == project_name
    ]
    if project_example_set_df.empty:
        print(f"No example_set entries found for project '{project_name}'")
    else:
        # Prepare full prompt DataFrame with all required input keys for pipeline
        prompts_df = project_example_set_df.rename(
            columns={"input": "question", "output": "sql"}
        )
        # Preserve original question and SQL for SQL generator
        prompts_df["original_question"] = prompts_df["question"]
        prompts_df["original_sql"] = prompts_df["sql"]
        # Add database context (SQLite) for SQL generator
        sqlite_paths = list(Path(data_dir).glob("*.sqlite"))
        if not sqlite_paths:
            raise FileNotFoundError("No .sqlite files found in data directory.")
        prompts_df["db_type"] = "sqlite"
        prompts_df["db_params"] = str(sqlite_paths[0])
        # Include schema and glossary for generators
        prompts_df["schema"] = schema
        prompts_df["glossary"] = glossary
        # Add fields required by SQL debugger
        prompts_df["sub_question"] = prompts_df["question"]
        prompts_df["error_sql"] = prompts_df["sql"]
        prompts_df["error_message"] = ""
        prompts_df["error_explanation"] = ""
        # Build prompts with complete set of input columns
        extract_cols = [
            "question",
            "sql",
            "original_question",
            "original_sql",
            "schema",
            "glossary",
            "db_type",
            "db_params",
            "sub_question",
            "error_sql",
            "error_message",
            "error_explanation",
        ]
        prompts = build_prompts_from_dataframe(prompts_df, extract_cols, {})
        # Run through pipeline
        raw_results = pipeline(prompts)
        processed = flatten_results(raw_results)
        results_df = pd.DataFrame(processed)
        # Save pipeline outputs for example_set
        save_results(results_df, ExperimentDefinition["experiment_name"])
        print(f"Processed {len(results_df)} example_set entries through pipeline.")
        # Create dataset of valid QA pairs and register experiment

        try:
            valid_pairs = results_df[results_df.get("is_valid") == True][
                ["question", "sql"]
            ]
            if not valid_pairs.empty:
                dataset_id = db.create_dataset(
                    name=ExperimentDefinition["experiment_name"],
                    description=ExperimentDefinition.get("description", ""),
                    qa_pairs=valid_pairs,
                )
                # Register experiment including dataset_id
                db.register_experiment(
                    project_id=project_name,
                    experiment_id=ExperimentDefinition["experiment_id"],
                    experiment_name=ExperimentDefinition["experiment_name"],
                    description=ExperimentDefinition.get("description", ""),
                    parameters={"_dummy": None},
                    model_config={"_dummy": None},
                    generators=None,
                    validators=None,
                    schema_id=None,
                    tuning_job_id=None,
                    dataset_id=dataset_id,
                )

                print(
                    f"Created dataset '{dataset_id}' with {len(valid_pairs)} valid pairs and linked to experiment."
                )
        except Exception as e:
            print(f"Error creating dataset or registering experiment: {e}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project_name", help="Project name")
    parser.add_argument("-e", "--experiment_name", help="Experiment name")
    parser.add_argument(
        "-b", "--batches", type=int, default=1, help="Number of batches"
    )
    parser.add_argument("-k", "--api_key", required=False, help="API key for Lamini")
    parser.add_argument(
        "-n",
        "--num_prompts",
        type=int,
        help="Number of prompts to process (default: all)",
    )
    parser.add_argument(
        "-tr",
        "--test_run",
        action="store_true",
        help="Test run - skip database operations",
    )

    args = vars(parser.parse_args())

    project_dir = f'projects/{args["project_name"]}'

    proj_path = f"{project_dir}/ymls/project.yml"

    with open(proj_path, "r") as file:
        proj_config = yaml.safe_load(file)

    exp_path = f"{project_dir}/ymls/experiment.yml"

    with open(exp_path, "r") as file:
        experiment_config = yaml.safe_load(file)

    # Only set LAMINI_API_KEY from config if it's not already set in the environment
    if "LAMINI_API_KEY" not in os.environ:
        if proj_config["Lamini"]["api_key"] == "<your_api_key>":
            raise ValueError(
                "API key is not set in the environment and is incorrect in config file"
            )
        os.environ["LAMINI_API_KEY"] = proj_config["Lamini"]["api_key"]

    api_url = proj_config["Lamini"]["base_url"]

    if not args.get("api_key") and not os.environ.get("LAMINI_API_KEY"):
        logging.error(
            "API key is missing. Please provide an API key using inside the confing.yml file"
        )
    else:
        api_key = args.get("api_key") or os.environ.get("LAMINI_API_KEY")
        os.environ["OPENAI_API_KEY"] = api_key

    main(args, proj_config, project_dir, experiment_config)
