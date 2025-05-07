from jinja2 import Environment, FileSystemLoader
import os
import click

def django_configuration(project_name, apps):


    os.chdir(project_name)
    settings_path = os.path.join(os.getcwd() ,'settings.py')

    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True)
    template = env.get_template('settings.py.j2')

    rendered = template.render(
        project_name=project_name,
        apps=apps,
    )

    with open(settings_path, 'w') as f:
        f.write(rendered)

    click.secho(' settings.py is configured.',fg='green')




    






