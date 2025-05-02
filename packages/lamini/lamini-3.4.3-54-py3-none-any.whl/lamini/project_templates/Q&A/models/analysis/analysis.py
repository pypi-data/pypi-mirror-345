import duckdb
import pandas as pd
from pathlib import Path
import textwrap
import os 

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

    def print_results(self, limit=None, chunk_id=None):
        """
        Print results from the database with consistent formatting
        
        Parameters
        ----------
        limit : int, optional
            Maximum number of results to print
        chunk_id : str, optional
            Specific chunk_id to filter for
        """
        query = "SELECT * FROM results"
        where_clauses = []
        
        if chunk_id:
            where_clauses.append(f"chunk_id = '{chunk_id}'")
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        if limit:
            query += f" LIMIT {limit}"
            
        results = self.conn.execute(query).df()
        
        if len(results) == 0:
            print("No results found matching the criteria.")
            return
            
        for _, row in results.iterrows():
            print("\n" + "=" * 100)
            print(f"Chunk ID: {row['chunk_id']}")
            if self.experiment_name is None:
                print(f"Experiment: {row['experiment_name']}")
            print("-" * 100)
            
            # Print question
            question = row['question_generator_output'].get('question', 'N/A')
            print("Question:")
            print(textwrap.fill(question, width=100, replace_whitespace=False))
            
            print("-" * 100)
            
            # Print answer
            answer = row['answer_generator_output'].get('answer', 'N/A')
            print("Answer:")
            print(textwrap.fill(answer, width=100, replace_whitespace=False))
            
            print("-" * 100)
            
            # Print validation result
            is_valid = row['FactValidator_output'].get('is_valid', 'N/A')
            print(f"Valid: {is_valid}")
            print("=" * 100)

    def _wrap_text(self, text, width=100):
        """Helper function to wrap text at specified width"""
        return textwrap.fill(text, width=width, replace_whitespace=False)

    def _print_record(self, row, include_context=False):
        """Helper function to print a single record with consistent formatting"""
        print("\n" + "=" * 100)
        print(f"Chunk ID: {row['chunk_id']}")
        print("-" * 100)
        print("Question:")
        print(self._wrap_text(row['question']))
        print("-" * 100)
        print("Answer:")
        print(self._wrap_text(row['answer']))
        if include_context and 'context' in row:
            print("-" * 100)
            print("Context:")
            print(self._wrap_text(row['context']))
        print("=" * 100)

    def get_summary_stats(self):
        """Get basic statistics about the experiment results"""
        query = """
        SELECT 
            COUNT(*) as total_pairs,
            SUM(CASE WHEN CAST(FactValidator_output->>'is_valid' AS BOOLEAN) THEN 1 ELSE 0 END) as valid_pairs,
            ROUND(AVG(CASE WHEN CAST(FactValidator_output->>'is_valid' AS BOOLEAN) THEN 1.0 ELSE 0.0 END) * 100, 2) as validity_rate
        FROM results
        """
        return self.conn.execute(query).fetchone()

    def get_valid_qa_pairs(self, limit=None):
        """Get all valid question-answer pairs"""
        query = """
        SELECT 
            chunk_id,
            question_generator_output->>'question' as question,
            answer_generator_output->>'answer' as answer
        FROM results
        WHERE CAST(FactValidator_output->>'is_valid' AS BOOLEAN) = true
        """
        if limit:
            query += f" LIMIT {limit}"
        df = self.conn.execute(query).df()
        
        print("\nValid Q&A Pairs:")
        for _, row in df.iterrows():
            self._print_record(row)
        
        return df

    def search_by_keyword(self, keyword, context=False):
        """Search through questions and answers for a keyword"""
        select_clause = """
            chunk_id,
            question_generator_output->>'question' as question,
            answer_generator_output->>'answer' as answer
        """
        if context:
            select_clause += """,
            answer_generator_input->>'chunk_text' as context
            """

        query = f"""
        SELECT {select_clause}
        FROM results
        WHERE 
            (LOWER(question_generator_output->>'question') LIKE LOWER($1))
            OR (LOWER(answer_generator_output->>'answer') LIKE LOWER($1))
        """
        df = self.conn.execute(query, [f'%{keyword}%']).df()
        
        print(f"\nSearch Results for '{keyword}':")
        for _, row in df.iterrows():
            self._print_record(row, include_context=context)
        
        return df

    def get_invalid_responses(self, limit=None):
        """Get questions and answers that were marked as invalid"""
        query = """
        SELECT 
            chunk_id,
            question_generator_output->>'question' as question,
            answer_generator_output->>'answer' as answer,
            FactValidator_output->>'is_valid' as is_valid
        FROM results
        WHERE CAST(FactValidator_output->>'is_valid' AS BOOLEAN) = false
        """
        if limit:
            query += f" LIMIT {limit}"
        df = self.conn.execute(query).df()
        
        print("\nInvalid Responses:")
        for _, row in df.iterrows():
            self._print_record(row)
        
        return df

    def custom_query(self, query, parameters=None):
        """Execute a custom SQL query"""
        if parameters:
            return self.conn.execute(query, parameters).df()
        return self.conn.execute(query).df()

    def get_qa_pairs_with_validity(self, limit=None):
        """
        Get all question-answer pairs with their validity status
        
        Args:
            limit (int, optional): Number of results to return
            
        Returns:
            pandas.DataFrame: DataFrame containing questions, answers, and validity status
        """
        
        query = """
        SELECT 
            question_generator_output->>'question' as question,
            answer_generator_output->>'answer' as answer,
            CAST(FactValidator_output->>'is_valid' AS BOOLEAN) as is_valid
        FROM results
        ORDER BY CAST(FactValidator_output->>'is_valid' AS BOOLEAN) DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        
        return self.conn.execute(query).df()

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
    def print_result(result):
        """
        Static method to print a single result with consistent formatting.
        Can be used outside of ResultsAnalyzer instance.
        
        Parameters
        ----------
        result : dict
            Dictionary containing result data with keys for outputs from each generator
        """
        print("\n" + "=" * 100)
        print(f"Chunk ID: {result.get('chunk_id', 'N/A')}")
        print("-" * 100)
        
        # Print question
        question = result.get('question_generator_output', {}).get('question', 'N/A')
        print("Question:")
        print(textwrap.fill(question, width=100, replace_whitespace=False))
        
        print("-" * 100)
        
        # Print answer
        answer = result.get('answer_generator_output', {}).get('answer', 'N/A')
        print("Answer:")
        print(textwrap.fill(answer, width=100, replace_whitespace=False))
        
        print("-" * 100)
        
        # Print validation result
        is_valid = result.get('FactValidator_output', {}).get('is_valid', 'N/A')
        print(f"Valid: {is_valid}")
        print("=" * 100)