import click
import os

from create_tg_bot.templates import create_files_from_template_folder
from create_tg_bot.constants import ROOT_DIRS


def create_python_folder(folder_path):
    os.makedirs(folder_path)
    init_file_path = os.path.join(folder_path, "__init__.py")
    open(init_file_path, "w").close()
    click.echo(f"✅ Python folder {folder_path} created.")


def create_project_structure(project_name, project_path, token, token_dev, db_url):
    os.makedirs(project_path)
    for folder_name in ROOT_DIRS:
        folder_path = os.path.join(project_path, folder_name)
        create_python_folder(folder_path)

    create_files_from_template_folder(
        project_path,
        project_name=project_name,
        token_dev=token_dev,
        db_url=db_url,
        token=token
    )
