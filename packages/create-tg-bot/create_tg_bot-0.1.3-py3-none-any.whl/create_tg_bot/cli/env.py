import os
import click


def use_env(project_path, debug):
    try:
        import venv as venv_module
        venv_path = os.path.join(project_path, ".venv")
        venv_module.create(venv_path, with_pip=True)
        if debug:
            click.echo(f"DEBUG > Virtual environment created at {venv_path}")
    except Exception as e:
        click.echo(f"ERROR: Failed to create virtual environment: {e}")

