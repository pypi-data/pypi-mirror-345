
import os
import subprocess
import sys
import  requests
import  click
from .write import django_configuration

VENV_NAME = 'venv'

def install_dependencies():
    click.secho('Installing dependencies in Virtual Environment.' ,fg='cyan')

    if is_connection():

        try:
            subprocess.run([venv_python(), '-m', 'pip', 'install', 'django'],check=True)
        except requests.ConnectionError:
            click.secho('"No internet connection. Cannot install dependencies."', fg='red')
        except subprocess.CalledProcessError as e:
            click.secho(f'Error -> {e}',  fg='red')
            exit()
        else:
             click.secho('Installed dependencies',fg='green')
    else:
        click.secho("No internet connection. Cannot install dependencies.",fg='red')
        exit()


def venv_creation() -> None:  # creating virtual environment


    if os.path.exists(VENV_NAME):
        click.secho('Virtual Environment already exists. Skipping creation.')
        install_dependencies()
        return

    click.secho('Creating Virtual Environment...',fg='cyan')
    try:
        subprocess.run(['python', '-m', 'venv', 'venv'], shell=True ,check=True)

    except Exception as e:
        click.secho(f'Error -> {e}', fg='red')
        exit()
    else:
        click.secho('Virtual Environment created.',fg='green')
        install_dependencies()


def is_connection():

    try :
        requests.get("https://pypi.org" ,timeout=5)
        return True
    except requests.ConnectionError:
        return False
    

def venv_python() -> str:

    if sys.platform == 'win32':
        venv_python = os.path.join(VENV_NAME, 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join('venv', 'bin', 'python')

    return venv_python


def static_files_creation():

    try:
        os.makedirs('templates',exist_ok=True)
        os.makedirs('static',exist_ok=True)
    except Exception as e:
        click.secho(f'Error -> {e}', fg='red')
    else:
        click.secho('Static directories created..',fg='green')

def root_creation(root):


    venv_creation()
    click.secho('Creating Django project..',fg='cyan')

    try:
        subprocess.run([venv_python(), '-m', 'django', 'startproject', root], shell=True, check=True)
        
    except subprocess.CalledProcessError as e:
        click.secho(f'Error -> {e}', fg='red')
        exit()

    else:
        click.secho("Django Project created successfully.",fg='green')
        


def app_creation(apps):

    venv_dir = os.path.join('..',venv_python())

    for app in apps:
        try:
            subprocess.run([venv_dir,'-m', 'django', 'startapp', app], shell=True,check=True)
            
        except subprocess.CalledProcessError as e:
            click.secho(f'Error ->{e}', fg='red')
            exit()
        else:
            click.secho(f'App -> {app} created successfully',fg='green')
    static_files_creation()

@click.command(
    context_settings=dict(help_option_names=['-h', '--help']),
)
@click.option('--root', type=str, required=False, prompt='root', help='Django project name (required).')
@click.option('--app',multiple=True, type=str, help='Django app name(s), can pass multiple (optional).')
def main(root, app):
    """
    Django Setup Tool

    This tool helps you quickly scaffold a Django project and optional apps.

    📌 Example:
        python script.py --root myproject --app app1 --app app2 

    Options:
        --root  Django project name (required)
        --app  One or more Django app names (optional)
    """

    if not root:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    project_dir = os.path.join(os.getcwd(),root)

    if not os.path.exists(project_dir):
        root_creation(root)

    if project_dir:
        try:
            os.chdir(project_dir)
        except Exception as e:
            click.secho(f'Error ->{e}',fg='red')
            return

        app_creation(app)
        django_configuration(root,app)

        

if __name__ == '__main__':
    main()




