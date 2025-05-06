from jinja2 import Environment, FileSystemLoader
import os.path
import click

templates_path = os.path.join(os.path.dirname(__file__))
env = Environment(loader=FileSystemLoader(templates_path))


def create_files_from_template_folder(project_path, **kwargs):

    files = os.listdir(templates_path)

    while files:
        template_path = files.pop()

        full_path = os.path.join(templates_path, template_path)

        if os.path.isdir(full_path):
            for item in os.listdir(full_path):
                item_rel = os.path.join(template_path, item)
                files.append(item_rel)

        elif os.path.isfile(full_path) and template_path.endswith(".jinja"):
            create_file_from_template(project_path, template_path, **kwargs)


def create_file_from_template(project_path, template_name, **kwargs):
    template = env.get_template(template_name)
    rendered = template.render(**kwargs)

    file_name = template_name.replace(".jinja", "")
    file_path = os.path.join(project_path, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    click.echo(f"✅ File {file_path} created.")
