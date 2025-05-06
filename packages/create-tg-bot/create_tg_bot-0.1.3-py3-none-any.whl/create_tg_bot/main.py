import subprocess
import click
import os

from create_tg_bot.utils.validators import validate_folder_name
from create_tg_bot.utils.setup_env import setup_env
from create_tg_bot.utils.folders import create_project_structure
from create_tg_bot.cli.database import get_db_url
from create_tg_bot.cli.tokens import get_tokens
from create_tg_bot.cli.env import use_env
from create_tg_bot.texts import (
    CREATE_TG_APP_DESCRIPTION,
    CREATE_TG_APP_SHORT_HELP,
    CREATE_TG_APP_EPILOG
)


@click.command(
    context_settings=dict(help_option_names=["--help", "-h"]),
    short_help=CREATE_TG_APP_SHORT_HELP,
    epilog=CREATE_TG_APP_EPILOG,
    help=CREATE_TG_APP_DESCRIPTION,
)
@click.option(
    "-d", "--debug",
    help="Activate debug mode.",
    is_flag=True
)
@click.argument("project_name")
@click.pass_context
def create_tg_bot(ctx, project_name, debug):
    project_path = os.path.join(os.getcwd(), project_name)
    validate_folder_name(ctx, project_path, project_name)

    project_path = os.path.join(os.getcwd(), project_name)
    validate_folder_name(ctx, project_path, project_name)

    token, token_dev = get_tokens(project_name, debug)

    db_url = get_db_url(project_name, debug)


    create_project_structure(
        project_name=project_name,
        project_path=project_path,
        token_dev=token_dev,
        db_url=db_url,
        token=token,
    )

    use_env(project_path, debug)

    try:
        subprocess.run(["git", "init"], cwd=project_path, check=True)
        click.echo("✅ Git repository initialized.")
    except Exception as e:
        click.echo(f"❌ Git initialization failed: {e}")

    setup_env(project_path, debug)

    click.echo(f"\n\n✅ Project '{project_name}' created successfully.")
    click.echo("👉 To run the project:")
    click.echo(f"   1. Navigate to the project directory:\n      cd {project_name}")
    click.echo("   2. Activate the virtual environment:")
    click.echo("      - On macOS/Linux: source .venv/bin/activate")
    click.echo("      - On Windows:     .\\.venv\\Scripts\\activate")
    click.echo("   3. Run the project:")
    click.echo("      - With Makefile:     make run\n")
    click.echo("      - Without Makefile:  make run\n")


def main():
    create_tg_bot()
