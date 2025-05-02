import duckdb
import pandas as pd
from pathlib import Path
import textwrap
import os 
from typing import Tuple

class ResultsAnalyzer:
    def __init__(self, experiment_name=None, base_dir="./local-db",project_name=None):
        """
        Initialize ResultsAnalyzer with optional experiment filter
        
        Parameters
        ----------
        experiment_name : str, optional
            Name of specific experiment to analyze. If None, will query across all experiments
        base_dir : str
            Base directory for the database
        """
        self.experiment_name = experiment_name
        base_dir = os.path.join(Path(__file__).parent.parent.parent, base_dir)
        self.base_dir = base_dir
        self.parquet_path = Path(base_dir) / "results.parquet"
        if not self.parquet_path.exists():
            raise FileNotFoundError(f"No results found at: {self.parquet_path}")
        
        self.conn = duckdb.connect()
        # Build the query for the Parquet file
        base_query = f"SELECT * FROM read_parquet('{self.parquet_path}')"
        
        if experiment_name:
            base_query += f" WHERE experiment_name = '{experiment_name}'"

        # Use CREATE OR REPLACE to ensure that the view is updated on each initialization
        self.conn.execute(f"CREATE OR REPLACE VIEW results AS {base_query}")
        
        self.output_dir = os.path.join(Path(__file__).parent.parent.parent, 'projects', project_name)

    def print_results(self, limit: int | None = None, schema_id: str | None = None):
        """
        Print question–SQL pairs from results.parquet with consistent formatting.

        Parameters
        ----------
        limit : int, optional
            Max number of rows to display.
        schema_id : str, optional
            If given, only show rows matching this schema_id.
        """
        # 1. Load only the necessary columns:
        parquet_path = os.path.join(self.base_dir, "results.parquet")
        cols = ["q2", "generated_sql", "is_valid", "schema_id", "experiment_name"]
        df = pd.read_parquet(parquet_path, columns=cols)

        # 2. Rename for clarity
        df = df.rename(columns={
            "q2": "question",
            "generated_sql": "sql",
        })

        # 3. Filter by schema_id if requested
        if schema_id is not None:
            df = df[df["schema_id"] == schema_id]

        # 4. Apply limit
        if limit is not None:
            df = df.head(limit)

        # 5. Early exit if empty
        if df.empty:
            print("No results found matching the criteria.")
            return

        # 6. Print each row
        for _, row in df.iterrows():
            print("\n" + "=" * 100)
            print(f"Schema ID: {row['schema_id']}")
            # only print the experiment name if this analyzer wasn't initialized
            # with a fixed experiment_name
            if self.experiment_name is None:
                print(f"Experiment: {row['experiment_name']}")
            print("-" * 100)

            # Question
            print("Question:")
            print(textwrap.fill(row["question"], width=100, replace_whitespace=False))
            print("-" * 100)

            # Generated SQL
            print("SQL:")
            print(textwrap.fill(row["sql"], width=100, replace_whitespace=False))
            print("-" * 100)

            # Validity flag
            print(f"Valid: {row['is_valid']}")
            print("=" * 100)

    def _wrap_text(self, text, width=100):
        """Helper function to wrap text at specified width"""
        return textwrap.fill(text, width=width, replace_whitespace=False)

    def _print_record(self, row, include_context: bool = False):
        """Helper to print a single QA/SQL record with consistent formatting."""
        print("\n" + "=" * 100)
        print(f"Schema ID: {row['schema_id']}")
        print("-" * 100)

        # Question
        print("Question:")
        print(self._wrap_text(row['question']))
        print("-" * 100)

        # Generated SQL
        print("SQL:")
        print(self._wrap_text(row['sql']))
        print("-" * 100)

        # Validity flag
        print(f"Valid: {row['is_valid']}")
        
        # Optional context
        if include_context and 'context' in row:
            print("-" * 100)
            print("Context:")
            print(self._wrap_text(row['context']))

        print("=" * 100)

    def get_summary_stats(self) -> tuple[int, int, float]:
        """
        Basic statistics for the experiment results stored in results.parquet.

        Returns
        -------
        tuple
            (total_pairs, valid_pairs, validity_rate) where validity_rate is a
            percentage rounded to two decimals.
        """
        parquet_path = os.path.join(self.base_dir, "results.parquet")

        # Load only the flag column
        df = pd.read_parquet(parquet_path, columns=["is_valid"])

        # Ensure boolean dtype
        if df["is_valid"].dtype != bool:
            df["is_valid"] = df["is_valid"].astype(bool)

        total_pairs = len(df)
        valid_pairs = int(df["is_valid"].sum())
        validity_rate = round((valid_pairs / total_pairs) * 100, 2) if total_pairs else 0.0

        return total_pairs, valid_pairs, validity_rate

    def get_valid_qa_pairs(self, limit: int | None = None) -> pd.DataFrame:
        """
        Get all valid question–SQL pairs from the parquet results.

        Parameters
        ----------
        limit : int, optional
            Maximum number of rows to return.

        Returns
        -------
        pandas.DataFrame
            DataFrame of valid pairs, with columns: schema_id, question, sql, is_valid.
        """
        # 1. Load only the needed columns from the parquet
        parquet_path = os.path.join(self.base_dir, "results.parquet")
        df = pd.read_parquet(parquet_path, columns=["schema_id", "q2", "generated_sql", "is_valid"])

        # 2. Rename for consistency
        df = df.rename(columns={"q2": "question", "generated_sql": "sql"})

        # 3. Ensure boolean dtype on is_valid
        if df["is_valid"].dtype != bool:
            df["is_valid"] = df["is_valid"].astype(bool)

        # 4. Filter to only valid rows
        df = df[df["is_valid"]]

        # 5. Apply limit if requested
        if limit is not None:
            df = df.head(limit)

        # 6. Print header and each record
        print("\nValid Q&sql Pairs:")
        for _, row in df.iterrows():
            self._print_record(row)

        return df.reset_index(drop=True)

    def search_by_keyword(self, keyword: str, context: bool = False) -> pd.DataFrame:
        """
        Search through questions and SQL for a keyword, and print matching records.

        Parameters
        ----------
        keyword : str
            Substring to search for (case-insensitive) in the question or SQL.
        context : bool, optional
            If True, include and print the 'context' column (if present).

        Returns
        -------
        pandas.DataFrame
            All matching rows with columns: schema_id, question, sql, is_valid
            (and 'context' if requested).
        """
        # 1. Load the parquet file with only the needed columns
        parquet_path = os.path.join(self.base_dir, "results.parquet")
        cols = ["schema_id", "q2", "generated_sql", "is_valid"]
        if context:
            cols.append("context")
        df = pd.read_parquet(parquet_path, columns=cols)

        # 2. Rename for clarity
        df = df.rename(columns={"q2": "question", "generated_sql": "sql"})

        # 3. Ensure is_valid is boolean
        if df["is_valid"].dtype != bool:
            df["is_valid"] = df["is_valid"].astype(bool)

        # 4. Filter by keyword in question or SQL (case-insensitive)
        mask = (
            df["question"].str.contains(keyword, case=False, na=False)
            | df["sql"].str.contains(keyword, case=False, na=False)
        )
        df = df[mask]

        # 5. Print results
        print(f"\nSearch Results for '{keyword}':")
        if df.empty:
            print("No matches found.")
        else:
            for _, row in df.iterrows():
                self._print_record(row, include_context=context)

        return df.reset_index(drop=True)

    def get_invalid_responses(self, limit: int | None = None) -> pd.DataFrame:
        """
        Get questions and SQL queries that were marked as invalid.

        Parameters
        ----------
        limit : int, optional
            Maximum number of rows to return.

        Returns
        -------
        pandas.DataFrame
            DataFrame of invalid pairs with columns: schema_id, question, sql, is_valid.
        """
        # 1. Load only the needed columns from the parquet
        parquet_path = os.path.join(self.base_dir, "results.parquet")
        df = pd.read_parquet(parquet_path, columns=["schema_id", "q2", "generated_sql", "is_valid"])

        # 2. Rename for clarity
        df = df.rename(columns={"q2": "question", "generated_sql": "sql"})

        # 3. Ensure is_valid is boolean
        if df["is_valid"].dtype != bool:
            df["is_valid"] = df["is_valid"].astype(bool)

        # 4. Filter to only invalid rows
        df = df[~df["is_valid"]]

        # 5. Apply limit if requested
        if limit is not None:
            df = df.head(limit)

        # 6. Print header and each record
        print("\nInvalid Responses:")
        for _, row in df.iterrows():
            self._print_record(row)

        return df.reset_index(drop=True)

    def custom_query(self, query, parameters=None):
        """Execute a custom SQL query"""
        if parameters:
            return self.conn.execute(query, parameters).df()
        return self.conn.execute(query).df()

    def get_qa_pairs_with_validity(self, limit: int | None = None) -> pd.DataFrame:
        """
        Return question / SQL pairs together with their validity flag.

        Parameters
        ----------
        limit : int, optional
            Maximum number of rows to return (top-N after sorting by `is_valid`).

        Returns
        -------
        pandas.DataFrame
            Columns: ``question``, ``sql``, ``is_valid``.
        """
        # 1. Locate the parquet produced by your pipeline
        parquet_path = os.path.join(self.base_dir, "results.parquet")

        # 2. Load only the three relevant columns
        df = pd.read_parquet(parquet_path, columns=["q2", "generated_sql", "is_valid"])

        # 3. Rename for external use
        df = df.rename(columns={"q2": "question", "generated_sql": "sql"})

        # 4. Make sure `is_valid` is boolean
        if df["is_valid"].dtype != bool:
            df["is_valid"] = df["is_valid"].astype(bool)

        # 5. Sort valid pairs first (True > False) and apply limit if requested
        df = df.sort_values("is_valid", ascending=False, kind="mergesort")
        if limit is not None:
            df = df.head(limit)
        return df.reset_index(drop=True)

    def export_to_csv(self, df, filename_prefix="qa_pairs"):
        """
        Export any DataFrame to CSV with timestamp
        
        Args:
            df (pandas.DataFrame): DataFrame to export
            filename_prefix (str, optional): Prefix for the CSV filename
            
        Returns:
            str: Path to the created CSV file
        """

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        csv_path = self.output_dir / f"{filename_prefix}_{timestamp}.csv"
        
        # Save to CSV
        df.to_csv(csv_path, index=False)
        print(f"Data exported to: {csv_path}")
        return str(csv_path)

    @staticmethod
    def print_result(result: dict, include_context: bool = False):
        """
        Static method to print a single result with consistent formatting.
        Can be used outside of ResultsAnalyzer instance.

        Parameters
        ----------
        result : dict
            Dictionary containing keys:
            - 'schema_id'
            - 'question'
            - 'sql'
            - 'is_valid'
            - optionally 'context'
        include_context : bool, optional
            Whether to print the 'context' field if present.
        """
        print("\n" + "=" * 100)
        print(f"Schema ID: {result.get('schema_id', 'N/A')}")
        print("-" * 100)

        # Question
        print("Question:")
        print(textwrap.fill(result.get('question', 'N/A'), width=100, replace_whitespace=False))
        print("-" * 100)

        # SQL
        print("SQL:")
        print(textwrap.fill(result.get('sql', 'N/A'), width=100, replace_whitespace=False))
        print("-" * 100)

        # Validity flag
        print(f"Valid: {result.get('is_valid', 'N/A')}")

        # Optional context
        if include_context and 'context' in result:
            print("-" * 100)
            print("Context:")
            print(textwrap.fill(result.get('context', ''), width=100, replace_whitespace=False))

        print("=" * 100)