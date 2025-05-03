import duckdb
from pathlib import Path
import pandas as pd
from datetime import datetime
import hashlib
import json
import os


class ProjectDB:
    def __init__(self, base_dir="./local-db"):
        """
        Initialize ProjectDB handler

        Parameters
        ----------
        base_dir : str
            Base directory for the database files
        """
        base_dir = os.path.join(Path(__file__).parent.parent.parent, base_dir)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.conn = duckdb.connect()
        self._init_experiments_table()
        self._init_prompts_table()
        self._init_datasets_table()
        self._init_projects_table()

    def _init_experiments_table(self):
        """Initialize the experiments tracking table if it doesn't exist"""
        experiments_path = self.base_dir / "experiments.parquet"

        if not experiments_path.exists():
            # Create empty experiments table with schema
            df = pd.DataFrame(
                {
                    "experiment_id": [],
                    "experiment_name": [],
                    "created_at": [],
                    "description": [],
                    "project_id": [],
                    "parameters": [],
                    "model_config": [],
                    "status": [],
                    "total_chunks": [],
                    "total_results": [],
                    "valid_results": [],
                    "validity_rate": [],
                    "last_updated": [],
                    "question_generator_ids": [],  # List of question generator prompt IDs
                    "answer_generator_ids": [],  # List of answer generator prompt IDs
                    "validator_ids": [],  # List of validator prompt IDs
                    "chunk_ids": [],  # List of chunk IDs associated with this experiment
                    "tuning_job_id": [],  # Optional tuning job ID
                    "dataset_id": [],  # Reference to dataset table
                    "eval_dataset_id": [],  # Reference to evaluation dataset table
                }
            )
            df.to_parquet(experiments_path, index=False)

    def _init_prompts_table(self):
        """Initialize the prompts table if it doesn't exist"""
        prompts_path = self.base_dir / "prompts.parquet"

        if not prompts_path.exists():
            # Create empty prompts table with schema
            df = pd.DataFrame(
                {
                    "prompt_id": [],
                    "created_at": [],
                    "name": [],
                    "type": [],  # 'generator' or 'validator'
                    "prompt_text": [],
                    "last_updated": [],
                }
            )
            df.to_parquet(prompts_path, index=False)

    def _init_datasets_table(self):
        """Initialize the datasets table if it doesn't exist"""
        datasets_path = self.base_dir / "datasets.parquet"

        if not datasets_path.exists():
            df = pd.DataFrame(
                {
                    "dataset_id": [],
                    "created_at": [],
                    "name": [],
                    "description": [],
                    "qa_pairs": [],
                    "last_updated": [],
                    "qa_hash": [],
                }
            )
            df.to_parquet(datasets_path, index=False)

    def _init_projects_table(self):
        """Initialize the projects table if it doesn't exist"""
        projects_path = self.base_dir / "projects.parquet"

        if not projects_path.exists():
            # Create empty projects table with schema
            df = pd.DataFrame(
                {
                    "project_id": [],
                    "project_name": [],
                    "version": [],
                    "project_yml": [],
                    "experiment_yml": [],
                    "prompts_yml": [],
                    "roles_yml": [],
                    "created_at": [],
                    "updated_at": [],
                }
            )
            df.to_parquet(projects_path, index=False)

    def create_prompt(self, name: str, type: str, prompt_text: str):
        """
        Create a new prompt and return its ID, unless a prompt with the same prompt_text already exists.

        Parameters
        ----------
        name : str
            Name of the prompt
        type : str
            Type of prompt ('generator' or 'validator')
        prompt_text : str
            The actual prompt text

        Returns
        -------
        str
            The ID of the created prompt, or the existing prompt's ID if a duplicate is found.
        """
        prompts_path = self.base_dir / "prompts.parquet"

        # Load existing prompts
        existing = pd.read_parquet(prompts_path)

        # Check if prompt_text already exists in the database
        existing_prompt = existing[existing["prompt_text"] == prompt_text]
        if not existing_prompt.empty:
            # Return the prompt_id of the first matching record if already exists
            return existing_prompt.iloc[0]["prompt_id"]

        # Generate a unique prompt ID
        prompt_id = f"prompt_{len(existing) + 1}"

        # Create a new prompt record
        new_prompt = pd.DataFrame(
            [
                {
                    "prompt_id": prompt_id,
                    "created_at": datetime.now().isoformat(),
                    "name": name,
                    "type": type,
                    "prompt_text": prompt_text,
                    "last_updated": datetime.now().isoformat(),
                }
            ]
        )

        # Append to existing prompts and save back to parquet
        updated_prompts = pd.concat([existing, new_prompt], ignore_index=True)
        updated_prompts.to_parquet(prompts_path, index=False)

        return prompt_id

    def create_dataset(self, name: str, description: str, qa_pairs: pd.DataFrame):
        """
        Create a new dataset with question-answer pairs (avoiding duplicates)
        """
        datasets_path = self.base_dir / "datasets.parquet"

        # Load existing datasets
        if datasets_path.exists():
            existing = pd.read_parquet(datasets_path)
        else:
            existing = pd.DataFrame(
                columns=[
                    "dataset_id",
                    "created_at",
                    "name",
                    "description",
                    "qa_pairs",
                    "last_updated",
                    "qa_hash",
                ]
            )

        # Ensure that all elements are JSON serializable by converting complex structures to strings
        qa_pairs_normalized = qa_pairs.applymap(
            lambda x: (
                json.dumps(x, sort_keys=True) if isinstance(x, (dict, list)) else x
            )
        )

        # Serialize and sort QA pairs to ensure consistent hashing
        qa_json_str = qa_pairs_normalized.sort_values(
            by=qa_pairs.columns.tolist()
        ).to_json(orient="records")

        # Compute hash of the serialized QA pairs
        qa_hash = hashlib.sha256(qa_json_str.encode("utf-8")).hexdigest()

        # Check for duplicates
        if "qa_hash" in existing.columns and qa_hash in existing["qa_hash"].values:
            dataset_id = existing.loc[
                existing["qa_hash"] == qa_hash, "dataset_id"
            ].iloc[0]
            return dataset_id

        # Generate unique dataset ID
        dataset_id = f"dataset_{len(existing) + 1}"

        # Create new dataset record
        new_dataset = pd.DataFrame(
            [
                {
                    "dataset_id": dataset_id,
                    "created_at": datetime.now().isoformat(),
                    "name": name,
                    "description": description,
                    "qa_pairs": qa_json_str,
                    "last_updated": datetime.now().isoformat(),
                    "qa_hash": qa_hash,
                }
            ]
        )

        # Append and save
        updated_datasets = pd.concat([existing, new_dataset], ignore_index=True)
        updated_datasets.to_parquet(datasets_path, index=False)

        return dataset_id

    def delete_dataset(self, dataset_id: str):
        """
        Delete a dataset and its associated data

        Parameters
        ----------
        dataset_id : str
            ID of the dataset to delete
        """
        datasets_path = self.base_dir / "datasets.parquet"
        experiments_path = self.base_dir / "experiments.parquet"

        # Load existing data
        datasets_df = pd.read_parquet(datasets_path)
        experiments_df = pd.read_parquet(experiments_path)

        # Check if dataset exists
        if dataset_id not in datasets_df["dataset_id"].values:
            raise ValueError(f"Dataset ID '{dataset_id}' does not exist")

        # Check if dataset is referenced by any experiments
        if dataset_id in experiments_df["dataset_id"].values:
            raise ValueError(
                f"Cannot delete dataset '{dataset_id}' as it is referenced by experiments"
            )

        # Remove dataset
        datasets_df = datasets_df[datasets_df["dataset_id"] != dataset_id]
        datasets_df.to_parquet(datasets_path, index=False)

    def delete_experiment(self, experiment_id: str):
        """
        Delete an experiment and its associated data

        Parameters
        ----------
        experiment_id : str
            ID of the experiment to delete
        """
        experiments_path = self.base_dir / "experiments.parquet"
        results_path = self.base_dir / "results.parquet"
        chunks_path = self.base_dir / "chunks.parquet"

        # Load existing data
        experiments_df = pd.read_parquet(experiments_path)

        # Check if experiment exists
        if experiment_id not in experiments_df["experiment_id"].values:
            raise ValueError(f"Experiment ID '{experiment_id}' does not exist")

        # Get experiment name for filtering results and chunks
        experiment_name = experiments_df[
            experiments_df["experiment_id"] == experiment_id
        ]["experiment_name"].iloc[0]

        # Remove experiment from experiments table
        experiments_df = experiments_df[
            experiments_df["experiment_id"] != experiment_id
        ]
        experiments_df.to_parquet(experiments_path, index=False)

        # Remove associated results if they exist
        if results_path.exists():
            results_df = pd.read_parquet(results_path)
            results_df = results_df[results_df["experiment_name"] != experiment_name]
            results_df.to_parquet(results_path, index=False)

        # Remove associated chunks if they exist
        if chunks_path.exists():
            chunks_df = pd.read_parquet(chunks_path)
            chunks_df = chunks_df[chunks_df["experiment_name"] != experiment_name]
            chunks_df.to_parquet(chunks_path, index=False)

    def register_experiment(
        self,
        project_id: str,
        experiment_id: str,
        experiment_name: str,
        description: str,
        parameters: dict,
        model_config: dict,
        generators: list = None,
        validators: list = None,
        chunk_ids: list = None,
        tuning_job_id: str = None,
        dataset_id: str = None,
    ):
        """
        Register a new experiment in the database

        Parameters
        ----------
        experiment_id : str
            Unique ID for the experiment
        experiment_name : str
            Name for the experiment
        description : str
            Description of the experiment
        parameters : dict
            Experiment parameters (chunk_size, step_size, etc.)
        model_config : dict
            Model configurations used in the experiment
        generators : list, optional
            List of generator names and their prompts
        validators : list, optional
            List of validator names and their prompts
        chunk_ids : list, optional
            List of chunk IDs associated with this experiment
        tuning_job_id : str, optional
            Optional tuning job ID
        dataset_id : str, optional
            Reference to dataset table
        """
        experiments_path = self.base_dir / "experiments.parquet"

        # Load existing experiments from parquet
        existing = pd.read_parquet(experiments_path)

        # Check if experiment_id already exists
        if experiment_id in existing["experiment_id"].values:
            raise ValueError(f"Experiment ID '{experiment_id}' already exists")

        # Create prompt IDs for generators and validators
        question_generator_ids = []
        answer_generator_ids = []
        validator_ids = []

        if generators:
            for gen in generators:
                prompt_id = self.create_prompt(
                    name=gen["name"], type="generator", prompt_text=gen["prompt"]
                )
                # Separate question and answer generators
                if "question" in gen["name"].lower():
                    question_generator_ids.append(prompt_id)
                elif "answer" in gen["name"].lower():
                    answer_generator_ids.append(prompt_id)

        if validators:
            for val in validators:
                prompt_id = self.create_prompt(
                    name=val["name"], type="validator", prompt_text=val["prompt"]
                )
                validator_ids.append(prompt_id)

        # Create new experiment record
        new_experiment = pd.DataFrame(
            [
                {
                    "experiment_id": experiment_id,
                    "experiment_name": experiment_name,
                    "created_at": datetime.now().isoformat(),
                    "description": description,
                    "project_id": project_id,
                    "parameters": parameters,
                    "model_config": model_config,
                    "status": "running",
                    "total_chunks": 0,
                    "total_results": 0,
                    "valid_results": 0,
                    "validity_rate": 0.0,
                    "last_updated": datetime.now().isoformat(),
                    "question_generator_ids": question_generator_ids or [],
                    "answer_generator_ids": answer_generator_ids or [],
                    "validator_ids": validator_ids or [],
                    "chunk_ids": chunk_ids or [],
                    "tuning_job_id": tuning_job_id,
                    "dataset_id": dataset_id,
                    "eval_dataset_id": None,
                }
            ]
        )

        # Append to existing experiments and save back to parquet
        updated_experiments = pd.concat([existing, new_experiment], ignore_index=True)
        updated_experiments.to_parquet(experiments_path, index=False)

    def update_experiment_stats(self, experiment_name: str):
        """
        Update experiment statistics based on results

        Parameters
        ----------
        experiment_name : str
            Name of the experiment to update
        """
        results_path = self.base_dir / "results.parquet"
        experiments_path = self.base_dir / "experiments.parquet"

        # If no results file exists, update with zeros
        if not results_path.exists():
            update_query = f"""
                UPDATE experiments 
                SET total_results = 0,
                    valid_results = 0,
                    validity_rate = 0.0,
                    last_updated = '{datetime.now().isoformat()}'
                WHERE experiment_name = '{experiment_name}'
            """
            self.conn.execute(update_query)
            self.conn.execute(
                f"COPY experiments TO '{experiments_path}' (FORMAT PARQUET)"
            )
            return

        # Create temporary views of our tables
        self.conn.execute(
            f"CREATE OR REPLACE TABLE results AS SELECT * FROM read_parquet('{results_path}')"
        )
        self.conn.execute(
            f"CREATE OR REPLACE TABLE experiments AS SELECT * FROM read_parquet('{experiments_path}')"
        )

        # Calculate current stats using SQL with COALESCE to handle NULL values
        stats_query = f"""
            SELECT 
                COALESCE(COUNT(*), 0) as total_results,
                COALESCE(SUM(CASE WHEN CAST(FactValidator_output->>'is_valid' AS BOOLEAN) THEN 1 ELSE 0 END), 0) as valid_results,
                COALESCE(ROUND(AVG(CASE WHEN CAST(FactValidator_output->>'is_valid' AS BOOLEAN) THEN 1.0 ELSE 0.0 END) * 100, 2), 0.0) as validity_rate
            FROM results
            WHERE experiment_name = '{experiment_name}'
        """

        stats = self.conn.execute(stats_query).fetchone()
        total_results, valid_results, validity_rate = stats

        # Update experiments table with new stats
        update_query = f"""
            UPDATE experiments 
            SET total_results = {total_results},
                valid_results = {valid_results},
                validity_rate = {validity_rate},
                last_updated = '{datetime.now().isoformat()}'
            WHERE experiment_name = '{experiment_name}'
        """

        self.conn.execute(update_query)

        # Save back to parquet
        self.conn.execute(f"COPY experiments TO '{experiments_path}' (FORMAT PARQUET)")

    def update_experiment_tuning_id(self, experiment_name: str, tuning_job_id: str):
        """
        Update the tuning_job_id for an experiment identified by its name.

        Parameters
        ----------
        experiment_name : str
            Name of the experiment to update.
        tuning_job_id : str
            The new tuning job ID to set for the experiment.
        """
        experiments_path = self.base_dir / "experiments.parquet"

        # Create a temporary view of the experiments table
        self.conn.execute(
            f"CREATE OR REPLACE TABLE experiments AS SELECT * FROM read_parquet('{experiments_path}')"
        )

        # Update the tuning_job_id and last_updated timestamp for the specified experiment
        update_query = f"""
            UPDATE experiments
            SET tuning_job_id = '{tuning_job_id}',
                last_updated = '{datetime.now().isoformat()}'
            WHERE experiment_name = '{experiment_name}'
        """
        self.conn.execute(update_query)

        # Save the updated experiments table back to parquet
        self.conn.execute(f"COPY experiments TO '{experiments_path}' (FORMAT PARQUET)")

    def complete_experiment(self, experiment_name: str, status="completed"):
        """
        Mark an experiment as completed and update its stats

        Parameters
        ----------
        experiment_name : str
            Name of the experiment to complete
        status : str
            Final status ('completed' or 'failed')
        """
        experiments_path = self.base_dir / "experiments.parquet"

        # Update stats first
        self.update_experiment_stats(experiment_name)

        # Create a temporary view of the experiments table
        self.conn.execute(
            f"CREATE OR REPLACE TABLE experiments AS SELECT * FROM read_parquet('{experiments_path}')"
        )

        # Update the status using SQL
        update_query = f"""
            UPDATE experiments 
            SET status = '{status}',
                last_updated = '{datetime.now().isoformat()}'
            WHERE experiment_name = '{experiment_name}'
        """

        self.conn.execute(update_query)

        # Save back to parquet
        self.conn.execute(f"COPY experiments TO '{experiments_path}' (FORMAT PARQUET)")

    def update_experiment_eval_dataset_id(
        self, experiment_name: str, eval_dataset_id: str
    ):
        """Update an experiment record with an evaluation dataset ID. If the column doesn't exist, it will be created."""

        experiments_path = self.base_dir / "experiments.parquet"

        # Load existing experiments
        experiments_df = pd.read_parquet(experiments_path)

        # Add column if it doesn't exist
        if "eval_dataset_id" not in experiments_df.columns:
            experiments_df["eval_dataset_id"] = None

        # Update the record
        experiments_df.loc[
            experiments_df["experiment_name"] == experiment_name, "eval_dataset_id"
        ] = eval_dataset_id
        experiments_df.loc[
            experiments_df["experiment_name"] == experiment_name, "last_updated"
        ] = datetime.now().isoformat()

        # Save back to parquet
        experiments_df.to_parquet(experiments_path, index=False)

        return True
