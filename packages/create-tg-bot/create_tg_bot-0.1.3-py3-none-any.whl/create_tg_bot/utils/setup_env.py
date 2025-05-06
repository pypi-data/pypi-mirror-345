import subprocess
import click
import sys
import os


def setup_env(project_path, debug):
    is_windows = sys.platform == "win32"
    venv_path = os.path.join(project_path, ".venv", "Scripts" if is_windows else "bin")
    python_path = os.path.join(venv_path, "python")
    pip_path = os.path.join(venv_path, "pip")

    makefile_path = os.path.join(project_path, "Makefile")
    use_makefile = os.path.exists(makefile_path)

    try:
        if use_makefile:
            subprocess.run(
                ["make", "install"],
                cwd=project_path,
                check=True,
                shell=is_windows
            )
            subprocess.run(
                ["make", "gen-migration"],
                cwd=project_path,
                check=True,
                shell=is_windows
            )
            subprocess.run(
                ["make", "migrate"],
                cwd=project_path,
                check=True,
                shell=is_windows
            )
        else:
            subprocess.run(
                [pip_path, "install", "-r", os.path.join(project_path, "requirements.txt")],
                check=True
            )
            subprocess.run(
                [python_path, "-m", "alembic", "revision", "--autogenerate", "-m", "init"],
                cwd=project_path,
                check=True
            )
            subprocess.run(
                [python_path, "-m", "alembic", "upgrade", "head"],
                cwd=project_path,
                check=True
            )
        click.echo("✅ Successfully installed.")
        click.echo("✅ Successfully migrated.")
    except Exception as e:
        click.echo(f"ERROR: Migration failed: {e}")
