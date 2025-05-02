import os
import yaml
from pathlib import Path
import sqlite3
import pandas as pd  # for loading glossary parquet
# --- Lamini experiment primitives ------------------------------------------
from lamini.experiment.pipeline.base_agentic_pipeline import BaseAgenticPipeline
from lamini.experiment import BaseMemoryExperiment

# Generators & validator you already use in the standalone script
from lamini.experiment.generators import (
    PatternQuestionGenerator,      # "question" generator
    SchemaToSQLGenerator,          # SQL generator
    SQLDebuggerGenerator,          # (optional) automatic fix-ups
)
from lamini.experiment.validators import SQLValidator


def build_experiment_pipeline(ExperimentDefinition: dict):
    """
    Build an agentic pipeline that:
        1) turns natural-language questions into pattern-based rewrites,
        2) converts questions → SQL,
        3) validates the SQL against the DB schema,
        4) debugs / patches invalid SQL (optional),
        5) stores everything in a BaseMemoryExperiment object.

    Only the components from your first script are instantiated –
    no generic Q&A or fact validator objects.
    """

    # --------------------------------------------------------------------- #
    #  Load project configuration                                           #
    # --------------------------------------------------------------------- #
    project_dir = Path("projects") / ExperimentDefinition["project_name"]
    proj_path   = project_dir / "ymls" / "project.yml"
  
    with proj_path.open() as f:
        project_file = yaml.safe_load(f)

    # Locate the first available .sqlite file in the "data" folder of the project
    data_dir = project_dir / "data"
    sqlite_files = list(data_dir.glob("*.sqlite"))

    if not sqlite_files:
        raise FileNotFoundError("No .sqlite files found in the 'data' folder of the project.")

    db_path = sqlite_files[0]  # Use the first .sqlite file found
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)
    # Query to fetch the schema from the SQLite database
    cursor = connection.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    # Generate the schema from the SQL create statements
    db_schema = "\n".join(row[0] for row in cursor.fetchall())
    # Close the database connection
    connection.close()
    
    # You can keep per-step model overrides in project.yml if you like;
    # here we just default to the project-level "model".
    default_model = project_file["Project"]["model"]
    
    # --------------------------------------------------------------------- #
    #  Create generators & validator                                        #
    # --------------------------------------------------------------------- #
    question_generator = PatternQuestionGenerator(
        model=default_model,
        name="question_generator",        # pipeline handle
    )

    sql_generator = SchemaToSQLGenerator(
        model=default_model,
        name="sql_generator",
        db_type="sqlite",
        db_params=db_path,
        schema=db_schema,
    )

    sql_validator = SQLValidator(
        model=default_model,
        name="sql_validator",
        db_type="sqlite",
        db_params=db_path,
        sql_key="sql_query",
        is_valid_field="is_valid",
        instruction="""
        Query to validate: {sql_query}
        Schema: {schema}
        Glossary: {glossary}

        Validate this SQL query against the provided schema.
        """,
    )
    
    # If you want the automatic fixer, keep this; otherwise delete it
    sql_debugger = SQLDebuggerGenerator(
        model=default_model,
        db_type="sqlite",
        db_params=db_path,
        schema=db_schema,
    )


    # --------------------------------------------------------------------- #
    #  Build the agentic pipeline                                           #
    # --------------------------------------------------------------------- #
    path_record = project_dir / "experiment_results" / ExperimentDefinition["experiment_name"]
    pipeline = BaseAgenticPipeline(
        generators={
            "question_generator": question_generator,
            "sql_generator":      sql_generator,
            "sql_debugger":       sql_debugger, 
        },
        validators={
            "sql_validator": sql_validator,
        },
        
        order=[
            "question_generator",
            "sql_generator",
            "sql_validator",
            "sql_debugger",      
        ],
        record_dir = str(path_record)
    )

    path_record.mkdir(parents=True, exist_ok=True)
    # --------------------------------------------------------------------- #
    #  Wrap into an experiment                                              #
    # --------------------------------------------------------------------- #
    experiment = BaseMemoryExperiment(agentic_pipeline=pipeline)

    return {
        "question_generator": question_generator,
        "sql_generator":      sql_generator,
        "sql_validator":      sql_validator,
        "sql_debugger":       sql_debugger,
        "pipeline":           pipeline,
        "experiment":         experiment,
        "schema":             db_schema,
    }