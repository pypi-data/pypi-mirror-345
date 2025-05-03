import pandas as pd
from pathlib import Path
from tabulate import tabulate
import argparse
import os 

def load_experiments(base_dir="./local-db"):
    """Load experiments from the database"""
    base_dir=os.path.join(Path(__file__).parent.parent,base_dir)
    experiments_path = Path(base_dir) / "experiments.parquet"
    if not experiments_path.exists():
        print("No experiments database found.")
        return None
    return pd.read_parquet(experiments_path)

def list_experiments(detailed=False):
    """List all experiments in a formatted table"""
    df = load_experiments()
    if df is None:
        return
    
    if detailed:
        # Show more columns for detailed view
        columns = ['experiment_id', 'experiment_name', 'created_at', 'status', 
                'total_results', 'valid_results', 'validity_rate', 'description']
    else:
        # Show fewer columns for simple view
        columns = ['experiment_id', 'experiment_name', 'status', 'validity_rate']
    
    print(tabulate(df[columns], headers='keys', tablefmt='psql', showindex=False))

def show_experiment(experiment_id):
    """Show detailed information about a specific experiment"""
    df = load_experiments()
    if df is None:
        return
    
    exp = df[df['experiment_id'] == experiment_id]
    if len(exp) == 0:
        print(f"No experiment found with ID: {experiment_id}")
        return
    
    exp = exp.iloc[0]
    print("\nExperiment Details:")
    print("=" * 50)
    print(f"ID: {exp['experiment_id']}")
    print(f"Name: {exp['experiment_name']}")
    print(f"Created: {exp['created_at']}")
    print(f"Status: {exp['status']}")
    print(f"Description: {exp['description']}")
    print("\nResults:")
    print(f"Total Results: {exp['total_results']}")
    print(f"Valid Results: {exp['valid_results']}")
    print(f"Validity Rate: {exp['validity_rate']}%")
    print("\nParameters:")
    for k, v in exp['parameters'].items():
        print(f"  {k}: {v}")
    print("\nModel Configuration:")
    for k, v in exp['model_config'].items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", choices=['list', 'show'])
    parser.add_argument("--detailed", "-d", action="store_true", help="Show detailed information")
    parser.add_argument("--id", help="Experiment ID for show command")
    args = parser.parse_args()
    
    if args.command == 'list':
        list_experiments(args.detailed)
    elif args.command == 'show':
        if not args.id:
            print("Error: --id is required for show command")
            exit(1)
        show_experiment(args.id) 