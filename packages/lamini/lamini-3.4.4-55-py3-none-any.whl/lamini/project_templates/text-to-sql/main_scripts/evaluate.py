import lamini
import json
import pandas as pd
from tqdm import tqdm
import os
import argparse
from pathlib import Path
from lamini import Lamini
import numpy as np
import openai
import yaml
import sys 
import torch
from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as plt
# Note: pyarrow is required for parquet file support. Install with: pip install pyarrow
import pyarrow.parquet as pq
path_add =os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if not path_add in sys.path:
    sys.path.append(path_add)
from utils.utils import reduce_dimensionality, similarity_check
from utils.utils import save_results_to_jsonl, load_config, format_glossary, read_jsonl
from lamini.experiment.error_analysis_eval import SQLExecutionPipeline

DEFAULT_SYSTEM_MESSAGE = (
    "You are a SQL‐generation assistant.  "
    "Given a natural‐language question and table/schema glossary, output only the "
    "corresponding SQL query (no prose)."
)

def load_project_config(project_name):
    """Load project configuration from YAML file."""
    project_yml_path = os.path.join(Path(__file__).parent.parent, 'projects', project_name, 'ymls', 'project.yml')
    with open(project_yml_path, 'r') as file:
        project_config = yaml.safe_load(file)
    return project_config

def initialize_llm(project_name):
    """Initialize LLM with project configuration."""
    project_config = load_project_config(project_name)
    api_key = project_config['Lamini']['api_key']
    model_name = project_config['Project']['model']
    
    os.environ['LAMINI_API_KEY'] = api_key
    return Lamini(model_name, api_key=api_key)

def get_text_embeddings(text_list, project_name=None, model_name="sentence-transformers/all-MiniLM-L6-v2", batch_size=32):
    """
    Computes text embeddings for a list of strings.
    Uses the specified transformer model and processes texts in batches.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Use CPU explicitly (adjust if you intend to use GPU)
    device = torch.device("cpu")
    model = model.to(device)

    embeddings_list = []
    num_samples = len(text_list)
    for start_idx in range(0, num_samples, batch_size):
        end_idx = min(start_idx + batch_size, num_samples)
        text_batch = text_list[start_idx:end_idx]

        with torch.no_grad():
            inputs = tokenizer(text_batch, padding=True, truncation=True, return_tensors="pt").to(device)
            outputs = model(**inputs)
            # Use the [CLS] token representation
            batch_embeddings = outputs.last_hidden_state[:, 0, :]
            embeddings_list.append(batch_embeddings)

    embeddings = torch.cat(embeddings_list, dim=0)
    return embeddings.numpy()

def get_embeddings_from_strings(strings, project_name):
    path_yml = os.path.join(Path(__file__).parent.parent, 'projects', project_name, 'ymls', 'project.yml')
    with open(path_yml, 'r') as file:
        project_data = yaml.safe_load(file)

    client = openai.OpenAI(
        api_key=project_data['Lamini']['api_key'],
        base_url=project_data['Lamini']['base_url_inf'],
    )

    embeddings = []
    for s in strings:
        
        embedding = client.embeddings.create(
                model="text-embedding-3-small",
                input=s,
                encoding_format="float"
            )
        embeddings.append(embedding.data[0].embedding)
    return embeddings

def cosine_similarity_of_embeddings(answer_groundtruth, answer_generated,project_name):
    
    path_yml =os.path.join(Path(__file__).parent.parent,'projects',project_name,'ymls','project.yml')
    with open(path_yml, 'r') as file:
        project_data = yaml.safe_load(file)
        
    client = openai.OpenAI(
            api_key=project_data['Lamini']['api_key'],
            base_url=project_data['Lamini']['base_url_inf'],
        )
    # Create embeddings for both answers
    groundtruth_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=[answer_groundtruth],
        encoding_format="float"
    )["data"][0]["embedding"]

    generated_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=[answer_generated],
        encoding_format="float"
    )["data"][0]["embedding"]

    # Compute cosine similarity
    groundtruth_embedding = np.array(groundtruth_embedding)
    generated_embedding = np.array(generated_embedding)

    cosine_similarity = np.dot(groundtruth_embedding, generated_embedding) / (
        np.linalg.norm(groundtruth_embedding) * np.linalg.norm(generated_embedding)
    )

    return cosine_similarity

def llm_sql_evaluator(ref_sql: str, gen_sql: str, question: str, project_name: str):
    """
    Compare two SQL queries for the same question, and judge if the generated SQL
    is correct relative to the ground truth.

    Returns a dict: {
      'explanation': str,   # why the generated SQL is or isn't correct
      'correct': bool       # whether it matches the intent/results of the ref_sql
    }
    """
    # 1) System prompt setting the task
    system_prompt = (
        "You are a SQL evaluation assistant.  "
        "Given a natural-language question and two SQL queries "
        "(the ground-truth and the generated), determine "
        "whether the generated SQL correctly answers the question.  "
        "Respond with valid JSON: "
        "{'explanation': <detailed rationale>, 'correct': <true|false>}."
    )

    # 2) User prompt containing the question and both SQLs
    user_prompt = (
        f"========== Question ==========\n{question.strip()}\n\n"
        f"====== Ground-Truth SQL ======\n{ref_sql.strip()}\n\n"
        f"====== Generated SQL ========\n{gen_sql.strip()}\n\n"
        "Does the generated SQL correctly implement the intent of the ground-truth? "
        "Answer only with the JSON object as specified above."
    )
    llm_compare = initialize_llm(project_name)

    # 3) Build the full prompt
    full_prompt = make_prompt(user_prompt, system_prompt)

    
    # 4) Invoke your comparison LLM
    return llm_compare.generate(
        full_prompt,
        output_type={"explanation": "str", "correct": "bool"}
    )
    
def make_prompt(user_input, system_message):
    """
    Constructs a formatted prompt string for the language model by embedding the user input
    and system message within a structured template.

    Parameters:
        user_input (str): The input question or query from the user.
        system_message (str): The system message to set the context.

    Returns:
        str: A formatted string that serves as a prompt for the language model.
    """
    prompt = "<|start_header_id|>system<|end_header_id|>" + system_message
    prompt += "<|eot_id|>"  # End of the system header
    prompt += "<|start_header_id|>user<|end_header_id|>"  # Start of the user header
    prompt += user_input  # Append the user's question to the prompt
    prompt += "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"  # Marks the start of the assistant's response

    return prompt

def read_test_set(file_path):
    """Read the test set from parquet file and extract questions and ref queries."""
    try:
        # Read the parquet file
        df = pd.read_parquet(file_path)
        
        # Convert to list of dictionaries
        test_cases = []
        for _, row in df.iterrows():
            test_cases.append({
                'question': row['input'],
                'ref_query': row['output']
            })
        return test_cases
    except Exception as e:
        print(f"Error reading parquet file: {e}")
        return []

def run_inference(test_cases, model_id, formatted_glossary):
    """Run inference for each question and extract SQL query."""
    llm = Lamini(model_name=model_id)
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case['question']
        prompt = f'''<|begin_of_text|><|start_header_id|>user<|end_header_id|> 

            Glossary: {formatted_glossary}
            
            Output only SQL - {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>'''
        
        try:
            response = llm.generate(prompt)
            test_case['generated_query'] = response
            results.append(test_case)
            
            print(f"Processed question {i}/{len(test_cases)}")
        except Exception as e:
            print(f"Error processing question {i}: {str(e)}")
            test_case['generated_query'] = f"Error: {str(e)}"
            results.append(test_case)
    
    return results

def prepare_for_evaluation(inference_results):
    """Prepare inference results for SQL execution pipeline."""
    test_cases = []
    for result in inference_results:
        if result.get('generated_query', '').startswith('Error:'):
            continue
            
        test_case = {
            'question': result['question'],
            'ref_query': result.get('ref_query', ''),
            'generated_query': result.get('generated_query', '')
        }
        test_cases.append(test_case)
    
    return test_cases

def read_glossary_from_parquet(project_name):
    """Read and format glossary from parquet file for a specific project."""
    # Construct path to glossary parquet file
    glossary_path = Path(__file__).parent.parent / "local-db" / "glossary.parquet"
    
    if not glossary_path.exists():
        raise FileNotFoundError(f"Glossary parquet file not found at {glossary_path}")
    
    # Read the parquet file
    glossary_df = pd.read_parquet(glossary_path)
    
    # Filter for the specific project
    project_glossary_df = glossary_df[glossary_df["project_id"] == project_name]
    
    # Format the glossary entries
    formatted_entries = []
    for _, row in project_glossary_df.iterrows():
        formatted_entries.append({
            'input': row['input'],
            'output': row['output']
        })
    
    # Use existing format_glossary function to format the entries
    return format_glossary(formatted_entries)

def main(project_name):
    # Construct paths based on project name
    project_root = os.path.join(Path(__file__).parent.parent, 'projects', project_name)
    project_yml_path = os.path.join(project_root, 'ymls', 'project.yml')
    
    # Load project configuration
    with open(project_yml_path, 'r') as file:
        project_config = yaml.safe_load(file)
    
    # Set up Lamini API configuration
    lamini_api_url = project_config['Lamini']['base_url_inf']
    lamini_api_key = project_config['Lamini']['api_key']
    
    lamini.api_url = lamini_api_url
    lamini.api_key = lamini_api_key
    os.environ["LAMINI_API_URL"] = lamini_api_url
    os.environ["LAMINI_API_KEY"] = lamini_api_key

    # Construct data paths
    data_dir = os.path.join(project_root, 'data')
    local_db_dir = Path(__file__).parent.parent / "local-db"
    test_set_path = local_db_dir / "evalset.parquet"
    db_path = os.path.join(data_dir, f'{project_name}.sqlite')
    
    model_id = input("Enter the model ID for inference (this is the output model ID from memory tuning): ")
    
    analysis_model = project_config['Project']['model']
    
    results_dir = os.path.join(project_root, 'experiment_results')
    os.makedirs(results_dir, exist_ok=True)
    
    inference_output_path = os.path.join(results_dir, "inference_results.json")
    analysis_output_path = os.path.join(results_dir, "analysis_results_with_data.json")
    report_output_path = os.path.join(results_dir, "analysis_report.md")
    
    db_connection_params = {
        "db_path": db_path
    }
    
    # Load and format glossary from parquet
    print("Reading and formatting glossary...")
    formatted_glossary = read_glossary_from_parquet(project_name)

    # Step 1: Read test set
    print("Reading test set...")
    test_cases = read_test_set(test_set_path)
    print(f"Found {len(test_cases)} test cases")
    
    # Step 2: Run inference with schema and glossary
    print("Running inference...")
    inference_results = run_inference(test_cases, model_id, formatted_glossary)
    print("Saving inference results...")
    save_results_to_jsonl(inference_results, inference_output_path)
    
    # Step 3: Prepare for evaluation
    evaluation_test_cases = prepare_for_evaluation(inference_results)
    print(f"Prepared {len(evaluation_test_cases)} test cases for evaluation")
    
    # Step 4: Initialize SQL execution pipeline
    print("Initializing SQL execution pipeline...")
    pipeline = SQLExecutionPipeline(
        model=analysis_model,
        db_type="sqlite",
    )
    
    # Step 5: Run evaluation
    print("Running SQL execution and evaluation...")
    evaluation_results = pipeline.evaluate_queries(
        evaluation_test_cases,
        connection_params=db_connection_params
    )
    
    # Step 6: Save evaluation results
    print("Saving evaluation results with actual query data...")
    save_results_to_jsonl(evaluation_results, analysis_output_path)
    
    # Step 7: Generate and save report
    print("Generating report...")
    report = pipeline.generate_report(evaluation_results)
    with open(report_output_path, 'w') as f:
        f.write(report)
    
    print(f"Done! Results saved to:")
    print(f"- Inference results: {inference_output_path}")
    print(f"- Analysis results with data: {analysis_output_path}")
    print(f"- Analysis report: {report_output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run inference and evaluation for Text-to-SQL model")
    parser.add_argument("--project_name", required=True, help="Project name to evaluate")
    
    args = parser.parse_args()
    main(args.project_name)