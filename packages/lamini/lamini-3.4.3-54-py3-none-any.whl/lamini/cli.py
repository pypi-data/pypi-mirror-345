import os
import shutil
import click
import lamini
from importlib import resources
import pathlib
import subprocess
import datetime

base_dir = os.path.dirname(lamini.__file__)


@click.group()
def cli():
    """CLI tool for scaffolding projects."""
    pass


@cli.command()
@click.argument("project_type")
@click.argument("workspace_name", required=False, default=None)
def create(project_type, workspace_name=None):
    """
    Create a new project based on the specified template.
    PROJECT_TYPE: Type of project (e.g., 'Q&A', 'text-to-sql')
    WORKSPACE_NAME: Name of the new workspace (optional; defaults to current timestamp if omitted)

    Options:

    - text-to-sql: Use agentic pipelines to generate synthetic data based on examples provided by the user to create a training dataset for text-to-sql. This option also enables the user to tune SLM models, perform inference, and evaluation.

    - Q&A: Use agentic pipelines to generate pairs of questions and answers from a source document, creating training data for tuning SLMs, inference, and evaluation.
    """
    if workspace_name is None:
        workspace_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        # Access template files from package data
        with resources.path("lamini.project_templates", project_type) as template_path:
            template_dir = pathlib.Path(template_path)
            if not template_dir.exists():
                click.echo(
                    f"Template for project type '{project_type}' does not exist."
                )
                return

            target_dir = os.path.join(os.getcwd(), workspace_name)
            if os.path.exists(target_dir):
                click.echo(f"Workspace '{workspace_name}' already exists.")
                return

            shutil.copytree(template_dir, target_dir)
            click.echo(
                f"Workspace '{workspace_name}' created successfully using the '{project_type}' template."
            )
    except ModuleNotFoundError:
        click.echo(f"Template for project type '{project_type}' does not exist.")
        return


@cli.command()
@click.argument("workspace_name", required=False, default=None)
@click.argument("args", nargs=-1)
def run(workspace_name, args):
    """
    Run the CLI app inside the specified workspace.
    WORKSPACE_NAME: Name of the workspace to run.
    Additional ARGS are forwarded to the CLI app.
    """
    if workspace_name is None:
        # Default to current directory as workspace
        workspace_name = os.path.basename(os.getcwd())
        target_dir = os.getcwd()
    else:
        target_dir = os.path.join(os.getcwd(), workspace_name)

    if not os.path.exists(target_dir):
        click.echo(f"Workspace '{workspace_name}' does not exist.")
        return
    script_path = os.path.join(target_dir, "cli-app.py")
    if not os.path.exists(script_path):
        click.echo(f"No 'cli-app.py' found in workspace '{workspace_name}'.")
        return
    result = subprocess.run(["python", script_path] + list(args))
    if result.returncode != 0:
        click.echo(f"'cli-app.py' exited with code {result.returncode}")
    return


if __name__ == "__main__":
    cli()
