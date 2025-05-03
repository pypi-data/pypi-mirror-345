import os
from tqdm import tqdm
import argparse
import sys
import pandas as pd
import logging
from pathlib import Path

import yaml


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))


if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# from models.generators.table_description_generator import TableDescriptionGenerator
from lamini.experiment.generators.table_description_generator import TableDescriptionGenerator
from models.analysis.analysis import ResultsAnalyzer
from models.chunking.chunking import PDFSentenceChunker, SentenceChunker, PDFSemanticChunker
from models.project.projectdb import ProjectDB
from models.loaders.loader_mm import PDFSemanticLoader
from main_scripts.experiment_prep import build_experiment_pipeline
from models.loaders.loader import PDFLoader, DictLoader
from utils.utils import build_prompts_from_dataframe, save_chunks, save_results, filter_relevant_chunks, combine_relevant_chunks

from datetime import datetime
import uuid
from utils.utils import generate_question_chunks
# Suppress PyPDF warnings
logging.getLogger('pypdf').setLevel(logging.ERROR)


def main(args,config,project_dir,experiment_config):
    
    project_name=config['Project']['project_name']['value'] 
    mode = args["mode"]
    chunk_strategy=args['chunk_strategy']
    results_dir=os.path.join(Path(__file__).parent.parent,'projects',project_name,'experiment_results')
    data_dir = os.path.join(Path(__file__).parent.parent,'projects',project_name,'data')
    
    def generate_experiment_id():
        """Generate a unique experiment ID using timestamp and UUID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"
    
    
    def get_experiment_config(experiment_name, project_name, description,
                                product,keywords,title,data_description,
                                chunk_size=20,step_size=10,
                                breakpoint_percentile=95, window_size=1,
                                data_dir='data',results_dir='experiment_results', batches=1,
                                
                                ):
        experiment_id = generate_experiment_id()
        
        ExperimentDefinition = {
            "experiment_id": experiment_id, 
            "project_name": project_name,
            "description": description,
            "experiment_name": experiment_name,
            "results_dir": results_dir,
            "data_dir": data_dir,
            "batches": batches,
            "chunk_size": chunk_size,
            "step_size": step_size,
            "breakpoint_percentile":breakpoint_percentile,
            "window_size":window_size
            
        }

        additional_data = {
            "product": product,
            "keywords": keywords,
            "title": title,
            "description": data_description
        }

        return ExperimentDefinition, additional_data


    ExperimentDefinition, additional_data = get_experiment_config(
    experiment_name=args["experiment_name"],
    project_name=config['Project']['project_name']['value'],
    description=config['Project']['description']['value'],
    product=config['document_metadata']['product'],
    keywords=config['document_metadata']['keywords'],
    title=config['document_metadata']['title'],
    data_description=config['document_metadata']['description'],
    chunk_size=experiment_config['Experiment']['chunk_size']['value'],
    step_size=experiment_config['Experiment']['step_size']['value'],
    data_dir=data_dir,
    breakpoint_percentile=experiment_config['Experiment']['breakpoint_percentile']['value'], 
    window_size=experiment_config['Experiment']['window_size']['value'],
    results_dir=results_dir,
    batches=args.get("batches", 1),
    )
    

    experiment_id=generate_experiment_id()
    ExperimentDefinition['experiment_id']=experiment_id

    table_desc_gen = TableDescriptionGenerator(model=experiment_config['model']['default']['value'])
    
    if mode=='text':
        
        # First PDFLoader to get structured chunks
        pdf_loader = PDFLoader(
            PDFSentenceChunker(chunk_size=ExperimentDefinition["chunk_size"],
                                step_size=ExperimentDefinition["step_size"]),
                                ExperimentDefinition["data_dir"]
        )
    
        # Create a second PDFLoader to process the structured chunks
        second_loader = DictLoader(
            SentenceChunker(chunk_size=ExperimentDefinition["chunk_size"],
                            step_size=ExperimentDefinition["step_size"])
        )
        
        # Convert structured chunks into a format the loader can process
        structured_docs = [{**{k: v for k, v in chunk.items() if k != 'chunk_text'}, 
                        'content': chunk['chunk_text']} 
                        for chunk in pdf_loader.structured_chunks]
        # Process each structured chunk through the regular chunking process
        regular_chunks_from_structured = []
        for doc in structured_docs:
            for chunk in second_loader.get_chunks(doc):
                regular_chunks_from_structured.append(chunk)
        
        if chunk_strategy=='sentence':
            # Combine all chunks
            rich_chunks = pdf_loader.all_chunks
        elif chunk_strategy=='semantic':
            pdf_path = Path(ExperimentDefinition["data_dir"])
            semantic_chunker = PDFSemanticChunker(api_key=os.getenv('LAMINI_API_KEY'))
            rich_chunks=[]

            for pdf_file in os.listdir(pdf_path):
                if pdf_file.endswith('.pdf'):
                    rich_chunks.extend(semantic_chunker.chunk_pdf(os.path.join(pdf_path,pdf_file)))
                    
    elif mode=='multimodal':
        semantic_chunker = PDFSemanticChunker(
            api_key=config['Lamini']['api_key']['value'] ,
            embedding_model="text-embedding-3-small",
            window_size=ExperimentDefinition["window_size"],
            breakpoint_percentile=ExperimentDefinition["breakpoint_percentile"]
        )
        
        semantic_loader = PDFSemanticLoader(
            chunker=semantic_chunker,
            input_path=ExperimentDefinition["data_dir"],
            output_path=ExperimentDefinition["results_dir"],
            table_describer=table_desc_gen
        )
        
        # Get rich chunks from all ingested PDFs.
        rich_chunks= list(semantic_loader.load())
    else:
        return "Select correct mode"
    

    if args['chunk_filtering']==True:
        filtered = filter_relevant_chunks(
            topics=experiment_config['Experiment']['topics']['value'] ,
            chunks=rich_chunks,
            api_key=config['Lamini']['api_key']['value'] ,
            api_base_url=config['Lamini']['base_url_inf']['value'] ,
            model="text-embedding-3-small",
            threshold=experiment_config['Experiment']['threshold']['value'] ,
        )
        rich_chunks=filtered

    
    
    if args['combine_chunk']==True:
        new_chunks = combine_relevant_chunks(
                    rich_chunks,
                    api_key=config['Lamini']['api_key']['value'],
                    api_base_url=config['Lamini']['base_url_inf']['value'],
                    model="text-embedding-3-small",
                    batch_size=32,
                    similarity_threshold=experiment_config['Experiment']['combine_chunk']['similarity_threshold'],
                    )
        combined_chunks_count = len(rich_chunks) - len(new_chunks)
        print(f"Total number of combined chunks: {combined_chunks_count}")
        rich_chunks=new_chunks


    if not args.get("test_run"):
        chunks_path = save_chunks(rich_chunks, ExperimentDefinition["experiment_name"])
    
    # Assuming ExperimentDefinition, roles, and Prompts are already defined:
    pipeline_components = build_experiment_pipeline(ExperimentDefinition)
    from models.project.prompts import Prompts
    
    question_generator = pipeline_components["question_generator"]
    answer_generator = pipeline_components["answer_generator"]
    validator = pipeline_components["validator"]
    pipeline = pipeline_components["pipeline"]
    experiment = pipeline_components["experiment"]

    
    db = ProjectDB()
    q_prompt_id = db.create_prompt(name="question_generator",prompt_text=Prompts.QUESTION, type='generator')
    a_prompt_id = db.create_prompt(name="answer_generator",prompt_text=Prompts.ANSWER, type='generator')
    v_prompt_id = db.create_prompt(name="fact_validator",prompt_text=Prompts.VALIDATOR, type='validator')

    # Create input prompts from the chunks
    prompts = build_prompts_from_dataframe(
        pd.DataFrame(rich_chunks), 
        extract_columns=list(rich_chunks[0].keys()),
        #deprecated additional data, it is now handled by the document metadata in yml files
        additional_data=additional_data
    )
    
    if args['recursive_chunk']==True:
        prompts = generate_question_chunks(prompts, chunk_size= ExperimentDefinition["chunk_size"])

    # Limit number of prompts if specified
    if args.get("num_prompts"):
        prompts = prompts[:args["num_prompts"]]
        print(f"\nProcessing {len(prompts)} prompts...")

    # Handle potentially nested results and None values
    def flatten_results(results):
        flattened = []
        for result in results:
            if result is None:
                continue
            if isinstance(result, list):
                flattened.extend([r.data for r in result if r is not None])
            else:
                flattened.append(result.data)
        return flattened
    
    # Execute experiment
    results = experiment(prompts)
    # Convert results to DataFrame
    flattened_results = flatten_results(results)
    results_df = pd.DataFrame(flattened_results)
    results_df_dataset = results_df[["question_generator_output", "answer_generator_output", "FactValidator_output"]]
    qa_json_str = results_df_dataset.to_json(orient="records")
    dataset_id=db.create_dataset(name=f"dataset_{ExperimentDefinition["experiment_name"]}",description="Q&A set",qa_pairs=results_df_dataset)

    # Print results - all if -n specified, otherwise just a sample
    if args.get("num_prompts"):
        print("\nAll Results:")
        for result in flattened_results:
            ResultsAnalyzer.print_result(result)
    else:
        print("\nSample Result:")
        if flattened_results:
            ResultsAnalyzer.print_result(flattened_results[0])
    if not args.get("test_run"):
        # Initialize database
        db = ProjectDB()

        # Register experiment
        db.register_experiment(
            dataset_id=dataset_id,
            project_id=config['Project']['project_name']['value'] ,
            experiment_id=ExperimentDefinition["experiment_id"],
            experiment_name=ExperimentDefinition["experiment_name"],
            description=ExperimentDefinition["description"],
            parameters={
                "chunk_size": ExperimentDefinition["chunk_size"],
                "step_size": ExperimentDefinition["step_size"],
                "batches": ExperimentDefinition["batches"]
            },
            model_config={
                "question_generator": question_generator.model,
                "answer_generator": answer_generator.model,
                "validator": validator.model
            },
            generators=[
                {
                    "name": "question_generator",
                    "prompt": Prompts.QUESTION
                },
                {
                    "name": "answer_generator",
                    "prompt": Prompts.ANSWER
                }
            ],
            validators=[
                {
                    "name": "FactValidator",
                    "prompt": Prompts.VALIDATOR
                }
            ],
            chunk_ids=[chunk.get("chunk_id") for chunk in rich_chunks if "chunk_id" in chunk]
        )

        try:
            # Save results to central database
            results_path = save_results(results_df, ExperimentDefinition["experiment_name"])
        
            # Now that results are saved, we can analyze them
            analyzer = ResultsAnalyzer(experiment_name=ExperimentDefinition["experiment_name"],project_name=ExperimentDefinition["project_name"])

            # Print sample results from the database
            print("\nSample Results from Database:")
            analyzer.print_results(limit=3)

            # Get summary stats from the saved results
            total, valid, validity_rate = analyzer.get_summary_stats()

            print("\nExperiment Summary:")
            print("=" * 50)
            print(f"Experiment Name: {ExperimentDefinition['experiment_name']}")
            print(f"Total Q&A pairs: {total}")
            print(f"Valid pairs: {valid}")
            print(f"Validity rate: {validity_rate}%")

            # Mark experiment as completed
            db.complete_experiment(ExperimentDefinition["experiment_name"], status="completed")

        except Exception as e:
            print(f"Error during experiment execution: {str(e)}")
            # Mark experiment as failed if there was an error
            db.complete_experiment(ExperimentDefinition["experiment_name"], status="failed")
            raise e

    else:
        print("\nTest Run - Skipping database operations")
        print(f"Processed {len(results)} prompts")
        print("Sample results shown above") 
    # try:
    #     os.remove(os.path.join(Path(__file__).parent.parent.parent,'temp','temp.json'))
    # except:
    #     pass

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project_name", help="Project name")
    parser.add_argument("-e", "--experiment_name", help="Experiment name")
    parser.add_argument("-b", "--batches", type=int, default=1, help="Number of batches")
    parser.add_argument("-k", "--api_key", required=False, help="API key for Lamini")
    parser.add_argument("-n", "--num_prompts", type=int, help="Number of prompts to process (default: all)")
    parser.add_argument("-tr", "--test_run", action="store_true", help="Test run - skip database operations")
    parser.add_argument("-m", "--mode", choices=["multimodal", "text"], default="text",
                        help="Choose processing mode: multimodal or text (default: text)")
    parser.add_argument("-c", "--chunk_strategy", choices=["sentence", "semantic"], default="semantic",
                        help="Choose chunking strategy: sentence or semantic (default: sentence)")
    parser.add_argument("--recursive_chunk", action="store_true", help="Enable recursive chunking")
    parser.add_argument("--chunk_filtering", action="store_true", help="Enable filtering chunks according to topics")
    parser.add_argument("--combine_chunk", action="store_true", help="Enable combining of relevant chunks")


    args = vars(parser.parse_args())
    
    project_dir = f'projects/{args["project_name"]}'

    proj_path = f'{project_dir}/ymls/project.yml'
    
    with open(proj_path, 'r') as file:
        proj_config = yaml.safe_load(file)
    
    exp_path = f'{project_dir}/ymls/experiment.yml'
    
    with open(exp_path, 'r') as file:
        experiment_config = yaml.safe_load(file)
        
    # Only set LAMINI_API_KEY from config if it's not already set in the environment
    if 'LAMINI_API_KEY' not in os.environ:
        if proj_config['Lamini']['api_key']['value']  == '<your_api_key>':
            raise ValueError("API key is not set in the environment and is incorrect in config file")
        os.environ['LAMINI_API_KEY'] = proj_config['Lamini']['api_key']['value'] 
    
    api_url=proj_config['Lamini']['base_url']['value'] 


    if not args.get('api_key') and not os.environ.get('LAMINI_API_KEY'):
        logging.error("API key is missing. Please provide an API key using inside the confing.yml file")
    else:
        api_key = args.get('api_key') or os.environ.get('LAMINI_API_KEY')
        os.environ['OPENAI_API_KEY']=api_key


    main(args,proj_config,project_dir,experiment_config)
