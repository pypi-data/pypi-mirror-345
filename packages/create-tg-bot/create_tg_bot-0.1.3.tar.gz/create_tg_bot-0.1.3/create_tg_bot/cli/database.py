import click


def get_db_url(project_name, debug):
    db_type = click.prompt(
        "Select database",
        type=click.Choice(["sqlite", "postgres"], case_sensitive=False),
        default="sqlite"
    ).lower()

    if db_type == "postgres":
        db_host = click.prompt("PostgreSQL host", default="localhost")
        db_port = click.prompt("PostgreSQL port", default="5432")
        db_name = click.prompt("Database name", default="postgres")
        db_user = click.prompt("Database user")
        db_password = click.prompt("Database password", hide_input=True)

        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        db_url = f"sqlite:///{project_name}.db"

    if debug:
        click.echo(f"DEBUG > DB URL: {db_url}")

    return db_url
