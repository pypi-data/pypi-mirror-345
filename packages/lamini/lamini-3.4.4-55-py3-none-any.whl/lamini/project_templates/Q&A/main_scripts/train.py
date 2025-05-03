
from pathlib import Path
import lamini
import random
import jsonlines
import yaml
import sys 
import os 
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from pathlib import Path
import logging 
from models.project.projectdb import ProjectDB
from models.analysis.analysis import ResultsAnalyzer
import argparse

def load_experiment_data(experiment_name: str, base_dir: str ="./local-db",project_name: str=None):
    """
    Load all QA pairs and validation results for a specific experiment
    
    Parameters
    ----------
    experiment_name : str
        Name of the experiment to load
    base_dir : str
        Base directory for the database files
        
    Returns
    -------
    pd.DataFrame
        DataFrame containing only valid QA pairs
    """
    base_dir=os.path.join(Path(__file__).parent.parent, base_dir)
    analyzer = ResultsAnalyzer(experiment_name, base_dir,project_name)
    # Get all QA pairs with their validity status
    df = analyzer.get_qa_pairs_with_validity()
    # Filter for only valid pairs
    df = df[df['is_valid'] == True]
    
    # Get summary stats
    total = len(df)
    print(f"\nLoaded {total} valid QA pairs from experiment '{experiment_name}'")
    
    return df

def format_train_data(df):
    """
    Format training data from DataFrame into prompts
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing conversation data
    
    Returns
    -------
    list
        List of formatted training examples with prompts and outputs
    """
    data = []
    for _, row in df.iterrows():
        prompt = make_prompt(row)
        data.append({
            "input": prompt,
            "output": row["answer"] + "<|eot_id|>"
        })
    return data

def main():
    parser = argparse.ArgumentParser(description='Load experiment results for training')
    parser.add_argument('-e', '--experiment_name', help='Name of the experiment to load')
    parser.add_argument('-p', '--project_name', help='Name of the experiment to load')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--lr', help="learning rate", default=1.0e-4, type=float)
    parser.add_argument('-ms','--max_steps', help="max steps for fine tuning", default=500, type=int)
    parser.add_argument('--base_model', default='meta-llama/Meta-Llama-3.1-8B-Instruct',
                    help='Base model to use for fine-tuning')
    parser.add_argument('--format', choices=['csv', 'parquet', 'json'], default='csv',
                    help='Output format (default: csv)')
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Check and prioritize command-line argument over config file
    experiment_name = args.experiment_name
    project_name = args.project_name
    
    if not experiment_name or not project_name:
        logging.error("Experimen/Project name must be specified.")
        sys.exit(1)
    
    try:

        # Load the experiment data
        df = load_experiment_data(experiment_name=experiment_name,project_name=project_name)        

        # Format the training data
        data = format_train_data(df)

        llm = lamini.Lamini(model_name=args.base_model)
        

        tuning_job = llm.tune(
            data_or_dataset_id=data,
            finetune_args={
                "max_steps": args.max_steps,
                "learning_rate": args.lr,
            },
            gpu_config={"gpus": 1, "nodes": 1},
        )
        db=ProjectDB()
        db.update_experiment_tuning_id(experiment_name=experiment_name,tuning_job_id= tuning_job['job_id'])
        # Print sample using ResultsAnalyzer's print_result method
        if not df.empty:
            print("\nSample QA pair:")
            sample = df.iloc[0]
            print(f"Question: {sample['question']}")
            print(f"Answer: {sample['answer']}")
            print(f"Valid: {sample['is_valid']}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

def print_data(data):
    print("\nTraining Data:")
    for i, item in enumerate(data, 1):
        print(f"\nEntry {i}:")
        print(f"Input: {item['input']}")
        print(f"Output: {item['output']}")
        print("-" * 80)


def make_prompt(item):
    prompt = "<|start_header_id|>user<|end_header_id|>"
    prompt += item["question"]
    prompt += "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"

    return prompt

if __name__ == "__main__":
    exit(main()) 