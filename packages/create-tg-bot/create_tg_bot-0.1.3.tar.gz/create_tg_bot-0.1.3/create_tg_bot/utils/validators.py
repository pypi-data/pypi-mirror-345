import os
import re

import click

from create_tg_bot.constants import INVALID_FOLDER_NAME_CHARS_PATTERN


def validate_folder_name(ctx: click.Context, path: str, name: str) -> None:
    is_folder_name_invalid = re.search(INVALID_FOLDER_NAME_CHARS_PATTERN, name)
    is_folder_exist = os.path.exists(path)

    if is_folder_name_invalid:
        click.echo("ERROR: Invalid project name. Avoid characters: <>:\"/\\|?* and control characters.")
        ctx.exit(1)

    if is_folder_exist:
        click.echo(f"ERROR: A folder named '{name}' already exists.")
        ctx.exit(1)
