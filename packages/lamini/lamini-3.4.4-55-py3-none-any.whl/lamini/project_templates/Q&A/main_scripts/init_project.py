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
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
from experiment_prep import update_all_project_ymls

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
    
    # Create eval_data directory inside project directory
    eval_data_dir = project_dir / "eval_data"
    eval_data_dir.mkdir(exist_ok=True)
    
    print(f"Created project directory: {project_dir}")
    print(f"Created data directory: {data_dir}")
    print(f"Created eval_data directory: {eval_data_dir}")
    return project_dir

def copy_yml_templates(project_dir,project_name,main_topic):
    """
    Copy yml templates from yml-templates directory to project yml directory.
    
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
            yml_files[yml_file.name] = dest_file
            print(f"Copied {yml_file.name} to {yml_dir}")
    except Exception as e:
        print(f"Error copying yml templates: {e}")
        return {}

    update_all_project_ymls(project_name,main_topic)
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
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
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
        projects_df = pd.DataFrame({
            'project_id': [],
            'project_name': [],
            'version': [],
            'project_yml': [],
            'experiment_yml': [],
            'prompts_yml': [],
            'roles_yml': [],
            'created_at': [],
            'updated_at': []
        })
        
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
    exp_yml = read_yml_file(yml_files.get('experiment.yml', ''))
    proj_yml = read_yml_file(yml_files.get('project.yml', ''))
    prompts_yml = read_yml_file(yml_files.get('prompts.yml', ''))
    roles_yml = read_yml_file(yml_files.get('roles.yml', ''))
    
    # Create a new project record
    new_project = pd.DataFrame({
        'project_id': [project_id],
        'project_name': [project_name],
        'version': [0],  # Initial version set to 0
        'proj_yml': [proj_yml],
        'exp_yml': [exp_yml],
        'prompts_yml': [prompts_yml],
        'roles_yml': [roles_yml],
        'created_at': [now],
        'updated_at': [now]
    })
    
    # Initialize DuckDB connection
    conn = duckdb.connect()
    
    # Read existing projects
    if projects_file.exists():
        existing_projects = conn.execute(
            f"SELECT * FROM read_parquet('{projects_file}')"
        ).df()
        
        # Combine with new project
        combined_projects = pd.concat([existing_projects, new_project], ignore_index=True)
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
    
    # Path to the project directory
    project_dir = base_dir / "projects" / project_name
    
    # Check if project directory exists
    if not project_dir.exists():
        print(f"Project directory '{project_name}' does not exist.")
        return False
    
    # Check if projects table exists
    if not projects_file.exists():
        print("Projects table does not exist. Cannot update project.")
        return False
    
    # Initialize DuckDB connection
    conn = duckdb.connect()
    
    # Read projects table
    projects_df = conn.execute(
        f"SELECT * FROM read_parquet('{projects_file}')"
    ).df()
    
    # Auto-increment project name if it already exists
    existing_names = projects_df['project_name'].tolist()
    original_name = project_name
    counter = 1
    while project_name in existing_names:
        project_name = f"{original_name}{counter}"
        counter += 1
    
    # Filter for the specified project
    project_df = projects_df[projects_df['project_name'] == original_name]
    
    # Check if project exists in the table
    if project_df.empty:
        print(f"Project '{original_name}' does not exist in the projects table.")
        return False
    
    # Get the latest version of the project
    latest_version = project_df['version'].max()
    latest_project = project_df[project_df['version'] == latest_version].iloc[0]
    
    # Read the current YML files
    yml_dir = project_dir / "ymls"
    experiment_yml_path = yml_dir / "experiment.yml"
    project_yml_path = yml_dir / "project.yml"
    prompts_yml_path = yml_dir / "prompts.yml"
    roles_yml_path = yml_dir / "roles.yml"
    
    current_experiment_yml = read_yml_file(experiment_yml_path)
    current_project_yml = read_yml_file(project_yml_path)
    current_prompts_yml = read_yml_file(prompts_yml_path)
    current_roles_yml = read_yml_file(roles_yml_path)
    

    # Compare with the stored versions
    exp_changed = current_experiment_yml != latest_project['exp_yml']
    proj_changed = current_project_yml != latest_project['proj_yml']
    prompts_changed = current_prompts_yml != latest_project['prompts_yml']
    roles_changed = current_roles_yml != latest_project['roles_yml']
    
    # Check if any YML files have changed
    if not (exp_changed or prompts_changed or roles_changed, proj_changed):
        print("There are no updates to save.")
        return True
    
    # Print which YML files have changed
    if exp_changed:
        print("experiment.yml has changed.")
    if proj_changed:
        print("project.yml has changed.")
    if prompts_changed:
        print("prompts.yml has changed.")
    if roles_changed:
        print("roles.yml has changed.")
    
    # Generate a unique project ID
    project_id = str(uuid.uuid4())
    
    # Get the current timestamp
    now = datetime.now().isoformat()
    
    # Create a new project record with incremented version
    new_project = pd.DataFrame({
        'project_id': [project_id],
        'project_name': [project_name],
        'version': [latest_version + 1],  # Increment version
        'proj_yml': [current_project_yml],
        'exp_yml': [current_experiment_yml],
        'prompts_yml': [current_prompts_yml],
        'roles_yml': [current_roles_yml],
        'created_at': [now],
        'updated_at': [now]
    })
    
    # Combine with existing projects
    combined_projects = pd.concat([projects_df, new_project], ignore_index=True)
    
    # Register the combined DataFrame with DuckDB and write back to parquet
    conn.register("combined_projects", combined_projects)
    conn.execute(f"COPY combined_projects TO '{projects_file}' (FORMAT PARQUET)")
    
    print(f"Updated project '{project_name}' to version {latest_version + 1}")
    return True

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Initialize or update a project')
    parser.add_argument('--project_name', help='Name of the project to create or update')
    parser.add_argument('--topic', help='main topic of the project')
    parser.add_argument('--update', action='store_true', help='Update an existing project')
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
        yml_files = copy_yml_templates(project_dir,args.project_name, args.topic)
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
        
        print('-'*100)
        # Print next steps
        print("\nNext Steps before running the pipeline:")
        print("1. add your lamini api key as an environment variable. for example: export LAMINI_API_KEY=<api_key>")
        print("2. Copy your data files into the data directory for the project")
        print("3. update experiment.yml for your first experiment. HINT: This repo considers each run of the pipeline as an \"experiment\"")
        print("4. update roles.yml")
        print("5. (optional) update prompts.yml. The default prompts will work well for your initial run. but definitely update them to shape the pipeline output to more closely resemble your eval data and how your users expect the data.")
        print("6. run \"python init_project.py <project_name> --update\" to save your project setup changes.")

if __name__ == "__main__":
    main()
