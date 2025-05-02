import os
import sys
path_add =os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if not path_add in sys.path:
    sys.path.append(path_add)
from utils.utils import generate_role_descriptions
from utils.utils import (
    write_roles_yml,
    read_roles_yml_to_dict,
    create_prompts_yml,
    generate_prompts_class_from_yml,
    generate_document_metadata
)
import logging

from lamini.experiment import BaseMemoryExperiment
from lamini.experiment.validators import BaseValidator
from lamini.experiment.generators import BaseGenerator
from lamini.experiment.generators import SaveGenerator

import yaml
from lamini.experiment.pipeline.base_agentic_pipeline import BaseAgenticPipeline
from pathlib import Path

def update_all_project_ymls(project_name, topic):

    project_dir = f'projects/{project_name}'
    roles = generate_role_descriptions(
        topic, os.getenv("LAMINI_API_KEY")
    )
    
    metadata = generate_document_metadata( topic, os.getenv("LAMINI_API_KEY"))
    with open(os.path.join('projects',project_name,'ymls','project.yml'), 'r') as file:
        project_file = yaml.safe_load(file)
    project_file['document_metadata']=metadata['document_metadata']
    
    with open(os.path.join('projects',project_name,'ymls','project.yml'), 'w') as file:
        yaml.dump(project_file, file)

    write_roles_yml(
        roles, output_path=f'{project_dir}/ymls/roles.yml', topic=topic
    )

    create_prompts_yml(
        focus_area=topic, output_path=f"{project_dir}/ymls/prompts.yml"
    )

    generate_prompts_class_from_yml(
        yml_path=f"{project_dir}/ymls/prompts.yml", output_path="models/project/prompts.py"
    )

def build_experiment_pipeline(ExperimentDefinition):
    project_dir = f'projects/{ExperimentDefinition["project_name"]}'

    proj_path = os.path.join(project_dir, "ymls", "project.yml")

    with open(proj_path, "r") as file:
        project_file = yaml.safe_load(file)

    if not os.path.exists(f"{project_dir}/ymls/roles.yml"):
        roles = generate_role_descriptions(
            project_file["Project"]["topic"], os.getenv("LAMINI_API_KEY")
        )
        write_roles_yml(
            roles, output_path=f'{project_dir}/ymls/roles.yml', topic=project_file["Project"]["topic"]
        )
    else:
        roles = read_roles_yml_to_dict(path=f"{project_dir}/ymls/roles.yml")

    if not os.path.exists(f"{project_dir}/ymls/prompts.yml"):
        create_prompts_yml(
            focus_area=project_file["Project"]["topic"], output_path=f"{project_dir}/ymls/prompts.yml"
        )
        logging.error(
            "Please define prompts at ymls-templates/prompts.yml. default prompts are added please feel free to modify as needed"
        )
        sys.exit(1)
    else:
        generate_prompts_class_from_yml(
            yml_path=f"{project_dir}/ymls/prompts.yml", output_path="models/project/prompts.py"
        )
        # keep this here so prompts are reloaded
        from models.project.prompts import Prompts

    # Create generators
    question_generator = BaseGenerator(
        model="meta-llama/Llama-3.1-8B-Instruct",
        name="question_generator",
        role=roles["question_generator"],
        output_type={"question": "str"},
        instruction=Prompts.QUESTION,
    )

    answer_generator = BaseGenerator(
        model="meta-llama/Llama-3.1-8B-Instruct",
        name="answer_generator",
        role=roles["answer_generator"],
        output_type={"answer": "str"},
        instruction=Prompts.ANSWER,
    )

    # Create validator
    validator = BaseValidator(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        name="fact_validator",
        output_type={"is_valid": "bool"},
        role=roles["validator"],
        instruction=Prompts.VALIDATOR,
        is_valid_field="is_valid",
    )

    # Create pipeline
    pipeline = BaseAgenticPipeline(
        generators={
            "question_generator": question_generator,
            "answer_generator": answer_generator,
        },
        validators={"FactValidator": validator},
        order=["question_generator", "answer_generator", "FactValidator"],
        record_dir=os.path.join(Path(__file__).parent.parent,'projects',ExperimentDefinition["project_name"],"experiment_results", ExperimentDefinition["experiment_name"]),
    )

    # Create experiment
    experiment = BaseMemoryExperiment(agentic_pipeline=pipeline)

    return {
        "question_generator": question_generator,
        "answer_generator": answer_generator,
        "validator": validator,
        "pipeline": pipeline,
        "experiment": experiment,
    }
