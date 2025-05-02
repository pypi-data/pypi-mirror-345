import os
import sys
import argparse
import random
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime
import uuid
import yaml

# Ensure parent directory (Pipeline_qa/) is on sys.path so we can import project modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.utils import build_prompts_from_dataframe
from main_scripts.experiment_prep import build_experiment_pipeline
from models.project.projectdb import ProjectDB
from models.analysis.analysis import ResultsAnalyzer  # Only used for pretty print

logging.getLogger('pypdf').setLevel(logging.ERROR)

def flatten_results(results):
    """Utility to flatten potentially nested Lamini experiment results."""
    flattened = []
    for result in results:
        if result is None:
            continue
        if isinstance(result, list):
            flattened.extend([r.data for r in result if r is not None])
        else:
            flattened.append(result.data)
    return flattened

def generate_eval_dataset(project_name:str, experiment_name:str, sample_frac:float = 0.2, random_state:int = 42, recursive_chunk:bool = False):
    """
    Generates an evaluation dataset by sampling a fraction of chunks from an existing experiment, running the
    question/answer/validator pipeline, and saving the results to both the local database and a parquet file.
    """
    
    base_dir_local_db = Path(__file__).parent.parent / "local-db"
    chunks_path = base_dir_local_db / "chunks.parquet"

    if not chunks_path.exists():
        raise FileNotFoundError("chunks.parquet not found. Please generate data first using option 'd'.")

    # Load chunks and filter by experiment
    chunks_df = pd.read_parquet(chunks_path)
    filtered_chunks_df = chunks_df[chunks_df['experiment_name'] == experiment_name]

    if filtered_chunks_df.empty:
        raise ValueError(f"No chunks found for experiment '{experiment_name}'.")

    # Sample chunks
    sample_df = filtered_chunks_df.sample(frac=sample_frac, random_state=random_state) if sample_frac < 1.0 else filtered_chunks_df.copy()

    # Retrieve project metadata for prompts additional data
    proj_yml_path = Path(__file__).parent.parent / 'projects' / project_name / 'ymls' / 'project.yml'
    if not proj_yml_path.exists():
        raise FileNotFoundError(f"Project yml not found at {proj_yml_path}")

    with open(proj_yml_path, 'r') as f:
        project_config = yaml.safe_load(f)

    additional_data = {
        "product": project_config['document_metadata']['product'],
        "keywords": project_config['document_metadata']['keywords'],
        "title": project_config['document_metadata']['title'],
        "description": project_config['document_metadata']['description']
    }

    # Build prompts from sampled chunks
    extract_columns = [col for col in sample_df.columns if col != 'content_hash']  # we can include most columns
    prompts = build_prompts_from_dataframe(sample_df, extract_columns=extract_columns, additional_data=additional_data)

    
    # Optionally apply recursive chunking to prompt data
    if recursive_chunk:
        # Load original experiment config to get chunk_size
        exp_yml_path = Path(__file__).parent.parent / 'projects' / project_name / 'ymls' / 'experiment.yml'
        with open(exp_yml_path, 'r') as f:
            exp_config = yaml.safe_load(f)
        chunk_size_val = exp_config['Experiment']['chunk_size']['value']
        from utils.utils import generate_question_chunks
        prompts = generate_question_chunks(prompts, chunk_size=chunk_size_val)

    # Create a lightweight ExperimentDefinition for pipeline building
    ExperimentDefinition = {
        "experiment_id": f"{experiment_name}_eval_{uuid.uuid4().hex[:8]}",
        "project_name": project_name,
        "experiment_name": experiment_name,
        "description": f"Evaluation dataset generation for experiment {experiment_name}",
    }

    # Build pipeline components (reuses roles/prompts)
    pipeline_components = build_experiment_pipeline(ExperimentDefinition)
    experiment = pipeline_components["experiment"]
    # Execute experiment
    results = experiment(prompts)
    flattened_results = flatten_results(results)
    results_df = pd.DataFrame(flattened_results)
    results_df_dataset = results_df[["question_generator_output", "answer_generator_output", "FactValidator_output"]]

    # Save dataset to DB
    db = ProjectDB()
    dataset_id = db.create_dataset(
        name=f"eval_dataset_{experiment_name}",
        description="Evaluation Q&A set",
        qa_pairs=results_df_dataset
    )
    # Update experiment record with eval dataset id
    db.update_experiment_eval_dataset_id(experiment_name=experiment_name, eval_dataset_id=dataset_id)

    # Save a physical parquet file inside project/eval_data
    eval_data_dir = Path(__file__).parent.parent / 'projects' / project_name / 'eval_data'
    eval_data_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = eval_data_dir / 'evalset.parquet'
    results_df_dataset.to_parquet(parquet_path, index=False)
    # Print brief summary
    print(f"Evaluation dataset saved to {parquet_path}")
    total = len(results_df_dataset)
    valid = results_df_dataset['FactValidator_output'].apply(lambda x: x.get('is_valid') if isinstance(x, dict) else False).sum()
    validity_rate = round((valid/total)*100, 2) if total else 0.0
    print(f"Total Q&A pairs: {total} | Valid pairs: {valid} | Validity rate: {validity_rate}%")

    # Optionally print a sample
    if not results_df_dataset.empty:
        print("\nSample Eval Result:")
        sample = results_df_dataset.iloc[0]
        print(sample)

    return parquet_path, dataset_id


def main():
    parser = argparse.ArgumentParser(description="Generate evaluation dataset from existing experiment chunks")
    parser.add_argument('-p', '--project_name', required=True, help='Project name')
    parser.add_argument('-e', '--experiment_name', required=True, help='Existing experiment name to sample chunks from')
    parser.add_argument('-f', '--sample_frac', type=float, default=0.2, help='Fraction of chunks to sample (default 0.2)')
    parser.add_argument('--random_state', type=int, default=42, help='Random seed')
    parser.add_argument('--recursive_chunk', action='store_true', help='Enable recursive chunking of prompts')
    args = parser.parse_args()

    generate_eval_dataset(
        project_name=args.project_name,
        experiment_name=args.experiment_name,
        sample_frac=args.sample_frac,
        random_state=args.random_state,
        recursive_chunk=args.recursive_chunk
    )

if __name__ == "__main__":
    main() 