from lamini.generation.base_prompt_object import PromptObject
from lamini.experiment.base_experiment_object import ExperimentObject
import duckdb
import pandas as pd
from pathlib import Path
from lamini import Lamini
import os 
from openai import OpenAI
import yaml
import re
import hashlib
import shutil
from lamini.experiment.base_experiment_object import ExperimentObject
import duckdb
import pandas as pd
from models.analysis.analysis import ResultsAnalyzer
from pathlib import Path
from lamini import Lamini
import copy
from openai import OpenAI
import yaml
import hashlib
from copy import deepcopy
import numpy as np
from typing import List, Union, Dict
from openai import OpenAI

from fuzzywuzzy import fuzz as fuzz_wuzzy
from rapidfuzz import fuzz as fuzz_rapid
import jaro 
import json
from sklearn.decomposition import PCA
import umap
from sklearn.manifold import TSNE
import torch
from transformers import AutoTokenizer, AutoModel
import os
import yaml
import json
import sqlite3

from lamini.generation.base_prompt_object import PromptObject

def read_jsonl(file_path):
    """Read JSONL file and return list of JSON objects."""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def get_schema(db_path):
    """Get schema for all tables from SQLite database with error handling."""
    try:
        if not os.path.exists(db_path):
            print(f"Database file not found at: {db_path}")
            return ""
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        print("Tables found in database:", tables)
        
        if not tables:
            print("No tables found in the database")
            return ""
        
        # Build complete schema for all tables
        full_schema = []
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Format the table schema
            columns_info = [f"{col[1]} {col[2]}" for col in columns]
            table_schema = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns_info) + "\n);"
            full_schema.append(table_schema)
        
        conn.close()
        return "\n\n".join(full_schema)
        
    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def format_glossary(glossary_entries):
    """Format glossary entries into a readable string."""
    formatted = []
    for entry in glossary_entries:
        formatted.append(f"{entry['input']}: {entry['output']}")
    return "\n".join(formatted)

def save_results_to_jsonl(data, output_path):
    """Save results to a JSONL file - handles both lists and dictionaries."""
    try:
        if isinstance(data, list):
            print(f"Saving list data with {len(data)} items")
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            print(f"Saving dictionary data with keys: {list(data.keys())}")
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
        print(f"Successfully saved data to {output_path}")
    except Exception as e:
        print(f"Error saving data: {str(e)}")
        print(f"Data type: {type(data)}")

def save_results(results, output_path, append=True):
    mode = 'a' if append else 'w'
    with open(output_path, mode) as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
            
def process_variation(variation, generator, sql_gen, sql_validator, sql_debugger, schema, glossary, is_subq=False, original_question=None, original_sql=None):
    """
    Process a single variation through the pipeline: SQL generation, validation, and debugging.
    """
    # Extract the question text based on whether it's a subquestion or not
    question_key = "sub_question" if is_subq else "question"
    
    if isinstance(variation, str):
        question_text = variation
    elif hasattr(variation, 'data') and isinstance(variation.data, dict):  
        question_text = variation.data.get(question_key, "")
    elif hasattr(variation, 'get'):  
        question_text = variation.get(question_key, "")
    else:
        question_text = ""
    
    if not question_text:
        return None
    
    print(f"Processing {'sub-question' if is_subq else 'variation'}: {question_text}")
    
    # Generate SQL for the variation
    sql_prompt = PromptObject("", data={
        "question": question_text,  
        "sub_question": question_text, 
        "schema": schema,
        "glossary": glossary,
        "original_question": original_question, 
        "original_sql": original_sql 
    })
    
    sql_result = sql_gen(sql_prompt)
    if not sql_result or "sql_query" not in sql_result.response:
        return None
    
    # Create result object
    result = {
        question_key: question_text,
        "generated_sql": sql_result.response["sql_query"]
    }
    
    # Validate SQL
    validation_prompt = PromptObject("", data={
        "sql_query": result["generated_sql"],
        "schema": schema,
        "glossary": glossary
    })
    validation_result = sql_validator(validation_prompt)
    
    if validation_result and validation_result.response:
        if not validation_result.response.get("is_valid", False):
            # Debug invalid SQL
            debug_prompt = PromptObject("", data={
                "error_message": validation_result.response.get("error", ""),
                "error_explanation": validation_result.response.get("explanation", ""),
                "error_sql": result["generated_sql"],
                "sub_question": question_text,
                "schema": schema,
                "glossary": glossary
            })
            
            debug_result = sql_debugger(debug_prompt)
            if debug_result and debug_result.response and "corrected_sql" in debug_result.response:
                result["corrected_sql"] = debug_result.response["corrected_sql"]
                
                # Validate corrected SQL
                corrected_validation = sql_validator(PromptObject("", data={
                    "sql_query": debug_result.response["corrected_sql"],
                    "schema": schema,
                    "glossary": glossary
                }))
                result["final_validation"] = corrected_validation.response
            else:
                result["validation"] = validation_result.response
        else:
            result["validation"] = validation_result.response
            result['generated_sql'] = validation_result.data['sql_query']
    
    return result

def generate_variations(generator, prompt_data, result_key):
    """
    Generate variations using the specified generator
    """
    from lamini.generation.base_prompt_object import PromptObject
    
    prompt = PromptObject("", data=prompt_data)
    result = generator(prompt)
    
    if not result:
        print(f"Warning: Generator returned None or empty result")
        return []
        
    if hasattr(result, 'response') and isinstance(result.response, dict):
        # Get the list of variations from the response using the result_key
        variations = result.response.get(result_key, [])
        print(f"Generated {len(variations)} {result_key}")
        return variations
    
    print(f"Warning: Unexpected result format: {type(result)}")
    return []

def extract_sql(variation):
    """Extract the correct SQL based on validation status."""
    if 'corrected_sql' in variation and 'final_validation' in variation:
        if variation['final_validation'].get('is_valid', True):
            return variation['corrected_sql']
        return None  
    
    if 'generated_sql' in variation:
        if 'validation' in variation:
            if variation['validation'].get('is_valid', True):
                return variation['generated_sql']
            return None  
        return variation['generated_sql']
        
    return None

def process_jsonl(input_file, output_file=None, input_key="input", output_key="output"):
    """Process JSONL file and create flattened JSONL output with just question and SQL."""
    rows = []
    
    with open(input_file, 'r') as file:
        for line in file:
            try:
                data = json.loads(line.strip())
                for var in data['pattern_variations']:
                    if 'question' in var:
                        sql = extract_sql(var)
                        if sql:  
                            rows.append({
                                input_key: var['question'],
                                output_key: sql
                            })
                for var in data['structural_variations']:
                    if 'question' in var:
                        sql = extract_sql(var)
                        if sql:  
                            rows.append({
                                input_key: var['question'],
                                output_key: sql
                            })
                for q in data['sub_questions']:
                    if 'sub_question' in q:
                        sql = extract_sql(q)
                        if sql: 
                            rows.append({
                                input_key: q['sub_question'],
                                output_key: sql
                            })
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON line: {e}")
            except Exception as e:
                print(f"Error processing line: {e}")

    if output_file:
        with open(output_file, 'w') as file:
            for row in rows:
                json.dump(row, file)
                file.write('\n')

    print(f"Total rows processed: {len(rows)}")
    return rows

def jsonl_to_string(jsonl_file, input_key="input", output_key="output"):
    """Format JSONL file, e.g. glossary, into a readable string."""
    rows = read_jsonl(jsonl_file)
    formatted = []
    for row in rows:
        formatted.append(f"{row[input_key]}: {row[output_key]}")
    return "\n".join(formatted)

def get_user_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [default: {default}]: ")
        return user_input if user_input.strip() else default
    else:
        return input(f"{prompt}: ")
    
def load_config(config_path="config.yml"):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
    
def reduce_dimensionality(x: np.ndarray, method: str = "pca", dim: int = 2) -> np.ndarray:
    """
    Reduces the dimensionality of the embeddings using the specified method.
    Options for `method`: 'pca', 'umap', or 'tsne'. Target dimension must be 2 or 3.
    """
    if dim not in (2, 3):
        raise ValueError("The target dimension 'dim' must be either 2 or 3.")

    method = method.lower()

    if method == "pca":
        reducer = PCA(n_components=dim)
    elif method == "umap":
        reducer = umap.UMAP(n_components=dim)
    elif method == "tsne":
        reducer = TSNE(n_components=dim)
    else:
        raise ValueError("Method must be either 'pca', 'umap', or 'tsne'.")

    x_reduced = reducer.fit_transform(x)
    return x_reduced

def similarity_check(str1: str, str2: str, method: str) -> float:
    """
    Computes the similarity score between two strings using different fuzzy matching methods.
    Parameters:
    str1 (str): First string to compare.
    str2 (str): Second string to compare.
    method (str): Method of fuzzy matching. Options:
            - 'fuzzywuzzy': Uses fuzzywuzzy's ratio() for similarity score.
            - 'rapidfuzz': Uses rapidfuzz's ratio() for similarity score.
            - 'jarowinkler': Uses Jaro-Winkler metric for similarity score.
            - 'all': Averages the scores from 'fuzzywuzzy', 'rapidfuzz', and 'jarowinkler'.
    Returns:
    float: Similarity score (float between 0 and 100).
    """
    if method == 'fuzzywuzzy':
        score = fuzz_wuzzy.ratio(str1, str2)  # Calculate similarity using fuzzywuzzy
    elif method == 'rapidfuzz':
        score = fuzz_rapid.ratio(str1, str2)  # Calculate similarity using rapidfuzz
    elif method == 'jarowinkler':
        score = 100 * jaro.jaro_winkler_metric(str1, str2)  # Calculate similarity using Jaro-Winkler
    elif method == 'all':
        # Calculate average similarity using all methods
        score = np.mean([
            fuzz_wuzzy.ratio(str1, str2),
            fuzz_rapid.ratio(str1, str2),
            100 * jaro.jaro_winkler_metric(str1, str2)
        ])
    else:
        raise ValueError("Invalid method! Choose from 'fuzzywuzzy', 'rapidfuzz', 'jarowinkler', or 'all'.")

    return score  # Return the calculated similarity score

def get_text_embeddings(
    texts: List[str],
    api_key: str,
    api_base_url: str,
    model: str,
    batch_size: int = 512,
) -> List[List[float]]:
    """
    Convert a list of texts into embeddings.

    Args:
        texts: List of strings to embed.
        api_key: Your OpenAI API key.
        api_base_url: Base URL for the OpenAI API.
        model: The embedding model name (e.g. "text-embedding-3-small").
        batch_size: Number of texts to send in each batch.

    Returns:
        A list of embedding vectors (one per input text).
    """
    client = OpenAI(api_key=api_key, base_url=api_base_url)
    all_embeddings: List[List[float]] = []

    # Process in batches to avoid request-size limits
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(
            model=model,
            input=batch,
            encoding_format="float"
        )
        # Each resp.data item has an `.embedding` field
        for item in resp.data:
            all_embeddings.append(item.embedding)

    return all_embeddings



def experiment_to_csv(experiment_name):
    analyzer = ResultsAnalyzer(experiment_name)
    qa_pairs = analyzer.get_qa_pairs_with_validity(limit=20)  # get first 20 pairs
    all_pairs = analyzer.get_qa_pairs_with_validity()
    
    print("\nExperiment Summary:")
    print("=" * 50)
    print(f"Experiment Name: {experiment_name}")

    # Optional: Show a sample of valid Q&A pairs
    print("\nSample of valid Q&A pairs:")
    print("-" * 50)
    valid_pairs = analyzer.get_valid_qa_pairs(limit=3)
    print(valid_pairs)

    # Export all pairs to CSV
    csv_path = analyzer.export_to_csv(all_pairs, filename_prefix="all_qa_pairs")
    print(f"\nFull results exported to: {csv_path}")
    
def generate_prompts_class_from_yml(yml_path: str, output_path: str = "prompts.py"):
    # Load prompts.yml
    
    with open(yml_path, "r", encoding="utf-8") as f:
        prompt_yml = yaml.safe_load(f)
    
    prompts = prompt_yml.get("prompts", {})
    
    # Start building the class as a string
    class_code = "class Prompts:\n"

    for key in prompts:
        prompt_name = key.upper()
        template = prompts[key].get("template", "").strip()
        
        # Replace {{var}} with {var} to make Python f-string compatible
        formatted_template = template.replace("{{", "{").replace("}}", "}")
        
        # Indent each line by 4 spaces for class formatting
        indented_template = "\n".join(f"    {line}" for line in formatted_template.splitlines())
        
        class_code += f"\n    {prompt_name} = \"\"\"\n{indented_template}\n    \"\"\"\n"

    # Save to .py file
    output_file = Path(output_path)
    output_file.write_text(class_code.strip() + "\n", encoding="utf-8")
    print(f"`{output_file}` generated successfully from `{yml_path}`.")
    
def create_prompts_yml(focus_area: str, output_path: str = "ymls/prompts.yml"):
    indent = " " * 8
    def format_block(text: str) -> str:
        # Always prepend the indent (even for blank lines) to maintain consistency
        return "\n".join(f"{indent}{line}" for line in text.strip().splitlines())

    content = f"""prompts:
    question:
        description: Prompt for generating relevant questions from document chunks
        template: |
    {format_block(f'''
    Follow these steps closely, first consider the following document:
    {{{{product}}}}

    Second, consider the title of the documentation that outlines the best practices for {focus_area}:
    {{{{title}}}}

    Third, here is a description of the documentation that details the guidelines and procedures for {focus_area}:
    {{{{description}}}}

    Fourth, keep in mind the following keywords when writing your questions:
    {{{{keywords}}}}

    Fifth, read through the following text from the document:
    Page: {{{{page}}}}
    Source: {{{{source}}}}
    {{{{chunk_text}}}}

    Lastly, write a question that can be answered with respect to the document, description, and sourced by the text from the document noted above.
    ''')}

    answer:
        description: Prompt for generating answers to given questions from document chunks
        template: |
    {format_block(f'''
    Follow these steps closely, first consider the following document:
    {{{{product}}}}

    Second, consider the title of the document relevant to {focus_area}:
    {{{{title}}}}

    Third, here is a description of the document:
    {{{{description}}}}

    Fourth, read through the following text from the document:
    Page: {{{{page}}}}
    Source: {{{{source}}}}
    {{{{chunk_text}}}}

    Lastly, answer the following question and cite the source text from the document that correctly answers the question below. The answer should not be a single word or phrase; it should be a complete answer to the question and provide reference to the text of the document.
    {{{{question}}}}
    ''')}

    validator:
        description: Prompt for validating a question and its answer based on document content
        template: |
    {format_block(f'''
    Follow these steps closely, first consider the following document:
    {{{{product}}}}

    Second, consider the title of the document relevant to {focus_area}:
    {{{{title}}}}

    Third, here is a description of the document:
    {{{{description}}}}

    Fourth, read through the following text from the document:
    Page: {{{{page}}}}
    Source: {{{{source}}}}
    {{{{chunk_text}}}}

    Fifth, review the following question, paying attention to its relevance to the text from the document:
    {{{{question}}}}

    Sixth, compare this answer with the question above. Keep in mind the content of the document and best practices for {focus_area}
    {{{{answer}}}}

    Lastly, provide a boolean answer of [1, 0] on your determination if the question/answer pair is valid.
    ''')}
    """

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"`{output_file}` created successfully with focus area: '{focus_area}'")
    

def retreive_sample(json_files: dict, sample_size: int, job_id: int):
    start = sample_size * job_id
    end = sample_size * (job_id + 1)
    if end >= (len(json_files) - 50):
        end = len(json_files)
    sampled_json_files = list(json_files.keys())[start:end]
    return {file_: json_files[file_] for file_ in sampled_json_files}

def build_exp_obj_from_dataframe(
    df,  
    extract_columns,
    additional_data,
):
    """Build prompts from dataframe with optional additional data.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the chunks data
    extract_columns : List[str]
        Columns to extract from the dataframe
    additional_data : Dict[str, Any], optional
        Additional key-value pairs to add to each prompt's data
        
    Returns
    -------
    List[PromptObject]
        List of prompt objects with combined data
    """
    prompts = []
    
    for _, row in df.iterrows():
        # Start with the extracted columns
        data = {key_: row[key_] for key_ in extract_columns}
        
        # Add any additional data
        if additional_data:
            data.update(additional_data)
            
        prompts.append(ExperimentObject(
            experiment_step=None,#prompt = "",
            data = data
        ))
    
    print(prompts[0].data)
    return prompts

def build_prompts_from_dataframe(
    df,  
    extract_columns,
    additional_data,
):
    """Build prompts from dataframe with optional additional data.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the chunks data
    extract_columns : List[str]
        Columns to extract from the dataframe
    additional_data : Dict[str, Any], optional
        Additional key-value pairs to add to each prompt's data
        
    Returns
    -------
    List[PromptObject]
        List of prompt objects with combined data
    """

    prompts = []
    
    for _, row in df.iterrows():
        # Start with the extracted columns
        data = {key_: row[key_] for key_ in extract_columns}
        
        # Add any additional data
        if additional_data:
            data.update(additional_data)
            
        prompts.append(PromptObject(
            prompt = "",
            data = data
        ))
    
    print(prompts[0].data)
    return prompts

def save_schema(rich_schema, experiment_name, base_dir="./local-db"):
    """
    Save rich schema to a single parquet file using DuckDB, adding experiment_name as a column.
    Skips schema with exact matching schema_ids or with identical content.
    
    Parameters
    ----------
    rich_schema : List[Dict]
        List of dictionaries containing schema data. Each dictionary must contain a 'schema_id'
        and a 'content' key.
    experiment_name : str
        Name of the experiment to be added as a column.
    base_dir : str, optional
        Base directory for the database, defaults to './local-db'.
        
    Returns
    -------
    str
        Path to the saved parquet file.
    """
    base_dir=os.path.join(Path(__file__).parent.parent,base_dir)
    # Convert rich_schema to DataFrame and add experiment_name
    schema_df = pd.DataFrame(rich_schema)
    schema_df['experiment_name'] = experiment_name

    # Compute a content hash for each schema (using the 'content' field)
    if 'schema_text' in schema_df.columns:
        schema_df['content_hash'] = schema_df['schema_text'].apply(
            lambda x: hashlib.sha256(x.encode('utf-8')).hexdigest()
        )
    else:
        # Fallback: hash the entire row if 'content' column is not available.
        schema_df['content_hash'] = schema_df.apply(
            lambda row: hashlib.sha256(row.to_json().encode('utf-8')).hexdigest(), axis=1
        )

    # Initialize DuckDB connection
    conn = duckdb.connect()

    # Create output directory if it doesn't exist
    output_dir = Path(base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    parquet_path = output_dir / "schema.parquet"

    if parquet_path.exists():
        # Read existing data and get duplicate identifiers
        existing_df = conn.execute(
            f"SELECT * FROM read_parquet('{parquet_path}')"
        ).df()
        existing_schema_ids = set(existing_df['schema_id'].values)
        existing_content_hashes = set(existing_df['content_hash'].values)
        
        # Identify new schema: skip if either schema_id or content_hash already exists
        new_schema_mask = (~schema_df['schema_id'].isin(existing_schema_ids)) & \
                        (~schema_df['content_hash'].isin(existing_content_hashes))
        new_schema_df = schema_df[new_schema_mask]
        if len(new_schema_df) > 0:
            # Combine with existing data
            combined_df = pd.concat([existing_df, new_schema_df], ignore_index=True)
            # Register the combined DataFrame with DuckDB and write back to parquet
            conn.register("combined_df", combined_df)
            conn.execute("CREATE OR REPLACE TABLE schema AS SELECT * FROM combined_df")
            conn.execute(f"COPY schema TO '{parquet_path}' (FORMAT PARQUET)")
            print(f"Added {len(new_schema_df)} new schema")
            print(f"Skipped {len(schema_df) - len(new_schema_df)} duplicate schema")
        else:
            print("No new schema to add - all schema_ids or contents already exist in the database")
            combined_df = existing_df
    else:
        # No existing file, so write all schema to a new parquet file
        conn.register("schema_df", schema_df)
        conn.execute("CREATE TABLE schema AS SELECT * FROM schema_df")
        conn.execute(f"COPY schema TO '{parquet_path}' (FORMAT PARQUET)")
        new_schema_df = schema_df
        print(f"Created new database with {len(schema_df)} schema")
    
    # Verify the data
    total_schema = conn.execute(
        f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')"
    ).fetchone()[0]
    
    print(f"Schema saved to {parquet_path}")
    print(f"Total schema in database: {total_schema}")
    
    return str(parquet_path)

def save_results(results_df, experiment_name, base_dir="./local-db"):
    """
    Save experiment results to a single parquet file using DuckDB, adding experiment_name as a column.
    
    Parameters
    ----------
    results_df : pandas.DataFrame
        DataFrame containing the experiment results
    experiment_name : str
        Name of the experiment to be added as a column
    base_dir : str, optional
        Base directory for the database, defaults to ./local-db
        
    Returns
    -------
    str
        Path to the saved parquet file
    """
    base_dir=os.path.join(Path(__file__).parent.parent,base_dir)
    # Add experiment name to results
    results_df['experiment_name'] = experiment_name
    
    # Initialize DuckDB connection
    conn = duckdb.connect()
    
    # Create output directory if it doesn't exist
    output_dir = Path(base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    parquet_path = output_dir / "results.parquet"
    
    if parquet_path.exists():
        # Read existing data
        existing_df = conn.execute(f"SELECT * FROM read_parquet('{parquet_path}')").df()
        # Combine with new data
        combined_df = pd.concat([existing_df, results_df], ignore_index=True)
        # Write back to parquet
        conn.execute("CREATE TABLE results AS SELECT * FROM combined_df")
    else:
        # Create new parquet file
        conn.execute("CREATE TABLE results AS SELECT * FROM results_df")
    
    conn.execute(f"COPY results TO '{parquet_path}' (FORMAT PARQUET)")
    
    # Verify the data
    total_results = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')").fetchone()[0]
    new_results = len(results_df)
    
    print(f"Results saved to {parquet_path}")
    print(f"New results added: {new_results}")
    print(f"Total results in database: {total_results}")
    
    return str(parquet_path)

def clean_pycache():
    """
    Recursively deletes all __pycache__ directories in the current working directory
    and its subdirectories.
    """
    current_dir = os.getcwd()
    for root, dirs, files in os.walk(current_dir):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
            except Exception as e:
                print(f"Error deleting {pycache_path}: {str(e)}")

