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
path_add =os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if not path_add in sys.path:
    sys.path.append(path_add)
from utils.utils import reduce_dimensionality, similarity_check
DEFAULT_SYSTEM_MESSAGE = (
    "You are a experience assistant. Please answer the user's question thoroughly."
)
os.environ['LAMINI_API_KEY']='8354bff5db6fc1c4906d1b75a53ade1866cba05b0adaf8c749148f83225cc91a'

llm_compare = Lamini("meta-llama/Meta-Llama-3.1-8B-Instruct",api_key=os.environ['LAMINI_API_KEY'])



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

def llm_answer_evaluator(answer_groundtruth, answer_generated, question):
    # Build system prompt for concise instruction
    system_prompt = (
        "Compare the following two answers. They are similar if they convey the same information. "
        "Respond with valid JSON {'explanation' : str, 'similar' : bool}"
    )

    # Build user prompt with the ground truth, generated answers, and the question
    user_prompt = (
        f"========== Question =========\n{question.lower()}\n\n"
        f"========== Ground Truth Answer =========\n{answer_groundtruth.lower()}\n\n"
        f"========== Generated Answer =========\n{answer_generated.lower()}\n\n"
        "Are these answers similar based on the rules above?"
    )

    # Create a complete prompt using the provided templates
    prompt_output = make_prompt(user_prompt, system_prompt)

    return llm_compare.generate(prompt_output, output_type={"explanation": "str", "similar": "bool"})
    
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

def process_eval_data(model_id, system_message, project_name=None, experiment_name=None):
    
    eval_path = os.path.join(Path(__file__).parent.parent,'projects',project_name,'eval_data')
    files=os.listdir(eval_path)
    files = [x for x in files if x.endswith('.csv') or x.endswith('.jsonl')]   
    # Load the parquet file
    chunks_df = pd.read_parquet(os.path.join(Path(__file__).parent.parent, 'local-db', 'chunks.parquet'))
    # Filter the dataframe based on the experiment_name
    filtered_chunks_df = chunks_df[chunks_df['experiment_name'] == experiment_name]
    chunk_info = filtered_chunks_df['chunk_text'].to_list()

    for file in files:
        eval_file_path=os.path.join(eval_path,file)
        # The expected output type from the language model, specifying that it should return a string.
        output_type = {"answer": "str"}
        llm = lamini.Lamini(model_name=model_id)

        if not eval_file_path.endswith('.jsonl'):
            if not eval_file_path.endswith('.csv'):
                print("Error: Evaluation data should be in JSONL or CSV format.")
                return
            else:
                df = pd.read_csv(eval_file_path)
                # Check if required columns exist
                if not {'question', 'response'}.issubset(df.columns):
                    raise ValueError("CSV must contain 'question' and 'response' columns.")   
        else:
            try:
                with open(eval_file_path, 'r') as file:
                    df = pd.json_normalize([json.loads(line) for line in file.readlines()])
            except Exception as e:
                print(f"Error reading JSONL file: {e}")
                return
        
        results = []
        questions_list = df['question'].tolist()
        answers_list = df['response'].tolist()
        eval_question_embedding = get_text_embeddings(questions_list,project_name)
        train_question_embedding = get_text_embeddings(questions_list,project_name)
        chunk_embedding = get_text_embeddings(chunk_info,project_name)
        
        eval_question_embedding_2d = reduce_dimensionality(eval_question_embedding)
        train_question_embedding_2d = reduce_dimensionality(train_question_embedding)
        chunk_embedding_2d = reduce_dimensionality(chunk_embedding)
        
        
        # Create a 2D scatter plot for each set of embeddings with different colors
        plt.figure(figsize=(10, 7))

        # Scatter plot for eval_question_embedding_2d
        plt.scatter(eval_question_embedding_2d[:, 0], eval_question_embedding_2d[:, 1],
                    color='r', label='Eval Question Embedding', alpha=0.5)

        # # Scatter plot for train_question_embedding_2d
        # plt.scatter(train_question_embedding_2d[:, 0], train_question_embedding_2d[:, 1],
        #             color='g', label='Train Question Embedding', alpha=0.5)

        # Scatter plot for chunk_embedding_2d
        plt.scatter(chunk_embedding_2d[:, 0], chunk_embedding_2d[:, 1],
                    color='b', label='Chunk Embedding', alpha=0.5)

        plt.title('2D Scatter Plot of question Embeddings')
        plt.xlabel('Dimension 1')
        plt.ylabel('Dimension 2')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(eval_path, 'embedding_scatter_plot_q.png'))
        plt.close()
        
        # for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing records"):
        #     user_input = row['question']
        #     prompt = make_prompt(user_input, system_message)
        #     try:
        #         model_response = llm.generate(prompt, output_type=output_type)
        #         results.append({
        #             'question': user_input,
        #             'response': model_response['answer']
        #         })
        #     except Exception as e:
        #         print(f"Error processing record: {e}")
        #         continue
        
        # if project_name!=None:
        #     # Ensure the output directory exists.
        #     os.makedirs(os.path.join(Path(__file__).parent.parent,project_name,'experiment_results'), exist_ok=True)
        #     results_df = pd.DataFrame(results)
        #     results_df.to_csv(os.path.join(Path(__file__).parent.parent,project_name,'experiment_results', 'evaluation_results.csv'), index=False)
        #     print(f"Processed {len(results)} records. Results saved to evaluation_results.csv")
        # else:
        #     path_result = os.path.join('experiment_results')
        #     os.makedirs(path_result, exist_ok=True)
        #     results_df = pd.DataFrame(results)
        #     results_df.to_csv(os.path.join(path_result, 'evaluation_results.csv'), index=False)
        #     print(f"Processed {len(results)} records. Results saved to evaluation_results.csv")
            
        
        eval_answer_embedding = get_embeddings_from_strings(answers_list,project_name)
        generated_answer_embedding = get_embeddings_from_strings(answers_list,project_name)
        
        eval_answer_embedding_2d = reduce_dimensionality(eval_answer_embedding)
        generated_answer_embedding_2d = reduce_dimensionality(generated_answer_embedding)
        
        # Create a 2D scatter plot for each set of embeddings with different colors
        plt.figure(figsize=(10, 7))

        # Scatter plot for eval_question_embedding_2d
        plt.scatter(eval_answer_embedding_2d[:, 0], eval_answer_embedding_2d[:, 1],
                    color='r', label='Eval Answer Embedding', alpha=0.5)

        # # Scatter plot for train_question_embedding_2d
        # plt.scatter(generated_answer_embedding_2d[:, 0], generated_answer_embedding_2d[:, 1],
        #             color='g', label='Generated Answer  Embedding', alpha=0.5)

        plt.title('2D Scatter Plot of Answer Embeddings')
        plt.xlabel('Dimension 1')
        plt.ylabel('Dimension 2')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(eval_path, 'embedding_scatter_plot_a.png'))
        plt.close()
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process evaluation data using specified LLM model.')
    parser.add_argument('--model_id', type=str, required=True, help='Model ID for the LLM')
    parser.add_argument('--system_message', type=str, default=DEFAULT_SYSTEM_MESSAGE,
                        help='System message for the prompt. If not provided, a default message is used.')
    parser.add_argument('--project_name', type=str, required=False, help='Optional project name for saving results')
    parser.add_argument('--experiment_name', type=str, required=False, help='Optional experiment name for filtering data')
    args = parser.parse_args()
    process_eval_data(args.model_id, args.system_message,project_name=args.project_name, experiment_name=args.experiment_name)