import argparse
from models.project.projectdb import ProjectDB
from models.analysis.analysis import ResultsAnalyzer
from pathlib import Path
import duckdb
from tabulate import tabulate
import os 

def list_experiments(db):
    """List all experiments and their stats"""
    exp_dir=os.path.join(Path(__file__).parent.parent,'local-db','experiments.parquet')
    experiments_path = Path(exp_dir)
    if not experiments_path.exists():
        print("No experiments database found.")
        return

    conn = duckdb.connect()
    query = """
    SELECT 
        experiment_name,
        created_at,
        description,
        status,
        total_results,
        valid_results,
        validity_rate,
        last_updated
    FROM read_parquet($1)
    ORDER BY created_at DESC
    """
    
    results = conn.execute(query, [str(experiments_path)]).df()
    
    if len(results) == 0:
        print("No experiments found.")
        return
        
    print("\nExperiments Summary:")
    print("=" * 100)
    print(tabulate(results, headers='keys', tablefmt='grid', showindex=False))

def show_experiment_details(db, experiment_name):
    """Show detailed information about a specific experiment"""
    exp_dir=os.path.join(Path(__file__).parent.parent,'local-db','experiments.parquet')
    experiments_path = Path(exp_dir)
    if not experiments_path.exists():
        print("No experiments database found.")
        return

    conn = duckdb.connect()
    query = f"""
    SELECT *
    FROM read_parquet('{experiments_path}')
    WHERE experiment_name = '{experiment_name}'
    """
    
    result = conn.execute(query).df()
    
    if len(result) == 0:
        print(f"No experiment found with name: {experiment_name}")
        return
        
    exp = result.iloc[0]
    
    print("\nExperiment Details:")
    print("=" * 100)
    print(f"Name: {exp['experiment_name']}")
    print(f"Created: {exp['created_at']}")
    print(f"Status: {exp['status']}")
    print(f"Description: {exp['description']}")
    print("\nParameters:")
    for k, v in exp['parameters'].items():
        print(f"  {k}: {v}")
    print("\nModel Configuration:")
    for k, v in exp['model_config'].items():
        print(f"  {k}: {v}")
    print("\nResults:")
    print(f"  Total Results: {exp['total_results']}")
    print(f"  Valid Results: {exp['valid_results']}")
    print(f"  Validity Rate: {exp['validity_rate']}%")
    print(f"Last Updated: {exp['last_updated']}")

def show_experiment_results(db, experiment_name, limit=None):
    """Show results from a specific experiment"""
    analyzer = ResultsAnalyzer(experiment_name)
    analyzer.print_results(limit=limit)

def main():
    parser = argparse.ArgumentParser(description="Generate ad-hoc reports from experiment database")
    parser.add_argument("--command", choices=["list", "details", "results"], 
                        help="Command to execute")
    parser.add_argument("-e", "--experiment_name", 
                        help="Experiment name for details or results")
    parser.add_argument("-n", "--num_results", type=int,
                        help="Number of results to show")
    
    args = parser.parse_args()
    
    db = ProjectDB()
    
    if args.command == "list":
        list_experiments(db)
    
    elif args.command == "details":
        if not args.experiment_name:
            print("Error: experiment_name is required for details command")
            return
        show_experiment_details(db, args.experiment_name)
    
    elif args.command == "results":
        if not args.experiment_name:
            print("Error: experiment_name is required for results command")
            return
        show_experiment_results(db, args.experiment_name, args.num_results)

if __name__ == "__main__":
    main()