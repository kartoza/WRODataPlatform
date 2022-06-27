import os
import click
import time
import sys
from pathlib import Path

from ckan.cli import CKANConfigLoader
from ckan.config.environment import load_environment
from ckan.plugins import toolkit

@click.group()
def cli():
    pass


@cli.command()
@click.option("-c","--ckan-ini", envvar="CKAN_INI")
def gunicorn_up(ckan_ini):
    click.secho(f"beginning of the process, establish ckan environment using configs from {ckan_ini} ...", fg="green")
    available = establish_ckan_env(ckan_ini)
    if available:
        click.secho("loading gunicorn configs", fg="green")
        sys.stderr.flush()
        sys.stdout.flush()
        # create the gunicorn params and run os.exec()
        gunicorn_params = [
            "gunicorn",
            "--chdir=/home/appuser/app/ckan/",
            "wsgi:application",
            "--bind=0.0.0.0:5000",
            "--preload"
            
        ]
        os.execvp("gunicorn", gunicorn_params)
    else:
        click.secho("couldn't establish ckan env", fg='red')

def establish_ckan_env(ckan_ini_path):
    try:
        Path(ckan_ini_path)
    except Exception:
        click.secho(f"ckan ini file doesn't exist in given path {ckan_ini_path}", fg="red")
        raise Exception
    # retry to load the ckan environment
    retries = 100
    pause = 2
    config_object = _get_config(ckan_ini_path)
    for i in range(1,retries+1):
        try:
             click.echo("loading the environment ... ")
             load_environment(config_object)
             click.secho("this is just for debugging:", fg="blue")
        except Exception:
            click.secho(f"problem while loading ckan environment, {i}/{retries} retries", fg="red")
            click.secho(f"retrying in {pause} seconds")
            if i == 25:
                raise Exception
            time.sleep(pause)
        else:
            return True
    
    else:
        return False


def _get_config(ckan_ini_path:str) -> dict:
    try:
        config = CKANConfigLoader(ckan_ini_path)
        return config.get_config()

    except Exception:
        click.secho(f"ckan config couldn't be loaded from path {ckan_ini_path}")
        raise Exception

if __name__ == "__main__":
    cli()