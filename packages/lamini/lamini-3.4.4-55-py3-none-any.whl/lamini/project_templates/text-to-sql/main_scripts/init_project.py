#!/usr/bin/env python3
import os
import shutil
import argparse
import duckdb
import pandas as pd
import uuid
import yaml
from pathlib import Path
from datetime import datetime
import sys
import time

# Determine the current directory and append its parent path to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
import re  # for suffix matching
from models.project.projectdb import (
    ProjectDB,
)  # initialize all tables including datasets

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
db = ProjectDB()


def create_project_directory(project_name):
    """
    Create a project directory in the projects folder.

    Parameters
    ----------
    project_name : str
        Name of the project to create

    Returns
    -------
    Path
        Path to the created project directory
    """
    # Get the base directory (Pipeline_qa)
    base_dir = Path(__file__).parent.parent

    # Create projects directory if it doesn't exist
    projects_dir = base_dir / "projects"
    projects_dir.mkdir(exist_ok=True)

    # Create project directory
    project_dir = projects_dir / project_name
    project_dir.mkdir(exist_ok=True)

    # Create yml directory inside project directory
    yml_dir = project_dir / "ymls"
    yml_dir.mkdir(exist_ok=True)

    # Create data directory inside project directory
    data_dir = project_dir / "data"
    data_dir.mkdir(exist_ok=True)

    print(f"Created project directory: {project_dir}")
    print(f"Created data directory: {data_dir}")

    return project_dir


def copy_yml_templates(project_dir, project_name):
    """
    Copy yml templates from yml-templates directory to project yml directory.
    If API key is provided in environment, update the template with it.

    Parameters
    ----------
    project_dir : Path
        Path to the project directory

    Returns
    -------
    dict
        Dictionary containing the paths to the copied yml files
    """
    # Get the base directory (Pipeline_qa)
    base_dir = Path(__file__).parent.parent

    # Source directory for yml templates
    templates_dir = base_dir / "yml-templates"

    # Destination directory for yml files
    yml_dir = project_dir / "ymls"

    # Dictionary to store the paths to the copied yml files
    yml_files = {}

    try:
        # Copy all yml files from templates to project yml directory
        for yml_file in templates_dir.glob("*.yml"):
            dest_file = yml_dir / yml_file.name
            shutil.copy2(yml_file, dest_file)

            # If this is project.yml and we have an API key, update it
            if yml_file.name == "project.yml" and "LAMINI_API_KEY" in os.environ:
                with open(dest_file, "r") as f:
                    yml_content = yaml.safe_load(f)

                # Update the API key in the template
                yml_content["Lamini"]["api_key"] = os.environ["LAMINI_API_KEY"]

                # Write back to the template file
                with open(yml_file, "w") as f:
                    yaml.dump(yml_content, f, default_flow_style=False)

                # Also update the project's copy
                with open(dest_file, "w") as f:
                    yaml.dump(yml_content, f, default_flow_style=False)

            yml_files[yml_file.name] = dest_file
            print(f"Copied {yml_file.name} to {yml_dir}")
    except Exception as e:
        print(f"Error copying yml templates: {e}")
        return {}

    return yml_files


def read_yml_file(file_path):
    """
    Read a yml file and return its contents as a string.

    Parameters
    ----------
    file_path : Path
        Path to the yml file

    Returns
    -------
    str
        Contents of the yml file as a string
    """
    if file_path != "":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading yml file {file_path}: {e}")
            return ""


def check_and_create_projects_table():
    """
    Check if projects.parquet table exists in local-db.
    If not, create it with the required schema.

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    # Get the base directory (Pipeline_qa)
    base_dir = Path(__file__).parent.parent

    # Path to the local-db directory
    db_dir = base_dir / "local-db"
    db_dir.mkdir(exist_ok=True)

    # Path to the projects.parquet file
    projects_file = db_dir / "projects.parquet"

    # Check if projects.parquet exists
    if not projects_file.exists():
        print("Projects table does not exist. Creating a new one...")

        # Create a schema for the projects table with the required fields
        projects_df = pd.DataFrame(
            {
                "project_id": [],
                "project_name": [],
                "version": [],
                "project_yml": [],
                "experiment_yml": [],
                "prompts_yml": [],
                "created_at": [],
                "updated_at": [],
            }
        )

        # Initialize DuckDB connection
        conn = duckdb.connect()

        # Register the DataFrame with DuckDB and write to parquet
        conn.register("projects_df", projects_df)
        conn.execute(f"COPY projects_df TO '{projects_file}' (FORMAT PARQUET)")

        print(f"Created projects table at {projects_file}")
        return True
    else:
        print(f"Projects table already exists at {projects_file}")
        return True


def add_project_to_db(project_name, yml_files):
    """
    Add a new project to the projects table.

    Parameters
    ----------
    project_name : str
        Name of the project
    yml_files : dict
        Dictionary containing the paths to the yml files

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    # Get the base directory (Pipeline_qa)
    base_dir = Path(__file__).parent.parent

    # Path to the projects.parquet file
    projects_file = base_dir / "local-db" / "projects.parquet"

    # Generate a unique project ID
    project_id = str(uuid.uuid4())

    # Get the current timestamp
    now = datetime.now().isoformat()

    # Read the yml files
    exp_yml = read_yml_file(yml_files.get("experiment.yml", ""))
    proj_yml = read_yml_file(yml_files.get("project.yml", ""))
    prompts_yml = read_yml_file(yml_files.get("prompts.yml", ""))

    # Create a new project record
    new_project = pd.DataFrame(
        {
            "project_id": [project_id],
            "project_name": [project_name],
            "version": [0],  # Initial version set to 0
            "proj_yml": [proj_yml],
            "exp_yml": [exp_yml],
            "prompts_yml": [prompts_yml],
            "created_at": [now],
            "updated_at": [now],
        }
    )

    # Initialize DuckDB connection
    conn = duckdb.connect()

    # Read existing projects
    if projects_file.exists():
        existing_projects = conn.execute(
            f"SELECT * FROM read_parquet('{projects_file}')"
        ).df()

        # Combine with new project
        combined_projects = pd.concat(
            [existing_projects, new_project], ignore_index=True
        )
    else:
        combined_projects = new_project

    # Register the combined DataFrame with DuckDB and write back to parquet
    conn.register("combined_projects", combined_projects)
    conn.execute(f"COPY combined_projects TO '{projects_file}' (FORMAT PARQUET)")

    print(f"Added project '{project_name}' to the projects table with version 0")
    return True


def update_project(project_name):
    """
    Update a project in the projects table if any YML files have changed.

    Parameters
    ----------
    project_name : str
        Name of the project to update

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    # Get the base directory (Pipeline_qa)
    base_dir = Path(__file__).parent.parent

    # Path to the projects.parquet file
    projects_file = base_dir / "local-db" / "projects.parquet"

    # Initialize DuckDB connection
    conn = duckdb.connect()

    # Read projects table
    projects_df = conn.execute(f"SELECT * FROM read_parquet('{projects_file}')").df()

    # Strip all trailing version-like suffix segments (e.g., '_1.0.0', '_2.0', etc.)
    suffix_pattern = r"(?:_\d+(?:\.\d+)*)+$"
    base_name = re.sub(suffix_pattern, "", project_name)

    # Select all rows for this project (base or any versioned suffix)
    pattern = rf"^{re.escape(base_name)}(?:_\d+(?:\.\d+)*)*$"
    project_df = projects_df[projects_df["project_name"].str.match(pattern)]

    # Check if project exists in the table
    if project_df.empty:
        print(f"Project '{project_name}' does not exist in the projects table.")
        return False

    # Get the latest version number from the version column (default to 0 if none)
    latest_version = project_df["version"].max() if not project_df.empty else -1

    # Prepare new project_name by appending a single '_X.0.0' suffix
    new_version = latest_version + 1
    new_name = f"{base_name}_{new_version}.0.0"
    # Generate a unique project ID
    project_id = str(uuid.uuid4())

    # Get the current timestamp
    now = datetime.now().isoformat()

    # Read the current YML files
    yml_dir = base_dir / "projects" / base_name
    experiment_yml_path = yml_dir / "experiment.yml"
    project_yml_path = yml_dir / "project.yml"

    current_experiment_yml = read_yml_file(experiment_yml_path)
    current_project_yml = read_yml_file(project_yml_path)

    # Fetch the previous record based on the latest version (handles version 0 which has no numeric suffix)
    prev_record = project_df[project_df["version"] == latest_version].iloc[0]

    prev_exp_yml = prev_record["exp_yml"]
    prev_proj_yml = prev_record["proj_yml"]

    exp_changed = current_experiment_yml != prev_exp_yml
    proj_changed = current_project_yml != prev_proj_yml

    # Print which YML files have changed
    if exp_changed:
        print("experiment.yml has changed.")
    if proj_changed:
        print("project.yml has changed.")

    # Create a new project record with updated name and version
    new_project = pd.DataFrame(
        {
            "project_id": [project_id],
            "project_name": [new_name],
            "version": [new_version],  # Increment version
            "proj_yml": [current_project_yml],
            "exp_yml": [current_experiment_yml],
            "created_at": [now],
            "updated_at": [now],
        }
    )

    # Combine with existing projects
    combined_projects = pd.concat([projects_df, new_project], ignore_index=True)

    # Register the combined DataFrame with DuckDB and write back to parquet
    conn.register("combined_projects", combined_projects)
    conn.execute(f"COPY combined_projects TO '{projects_file}' (FORMAT PARQUET)")

    print(f"Updated project '{new_name}' (base '{base_name}') to version {new_version}")
    return True


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Initialize or update a project")
    parser.add_argument(
        "--project_name", help="Name of the project to create or update"
    )
    parser.add_argument(
        "--update", action="store_true", help="Update an existing project"
    )
    args = parser.parse_args()

    if args.update:
        # Update an existing project
        if not update_project(args.project_name):
            print(f"Failed to update project '{args.project_name}'. Exiting.")
            return
        print(f"Project '{args.project_name}' updated successfully!")
    else:

        # Create a new project
        project_dir = create_project_directory(args.project_name)

        # Copy yml templates
        yml_files = copy_yml_templates(project_dir, args.project_name)
        if not yml_files:
            print("Failed to copy yml templates. Exiting.")
            return

        # Check and create projects table
        if not check_and_create_projects_table():
            print("Failed to check/create projects table. Exiting.")
            return

        # Add project to the projects table
        if not add_project_to_db(args.project_name, yml_files):
            print("Failed to add project to the projects table. Exiting.")
            return

        print(f"Project '{args.project_name}' initialized successfully!")
        print(f"Please feel free to adjust YML files as needed.")

        print("-" * 100)
        


if __name__ == "__main__":
    main()
