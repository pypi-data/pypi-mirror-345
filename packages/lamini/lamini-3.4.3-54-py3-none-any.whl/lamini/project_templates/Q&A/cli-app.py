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
import re
from models.project.projectdb import ProjectDB

db = ProjectDB()


# Add the parent directory (factual_qa_pipeline/) to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from utils.utils import clean_pycache

# Global to hold whatever project the user last selected/created/activated
current_project = None
current_experiment = None

df_exp = pd.read_parquet("local-db/experiments.parquet")
df_proj = pd.read_parquet("local-db/projects.parquet")
list_projects = df_proj["project_name"].to_list()


def print_banner():
    print("=" * 100)
    print(" Welcome to the Lamini CLI ".center(100, " "))
    print(" Factual Q&A ".center(100, " "))
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


def update_yml(project_name, yml_type, param, value):
    """
    Update a value in a YAML file using a colon-separated path.

    Args:
        project_name (str): Name of the project
        yml_type (str): Type of yml file to update (e.g., 'experiment', 'project')
        param (str): Colon-separated path to the parameter (e.g., 'parent:child1:child2')
        value: Value to set

    Example:
        update_yml('my_project', 'experiment', 'Experiment:chunk_size:value', 100)
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
    print(" Factual Q&A ".center(100, " "))
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


def main():
    clean_pycache()
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print_banner()
        print_options()
        df_exp = pd.read_parquet("local-db/experiments.parquet")
        df_proj = pd.read_parquet("local-db/projects.parquet")
        list_projects = df_proj["project_name"].to_list()

        choice = input("Enter your choice [1/2/3/q]: ").strip()
        if choice == "q":
            print("\nExiting CLI. Goodbye!")
            break

        if choice not in ["1", "2", "3"]:
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
                print("Project already exists use option 3 to make it active.")
                for _ in tqdm(range(50), bar_format="{bar}"):
                    time.sleep(0.1)
            else:
                print(f"🆕  Creating new project “{project_name}”")

            print("=" * 100)
            if not project_name:
                print("\nProject name cannot be empty. Try again.")
                input("Press Enter to continue...")
                continue
            global current_project
            current_project = project_name

            if "LAMINI_API_KEY" not in os.environ:
                print("\nLAMINI_API_KEY environment variable is missing.")
                while "LAMINI_API_KEY" not in os.environ:
                    api_key = input("Please enter your LAMINI_API_KEY: ").strip()
                    if api_key:
                        os.environ["LAMINI_API_KEY"] = api_key
                        os.system("cls" if os.name == "nt" else "clear")
                        print_banner()
                        break
                    else:
                        print("API key cannot be empty. Please try again.")

                main_topic = input(
                    "Enter the main topic for the project (this will be used for baseline roles and prompts):  "
                ).strip()
                project_description = input(
                    "Enter a description for the project (optional): "
                ).strip()
                subprocess.run(
                    [
                        "python",
                        "main_scripts/init_project.py",
                        "--project_name",
                        project_name,
                        "--topic",
                        main_topic,
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
                project_file["Project"]["project_name"]["value"] = project_name
                project_file["Lamini"]["api_key"]["value"] = os.environ[
                    "LAMINI_API_KEY"
                ]
                project_file["Project"]["topic"]["value"] = main_topic
                if not project_description == "":
                    project_file["Project"]["topic"][
                        "description"
                    ] = project_description

                with open(
                    os.path.join("projects", project_name, "ymls", "project.yml"), "w"
                ) as file:
                    yaml.dump(project_file, file)

                print(
                    f"\nProject '{project_name}' is set up in the 'projects' folder. Please feel free to adjust YML files as needed."
                )
                print(
                    f"\nNOTE: Please also move your pdf files into data folder associated with your project"
                )
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
                    f"\nProject “{project_name}” does not exist. Returning to the main menu."
                )
                for _ in tqdm(range(50), bar_format="{bar}"):
                    time.sleep(0.1)
                continue

            print(f"✅  Using existing project “{project_name}”")
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
                    f"\nProject “{project_name}” does not exist. Returning to the main menu."
                )
                for _ in tqdm(range(50), bar_format="{bar}"):
                    time.sleep(0.1)
                continue

            print(f"✅  Using existing project “{project_name}”")
            print("=" * 100)

            # Use a regular expression to remove trailing digits
            project_name_org = re.sub(r"\d{1,2}$", "", project_name)

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
            with open(
                os.path.join("projects", project_name_org, "ymls", "project.yml"), "r"
            ) as file:
                project_file = yaml.safe_load(file)
            # TODO: check this
            filtered_df_exp = df_exp[df_exp["project_id"] == project_name_org]
            list_experiments = filtered_df_exp["experiment_name"].to_list()

            if "LAMINI_API_KEY" not in os.environ:
                with open(
                    os.path.join("projects", project_name_org, "ymls", "project.yml"),
                    "r",
                ) as file:
                    project_file = yaml.safe_load(file)
                os.environ["LAMINI_API_KEY"] = project_file["Lamini"]["api_key"][
                    "value"
                ]

            while True:
                os.system("cls" if os.name == "nt" else "clear")
                print_banner()
                print("=" * 100)
                print("\nWhat would you like to do with the activated project?")
                print("  [d] Perform data generation")
                print("  [ge] Generate evaluation set from chunks")
                print("  [t] Tune the model")
                print("  [i] Run inference")
                print("  [m] Monitor project data")
                print("  [e] Evaluate model performance")
                print("  [r] Return to main menu")
                print("  [q] Quit")
                print("=" * 100)

                action_choice = (
                    input("Enter your choice [d/ge/t/i/m/r/q]: ").strip().lower()
                )
                if action_choice not in ["d", "ge", "t", "i", "m", "r", "q"]:
                    print("\nInvalid choice. Try again.")
                    input("Press Enter to continue...")
                    continue

                if action_choice == "d":

                    print("\nPerforming data generation...")
                    print("=" * 100)
                    print(
                        "\n Please make sure that PDFs are loaded into your project folder inside data folder!"
                    )
                    print("=" * 100)

                    while True:

                        experiment_completer = WordCompleter(
                            list_experiments, ignore_case=True, sentence=True
                        )

                        experiment_name = prompt(
                            "Enter experiment name: ", completer=experiment_completer
                        ).strip()

                        if experiment_name in list_experiments:
                            print(
                                f"❌  Experiment name “{experiment_name}” already exists. Please try another."
                            )
                        else:
                            print(f"🆕  Creating new experiment “{experiment_name}”")
                            break  # Exit the loop if a unique experiment name is entered

                    global current_experiment
                    current_experiment = experiment_name

                    batches = exp_file["Experiment"]["batches"]["value"]
                    mode = (
                        exp_file["Experiment"]["loading_mode"]["value"].strip().lower()
                    )
                    chunk_strategy = (
                        exp_file["Experiment"]["chunk_strategy"]["value"]
                        .strip()
                        .lower()
                    )
                    recursive_chunk = exp_file["Experiment"]["recursive_chunk"]["value"]
                    chunk_filtering = exp_file["Experiment"]["chunk_filtering"]["value"]
                    combine_chunk = exp_file["Experiment"]["combine_chunk"]["value"]
                    exp_file["Experiment"]["experiment_name"] = experiment_name
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

                    if mode not in ["multimodal", "text"]:
                        print("\nDigestion mode: Defaulting to 'text'.")
                        mode = "text"

                    if chunk_strategy not in ["sentence", "semantic"]:
                        print("\nChunk strategy: Defaulting to 'sentence'.")
                        chunk_strategy = "sentence"

                    pipeline_command = [
                        "python",
                        "main_scripts/pipeline.py",
                        "--project_name",
                        project_name_org,
                        "--experiment_name",
                        experiment_name,
                        "--batches",
                        str(batches),
                        "--mode",
                        mode,
                        "--chunk_strategy",
                        chunk_strategy,
                    ]
                    if recursive_chunk:
                        pipeline_command.append("--recursive_chunk")
                    if chunk_filtering:
                        pipeline_command.append("--chunk_filtering")
                    if combine_chunk:
                        pipeline_command.append("--combine_chunk")

                    subprocess.run(pipeline_command)

                elif action_choice == "ge":
                    print("\nGenerating evaluation set from existing chunks...\n")

                    # Ensure experiment exists
                    while True:
                        experiment_completer = WordCompleter(
                            list_experiments, ignore_case=True, sentence=True
                        )

                        experiment_name = prompt(
                            "Enter experiment name to build evaluation set from: ",
                            completer=experiment_completer,
                        ).strip()

                        if experiment_name not in list_experiments:
                            print(
                                f"❌  Experiment name “{experiment_name}” does not exist. Please choose an existing experiment."
                            )
                        else:
                            print(
                                f"✅  Using experiment “{experiment_name}” for evaluation set generation"
                            )
                            break

                    sample_frac_input = input(
                        "Enter fraction of chunks to sample [default 0.2]: "
                    ).strip()
                    try:
                        sample_frac = (
                            float(sample_frac_input) if sample_frac_input else 0.2
                        )
                    except ValueError:
                        print("Invalid fraction. Defaulting to 0.2")
                        sample_frac = 0.2

                    generate_eval_cmd = [
                        "python",
                        "main_scripts/generate_eval_set.py",
                        "--project_name",
                        project_name_org,
                        "--experiment_name",
                        experiment_name,
                        "--sample_frac",
                        str(sample_frac),
                    ]
                    # Propagate recursive_chunk setting to evaluation set generation
                    if exp_file["Experiment"]["recursive_chunk"]["value"]:
                        generate_eval_cmd.append("--recursive_chunk")

                    subprocess.run(generate_eval_cmd)
                elif action_choice == "t":
                    print("\nTuning the model...")

                    while True:
                        experiment_completer = WordCompleter(
                            list_experiments, ignore_case=True, sentence=True
                        )

                        experiment_name = prompt(
                            "Enter experiment name: ", completer=experiment_completer
                        ).strip()

                        if experiment_name not in list_experiments:
                            print(
                                f"❌  Experiment name “{experiment_name}” does not exist. Please choose an existing experiment."
                            )
                        else:
                            print(f"✅  Using existing experiment “{experiment_name}”")
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
                    print("\nRunning inference...")
                    eval_file_path = input(
                        "Enter the path to the evaluation JSONL data file: "
                    ).strip()
                    model_id = input("Enter the Model ID for the LLM: ").strip()
                    system_message = input(
                        "Enter the system message for the prompt (or press Enter to use default): "
                    ).strip()

                    inference_command = [
                        "python",
                        "main_scripts/run_inference.py",
                        "--eval_file_path",
                        eval_file_path,
                        "--model_id",
                        model_id,
                    ]

                    if system_message:
                        inference_command.extend(["--system_message", system_message])

                    subprocess.run(inference_command)
                elif action_choice == "m":
                    print("\nMonitoring project data...")
                    while True:
                        print("\nSelect data to monitor:")
                        print("  [1] Chunks")
                        print("  [2] Datasets")
                        print("  [3] Experiments")
                        print("  [4] Prompts")
                        print("  [5] Results")
                        print("  [b] Back to project menu")

                        monitor_choice = (
                            input("\nEnter your choice [1/2/3/4/5/b]: ").strip().lower()
                        )

                        if monitor_choice == "b":
                            break

                        try:
                            if monitor_choice == "1":
                                # Display chunks data
                                chunks_df = pd.read_parquet("local-db/chunks.parquet")
                                display_dataframe_as_table(chunks_df, "Chunks Data")
                            elif monitor_choice == "2":
                                # Display datasets data
                                datasets_df = pd.read_parquet(
                                    "local-db/datasets.parquet"
                                )
                                display_dataframe_as_table(datasets_df, "Datasets")
                            elif monitor_choice == "3":
                                # Display experiments data
                                experiments_df = pd.read_parquet(
                                    "local-db/experiments.parquet"
                                )
                                display_dataframe_as_table(
                                    experiments_df, "Experiments"
                                )
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
                    print("\nEvaluating model performance...")
                    eval_file_path = input(
                        "Enter the path to the evaluation CSV data file: "
                    ).strip()
                    model_id = input("Enter the Model ID for the evaluation: ").strip()

                    eval_command = [
                        "python",
                        "main_scripts/evaluate.py",
                        "--eval_file_path",
                        eval_file_path,
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
