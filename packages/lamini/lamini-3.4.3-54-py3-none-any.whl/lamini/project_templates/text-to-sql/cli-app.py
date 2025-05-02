import subprocess
import os
import sys
import yaml
from prettytable import PrettyTable
import pandas as pd
import time
from pathlib import Path
from tqdm import tqdm
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import shutil
from models.project.projectdb import ProjectDB
import json
import re
import sqlite3
from lamini.generation.base_prompt_object import PromptObject

# Glossary generator import
from lamini.experiment.generators.glossary_generator import GlossaryGenerator
from utils import vscode_installer
from utils.plugin_install import install_vscode_extension

# Add the parent directory (factual_qa_pipeline/) to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from utils.utils import clean_pycache

# Global to hold whatever project the user last selected/created/activated
current_project = None
current_experiment = None
try:
    df_exp = pd.read_parquet("local-db/experiments.parquet")
    df_proj = pd.read_parquet("local-db/projects.parquet")
    list_projects = df_proj["project_name"].to_list()
except Exception as e:
    db = ProjectDB()
    df_exp = pd.read_parquet("local-db/experiments.parquet")
    df_proj = pd.read_parquet("local-db/projects.parquet")
    list_projects = df_proj["project_name"].to_list()


def update_yml(project_name, yml_type, param, value):
    """
    Update a value in a YAML file using a colon-separated path.

    Args:
        project_name (str): Name of the project
        yml_type (str): Type of yml file to update (e.g., 'experiment', 'project')
        param (str): Colon-separated path to the parameter (e.g., 'parent:child1:child2')
        value: Value to set

    Example:
    """
    # Load the YAML file
    yml_path = os.path.join(
        Path(__file__).parent, "projects", project_name, "ymls", f"{yml_type}.yml"
    )
    with open(yml_path, "r") as file:
        loaded_yml = yaml.safe_load(file)

    # Split the parameter path
    path_parts = param.split(":")

    # Navigate to the nested location
    current = loaded_yml
    for i, part in enumerate(path_parts[:-1]):  # All parts except the last one
        if part not in current:
            raise KeyError(
                f"Path '{':'.join(path_parts[:i+1])}' not found in {yml_type}.yml"
            )
        current = current[part]

    # Set the value at the final location
    last_part = path_parts[-1]
    if last_part not in current:
        raise KeyError(f"Final key '{last_part}' not found in {yml_type}.yml")
    current[last_part] = value

    # Save the updated YAML
    with open(yml_path, "w") as file:
        yaml.dump(loaded_yml, file, default_flow_style=False)


def print_banner():
    print("=" * 100)
    print(" Welcome to the Lamini CLI ".center(100, " "))
    print(" text-to-sql ".center(100, " "))
    if current_project:
        # show the active project on its own line, centered
        header = f"Active project: {current_project}"
        print(header.center(100, " "))
    if current_experiment:
        # show the active experiment on its own line, centered
        exp_header = f"Active experiment: {current_experiment}"
        print(exp_header.center(100, " "))
    print("=" * 100)


def print_options():
    print("\nPlease choose an option from the following tasks:")
    print("  [1] Start a new project")
    print("  [2] Update an existing project with the latest configurations")
    print("  [3] Activate an existing project for local use")
    print("  [q] Quit")
    print("=" * 100)


def display_dataframe_as_table(df, title):
    """Display a pandas DataFrame as a prettytable in the CLI with truncated data for readability"""
    MAX_WIDTH = 30  # Maximum width for any column

    table = PrettyTable()
    table.title = title
    table.field_names = df.columns.tolist()

    # Set max width for all columns
    for column in df.columns:
        table.max_width[column] = MAX_WIDTH

    # Function to truncate text
    def truncate_text(text):
        if isinstance(text, str) and len(text) > MAX_WIDTH:
            return text[: MAX_WIDTH - 3] + "..."
        return text

    # Add rows with truncated values
    for _, row in df.iterrows():
        truncated_row = [truncate_text(val) for val in row.tolist()]
        table.add_row(truncated_row)

    print(table)


def load_jsonl_to_parquet(jsonl_path, parquet_path, description):
    """Load data from a JSONL file into a Parquet file."""
    try:
        with open(jsonl_path, "r") as f:
            data = [json.loads(line) for line in f]
        df = pd.DataFrame(data)
        df.to_parquet(parquet_path, index=False)
        print(f"Loaded {description} from {jsonl_path} into {parquet_path}")
    except Exception as e:
        print(f"Error loading {description}: {str(e)}")


def is_vscode_available() -> bool:
    """Return True if VS Code's `code` CLI is available on the system PATH."""
    return shutil.which("code") is not None


def is_extension_installed(extension_id: str) -> bool:
    """Check if a VS Code extension is already installed."""
    try:
        output = subprocess.check_output(["code", "--list-extensions"], text=True)
        installed = [ext.strip() for ext in output.splitlines()]
        return extension_id in installed
    except Exception:
        # Either `code` is not available or another error occurred
        return False


# TODO: this needs to be replaced and do not ship it to public with this plugin. This is for internal use as of now
if is_vscode_available():
    # Ensure the 'code' command is available on macOS (adds shell helper if needed)
    vscode_installer.apply()
    parquet_ext = "lucien-martijn.parquet-visualizer"
    if not is_extension_installed(parquet_ext):
        ext_choice = (
            input(
                f"The VS Code extension '{parquet_ext}' is not installed. Install it now? (y/N): "
            )
            .strip()
            .lower()
        )
        if ext_choice == "y":
            install_vscode_extension(parquet_ext)


def get_next_project_version(project_name: str) -> str:
    """Get the next version number for a project name."""
    # Extract base name and version if it exists
    match = re.match(r"(.+?)(?:_(\d+))?$", project_name)
    if not match:
        return f"{project_name}_1"

    base_name, version = match.groups()
    if version is None:
        return f"{base_name}_1"

    return f"{base_name}_{int(version) + 1}"


def main():
    global current_project, current_experiment

    clean_pycache()
    # Initialize the database
    db = ProjectDB()

    def load_jsonl_to_parquet_with_project_id(
        jsonl_path, parquet_path, description, project_id
    ):
        """Load data from a JSONL file into a Parquet file with project_id."""
        try:
            with open(jsonl_path, "r") as f:
                data = [json.loads(line) for line in f]
            df = pd.DataFrame(data)
            df["project_id"] = project_id  # Add project_id to the DataFrame
            df.to_parquet(parquet_path, index=False)
            print(f"Loaded {description} from {jsonl_path} into {parquet_path}")
        except Exception as e:
            print(f"Error loading {description}: {str(e)}")

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print_banner()
        print_options()
        df_exp = pd.read_parquet("local-db/experiments.parquet")
        df_proj = pd.read_parquet("local-db/projects.parquet")
        list_projects = df_proj["project_name"].to_list()

        choice = input("Enter your choice [1/2/3/4/q]: ").strip()
        if choice == "q":
            print("\nExiting CLI. Goodbye!")
            break

        if choice not in ["1", "2", "3", "4"]:
            print("\nInvalid choice. Try again.")
            input("Press Enter to continue...")
            continue

        if choice == "1":
            project_completer = WordCompleter(
                list_projects, ignore_case=True, sentence=True
            )

            project_name = prompt(
                "Enter project name: ", completer=project_completer
            ).strip()

            if project_name in list_projects:
                # Auto-increment project name
                new_project_name = get_next_project_version(project_name)
                print(
                    f"Project '{project_name}' already exists. Creating new version: '{new_project_name}'"
                )
                project_name = new_project_name
                time.sleep(1)
            else:
                print(f"🆕  Creating new project '{project_name}'")
                print("=" * 100)

            if not project_name:
                print("\nProject name cannot be empty. Try again.")
                input("Press Enter to continue...")
                continue

            if "LAMINI_API_KEY" not in os.environ:
                print("\nLAMINI_API_KEY environment variable is missing.")
                while "LAMINI_API_KEY" not in os.environ:
                    api_key = input("Please enter your LAMINI_API_KEY: ").strip()
                    if api_key:
                        os.environ["LAMINI_API_KEY"] = api_key
                        # Update the template file with the API key
                        template_path = os.path.join(
                            Path(__file__).parent, "yml-templates", "project.yml"
                        )
                        with open(template_path, "r") as file:
                            template = yaml.safe_load(file)
                        template["Lamini"]["api_key"] = api_key
                        with open(template_path, "w") as file:
                            yaml.dump(template, file)
                        os.system("cls" if os.name == "nt" else "clear")
                        print_banner()
                        break
                    else:
                        print("API key cannot be empty. Please try again.")

            # Get SQLite database path from user
            sqlite_db_path = input("Enter the path to your SQLite database: ").strip()
            if not os.path.isfile(sqlite_db_path):
                print("Invalid path. Please ensure the file exists.")
                return
            # Prompt for evaluation set JSONL file
            evalset_jsonl_path = input(
                "Enter the path to the evaluation set JSONL file: "
            ).strip()
            # Copy the SQLite database to the project folder
            project_db_path = os.path.join(
                Path(__file__).parent,
                "projects",
                project_name,
                "data",
                os.path.basename(sqlite_db_path),
            )
            os.makedirs(os.path.dirname(project_db_path), exist_ok=True)
            shutil.copy(sqlite_db_path, project_db_path)
            print(f"SQLite database copied to {project_db_path}")

            subprocess.run(
                [
                    "python",
                    "main_scripts/init_project.py",
                    "--project_name",
                    project_name,
                ]
            )
            with open(
                os.path.join(
                    Path(__file__).parent,
                    "projects",
                    project_name,
                    "ymls",
                    "experiment.yml",
                ),
                "r",
            ) as file:
                exp_file = yaml.safe_load(file)
            with open(
                os.path.join("projects", project_name, "ymls", "project.yml"), "r"
            ) as file:
                project_file = yaml.safe_load(file)

            project_file["Project"]["project_name"] = project_name
            project_file["Lamini"]["api_key"] = os.environ["LAMINI_API_KEY"]

            with open(
                os.path.join("projects", project_name, "ymls", "project.yml"), "w"
            ) as file:
                yaml.dump(project_file, file)

            print(
                f"\nProject '{project_name}' is set up in the 'projects' folder. Please feel free to adjust YML files as needed."
            )
            print(
                "\nPlease Note: The pipeline will generate data based on the examples you provided. If none are available, we will use the evaluation file. Please note that it is recommended to use a separate set for examples.\n"
            )
            example_set_jsonl_path = input(
                "Enter the path to the example_set JSONL file (optional): "
            ).strip()

            # Prompt for glossary
            glossary_jsonl_path = input(
                "Enter the path to the glossary JSONL file (optional): "
            ).strip()

            if not example_set_jsonl_path:
                example_set_jsonl_path = evalset_jsonl_path
                print("No example set provided; using evaluation set as example set.")

            # Load glossary and example_set into Parquet files
            glossary_parquet_path = os.path.join(db.base_dir, "glossary.parquet")
            example_set_parquet_path = os.path.join(db.base_dir, "example_set.parquet")
            evalset_parquet_path = os.path.join(db.base_dir, "evalset.parquet")

            # Load glossary into Parquet or generate it if not provided
            if glossary_jsonl_path:
                load_jsonl_to_parquet_with_project_id(
                    glossary_jsonl_path, glossary_parquet_path, "glossary", project_name
                )
            else:
                print(
                    "No glossary provided; generating glossary using GlossaryGenerator..."
                )
                # Infer schema from the project's SQLite database
                conn = sqlite3.connect(project_db_path)
                cursor = conn.cursor()
                tables = cursor.execute(
                    "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
                ).fetchall()
                schema = "\n".join(sql for _, sql in tables)
                conn.close()

                # Load questions from the evaluation set JSONL
                with open(evalset_jsonl_path, "r") as f:
                    eval_entries = [json.loads(line) for line in f]
                queries = "\n".join(entry.get("input", "") for entry in eval_entries)

                # Instantiate and run the glossary generator
                glossary_gen = GlossaryGenerator(
                    api_key=os.environ.get("LAMINI_API_KEY"),
                    model=project_file["Project"]["model"],
                )

                glossary_prompt = PromptObject(
                    prompt="",
                    data={
                        "schema": schema,
                        "queries": queries,
                        "input_glossary": "",
                    },
                )

                glossary_result = glossary_gen(glossary_prompt)
                glossary_entries = glossary_result.data.get("glossary", [])
                # Save generated glossary to Parquet
                df_glossary = pd.DataFrame(glossary_entries)
                df_glossary["project_id"] = project_name
                df_glossary.to_parquet(glossary_parquet_path, index=False)
                print("Glossary generated and saved to Parquet file.")

            load_jsonl_to_parquet_with_project_id(
                example_set_jsonl_path,
                example_set_parquet_path,
                "example_set",
                project_name,
            )
            load_jsonl_to_parquet_with_project_id(
                evalset_jsonl_path, evalset_parquet_path, "evalset", project_name
            )
            print("\nParquet files created. Restarting CLI to pick up new data...")
            time.sleep(1)
            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif choice == "2":

            project_completer = WordCompleter(
                list_projects, ignore_case=True, sentence=True
            )

            project_name = prompt(
                "Enter project name: ", completer=project_completer
            ).strip()

            if not project_name:
                print("\nProject name cannot be empty. Try again.")
                input("Press Enter to continue...")
                continue

            if project_name not in list_projects:
                print(
                    f'\nProject "{project_name}" does not exist. Returning to the main menu.'
                )
                for _ in tqdm(range(50), bar_format="{bar}"):
                    time.sleep(0.1)
                continue

            print(f'✅  Using existing project "{project_name}"')
            print("=" * 100)

            subprocess.run(
                [
                    "python",
                    "main_scripts/init_project.py",
                    "--project_name",
                    project_name,
                    "--update",
                ]
            )

        elif choice == "3":
            project_completer = WordCompleter(
                list_projects, ignore_case=True, sentence=True
            )

            project_name = prompt(
                "Enter project name: ", completer=project_completer
            ).strip()

            if not project_name:
                print("\nProject name cannot be empty. Try again.")
                input("Press Enter to continue...")
                continue

            if project_name not in list_projects:
                print(
                    f'\nProject "{project_name}" does not exist. Returning to the main menu.'
                )
                for _ in tqdm(range(50), bar_format="{bar}"):
                    time.sleep(0.1)
                continue

            print(f'✅  Using existing project "{project_name}"')
            print("=" * 100)

            # Determine the original project directory name by stripping any trailing version-like suffix (_X, _X.Y, _X.Y.Z, ...)
            project_name_org = re.sub(r"(?:_\d+(?:\.\d+)*)+$", "", project_name)

            with open(
                os.path.join(
                    Path(__file__).parent,
                    "projects",
                    project_name_org,
                    "ymls",
                    "experiment.yml",
                ),
                "r",
            ) as file:
                exp_file = yaml.safe_load(file)

            if not os.path.exists(os.path.join("projects", project_name_org)):
                print(
                    f"\nProject '{project_name_org}' does not exist. Returning to the main menu."
                )
                for _ in tqdm(range(50), bar_format="{bar}"):
                    time.sleep(0.1)
                continue

            if "LAMINI_API_KEY" not in os.environ:
                with open(
                    os.path.join("projects", project_name_org, "ymls", "project.yml"),
                    "r",
                ) as file:
                    project_file = yaml.safe_load(file)
                os.environ["LAMINI_API_KEY"] = project_file["Lamini"]["api_key"]

            while True:
                os.system("cls" if os.name == "nt" else "clear")
                print_banner()
                print("=" * 100)
                print("\nWhat would you like to do with the activated project?")
                print("  [d] Perform data generation")
                print("  [t] Tune the model")
                print("  [i] Run inference")
                print("  [m] Monitor project data")
                print("  [e] Evaluate model performance")
                print("  [r] Return to main menu")
                print("  [q] Quit")
                print("=" * 100)

                action_choice = (
                    input("Enter your choice [d/t/i/m/e/a/r/q]: ").strip().lower()
                )
                if action_choice not in ["d", "t", "i", "m", "e", "a", "r", "q"]:
                    print("\nInvalid choice. Try again.")
                    input("Press Enter to continue...")
                    continue

                if action_choice == "d":
                    print("\nData Generation Steps:")
                    print(
                        "  Step 1: Use generators to generate pairs of questions and SQL queries."
                    )
                    print(
                        "  Step 2: Use validators and connection to your SQLite database to validate generated SQL queries."
                    )
                    print(
                        "  Step 3: Use SQL debugger to correct any incorrect queries."
                    )
                    print("  Step 4: Assemble the final dataset.")
                    print("=" * 100)
                    print("\nPerforming data generation...")
                    print("=" * 100)

                    filtered_df_exp = df_exp[df_exp["project_id"] == project_name_org]
                    list_experiments = filtered_df_exp["experiment_name"].to_list()
                    while True:
                        experiment_completer = WordCompleter(
                            list_experiments, ignore_case=True, sentence=True
                        )

                        experiment_name = prompt(
                            "Enter experiment name (press Enter for default): ",
                            completer=experiment_completer,
                        ).strip()

                        if (
                            not experiment_name
                        ):  # If no name provided, use timestamp-based default
                            from datetime import datetime

                            experiment_name = (
                                f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            )
                            print(
                                f"🆕  Using default experiment name: '{experiment_name}'"
                            )
                            break

                        if experiment_name in list_experiments:
                            print(
                                f"❌  Experiment name '{experiment_name}' already exists. Please try another."
                            )
                        else:
                            print(f"🆕  Creating new experiment '{experiment_name}'")
                            break  # Exit the loop if a unique experiment name is entered

                    current_experiment = experiment_name

                    exp_file["Experiment"]["experiment_name"]["value"] = experiment_name
                    with open(
                        os.path.join(
                            Path(__file__).parent,
                            "projects",
                            project_name_org,
                            "ymls",
                            "experiment.yml",
                        ),
                        "w",
                    ) as file:
                        yaml.dump(exp_file, file)

                    pipeline_command = [
                        "python",
                        "main_scripts/pipeline.py",
                        "--project_name",
                        project_name_org,
                        "--experiment_name",
                        experiment_name,
                    ]

                    subprocess.run(pipeline_command)

                elif action_choice == "t":
                    print("\nModel Tuning Steps:")
                    print("  Step 1: Prepare training dataset and hyperparameters.")
                    print(
                        "  Step 2: Train or fine-tune the model with the prepared dataset."
                    )
                    print("  Step 3: Evaluate performance on the validation set.")
                    print("  Step 4: Save the tuned model.")
                    print("=" * 100)
                    print("\nTuning the model...")
                    filtered_df_exp = df_exp[df_exp["project_id"] == project_name_org]
                    list_experiments = filtered_df_exp["experiment_name"].to_list()

                    while True:
                        experiment_completer = WordCompleter(
                            list_experiments, ignore_case=True, sentence=True
                        )

                        experiment_name = prompt(
                            "Enter experiment name: ", completer=experiment_completer
                        ).strip()

                        if experiment_name not in list_experiments:
                            print(
                                f"❌  Experiment name '{experiment_name}' does not exist. Please choose an existing experiment."
                            )
                        else:
                            print(f"✅  Using existing experiment '{experiment_name}'")
                            current_experiment = (
                                experiment_name  # Assign within proper scope
                            )
                            break  # Exit the loop if a valid existing experiment name is entered

                    output_file_path = input(
                        "Enter the output file path (optional): "
                    ).strip()
                    output_format = (
                        input(
                            "Enter the output format (choices: csv, parquet, json, default: csv): "
                        )
                        .strip()
                        .lower()
                    )

                    if output_format not in ["csv", "parquet", "json"]:
                        print("\nInvalid format. Defaulting to 'csv'.")
                        output_format = "csv"

                    train_command = [
                        "python",
                        "main_scripts/train.py",
                        "--experiment_name",
                        experiment_name,
                        "--project_name",
                        project_name,
                        "--format",
                        output_format,
                    ]

                    if output_file_path:
                        train_command.extend(["--output", output_file_path])

                    subprocess.run(train_command)
                elif action_choice == "i":
                    print("\nInference Steps:")
                    print("  Step 1: Load the evaluation data.")
                    print(
                        "  Step 2: Use the model to generate predictions or SQL queries."
                    )
                    print("  Step 3: Collect and save inference results.")
                    print("=" * 100)
                    print("\nRunning inference...")
                    breakpoint
                    inference_command = [
                        "python",
                        "main_scripts/inference.py",
                        "--project",
                        project_name_org,
                    ]

                    subprocess.run(inference_command)
                elif action_choice == "m":
                    print("\nMonitoring Steps:")
                    print("  Step 1: Load current data from local-db.")
                    print(
                        "  Step 2: Display metrics and logs for datasets, experiments, prompts, and results."
                    )
                    print("=" * 100)
                    print("\nMonitoring project data...")
                    while True:
                        print("\nSelect data to monitor:")
                        print("  [1] Datasets")
                        print("  [2] Experiments")
                        print("  [3] Prompts")
                        print("  [4] Results")
                        print("  [b] Back to project menu")

                        monitor_choice = (
                            input("\nEnter your choice [1/2/3/4/b]: ").strip().lower()
                        )

                        if monitor_choice == "b":
                            break

                        try:
                            if monitor_choice == "1":
                                # Display datasets data
                                datasets_df = pd.read_parquet(
                                    "local-db/datasets.parquet"
                                )
                                display_dataframe_as_table(datasets_df, "Datasets")
                            elif monitor_choice == "2":
                                # Display experiments data
                                experiments_df = pd.read_parquet(
                                    "local-db/experiments.parquet"
                                )
                                display_dataframe_as_table(
                                    experiments_df, "Experiments"
                                )
                            elif monitor_choice == "3":
                                # Display prompts data
                                prompts_df = pd.read_parquet("local-db/prompts.parquet")
                                display_dataframe_as_table(prompts_df, "Prompts")
                            elif monitor_choice == "4":
                                # Display results data
                                results_df = pd.read_parquet("local-db/results.parquet")
                                display_dataframe_as_table(results_df, "Results")
                            else:
                                print("\nInvalid choice. Try again.")
                        except Exception as e:
                            print(f"\nError loading data: {str(e)}")

                        input("\nPress Enter to continue...")
                elif action_choice == "e":
                    print("\nModel Evaluation Steps:")
                    print("  Step 1: Load evaluation dataset.")
                    print("  Step 2: Run evaluation metrics calculation.")
                    print("  Step 3: Display and save evaluation results.")
                    print("=" * 100)
                    print("\nEvaluating model performance...")

                    eval_command = [
                        "python",
                        "main_scripts/evaluate.py",
                        "--project_name",
                        project_name,
                    ]

                    subprocess.run(eval_command)

                elif action_choice == "r":
                    print("\nReturning to main menu...")
                    break

                elif action_choice == "q":
                    print("\nExiting CLI. Goodbye!")
                    exit()

                input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
