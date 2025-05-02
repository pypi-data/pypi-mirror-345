import lamini
import json
import pandas as pd
from tqdm import tqdm
import os
import argparse
from pathlib import Path

DEFAULT_SYSTEM_MESSAGE = (
    "You are a experience assistant. Please answer the user's question thoroughly."
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

def process_eval_data(eval_file_path, model_id, system_message, project_name=None):
    # The expected output type from the language model, specifying that it should return a string.
    output_type = {"answer": "str"}
    llm = lamini.Lamini(model_name=model_id)

    if not eval_file_path.endswith('.jsonl'):
        print("Error: Evaluation data should be in JSONL format.")
        return

    try:
        with open(eval_file_path, 'r') as file:
            df = pd.json_normalize([json.loads(line) for line in file.readlines()])
    except Exception as e:
        print(f"Error reading JSONL file: {e}")
        return

    results = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing records"):
        user_input = row['question']
        prompt = make_prompt(user_input, system_message)
        try:
            model_response = llm.generate(prompt, output_type=output_type)
            results.append({
                'question': user_input,
                'response': model_response['answer']
            })
        except Exception as e:
            print(f"Error processing record: {e}")
            continue
    
    if project_name!=None:
        # Ensure the output directory exists.
        os.makedirs(os.path.join(Path(__file__).parent.parent,project_name,'experiment_results'), exist_ok=True)
        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(Path(__file__).parent.parent,project_name,'experiment_results', 'evaluation_results.csv'), index=False)
        print(f"Processed {len(results)} records. Results saved to evaluation_results.csv")
    else:
        path_result = os.path.join('experiment_results')
        os.makedirs(path_result, exist_ok=True)
        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(path_result, 'evaluation_results.csv'), index=False)
        print(f"Processed {len(results)} records. Results saved to evaluation_results.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process evaluation data using specified LLM model.')
    parser.add_argument('--eval_file_path', type=str, required=True, help='Path to the evaluation JSONL data file')
    parser.add_argument('--model_id', type=str, required=True, help='Model ID for the LLM')
    parser.add_argument('--system_message', type=str, default=DEFAULT_SYSTEM_MESSAGE,
                        help='System message for the prompt. If not provided, a default message is used.')

    args = parser.parse_args()
    process_eval_data(args.eval_file_path, args.model_id, args.system_message)