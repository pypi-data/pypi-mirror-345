import click


def get_tokens(project_name, debug):
    token = click.prompt("Enter the production bot token")

    use_dev_bot = click.confirm("Do you want to use a separate bot for development?", default=False)
    token_dev = ""
    if use_dev_bot:
        token_dev = click.prompt("Enter the development bot token")

    if debug:
        click.echo(f"DEBUG > Project: {project_name}")
        click.echo(f"DEBUG > Prod token: {token[:5]}...")
        if use_dev_bot:
            click.echo(f"DEBUG > Dev token: {token_dev[:5]}...")

    return token, token_dev
