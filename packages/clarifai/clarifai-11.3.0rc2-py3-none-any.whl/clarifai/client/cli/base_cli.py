import click
import os
import yaml

@click.group()
@click.pass_context
def cli(ctx):
    """Clarifai CLI"""
    ctx.ensure_object(dict)
    config_path = 'config.yaml'
    if os.path.exists(config_path):
        ctx.obj = _from_yaml(config_path)
        print("Loaded config from file.")
        print(f"Config: {ctx.obj}")
    else:
        ctx.obj = {}

def _from_yaml(filename: str):
    try:
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        click.echo(f"Error reading YAML file: {e}", err=True)
        return {}

def _dump_yaml(data, filename: str):
    try:
        with open(filename, 'w') as f:
            yaml.dump(data, f)
    except Exception as e:
        click.echo(f"Error writing YAML file: {e}", err=True)

def _set_base_url(env):
    environments = {'prod': 'https://api.clarifai.com', 'staging': 'https://api-staging.clarifai.com', 'dev': 'https://api-dev.clarifai.com'}
    return environments.get(env, 'https://api.clarifai.com')


@cli.command()
@click.option('--config', type=click.Path(), required=False, help='Path to the config file')
@click.option('-e', '--env', required=False, help='Environment', type=click.Choice(['prod', 'staging', 'dev']))
@click.option('--user_id', required=False, help='User ID')
@click.pass_context
def login(ctx, config, env, user_id):
    """Login command to set PAT and other configurations."""

    if config and os.path.exists(config):
        ctx.obj = _from_yaml(config)
        
    if 'pat' in ctx.obj:
        os.environ["CLARIFAI_PAT"] = ctx.obj['pat']
        click.echo("Loaded PAT from config file.")
    elif 'CLARIFAI_PAT' in os.environ:
        ctx.obj['pat'] = os.environ["CLARIFAI_PAT"]
        click.echo("Loaded PAT from environment variable.")
    else:
        _pat = click.prompt("Get your PAT from https://clarifai.com/settings/security and pass it here", type=str)
        os.environ["CLARIFAI_PAT"] = _pat
        ctx.obj['pat'] = _pat
        click.echo("PAT saved successfully.")

    if user_id:
        ctx.obj['user_id'] = user_id
        os.environ["CLARIFAI_USER_ID"] = ctx.obj['user_id']
    elif 'user_id' in ctx.obj or 'CLARIFAI_USER_ID' in os.environ:
        ctx.obj['user_id'] = ctx.obj.get('user_id', os.environ["CLARIFAI_USER_ID"])
        os.environ["CLARIFAI_USER_ID"] = ctx.obj['user_id']

    if env:
        ctx.obj['env'] = env
        ctx.obj['base_url'] = _set_base_url(env)
        os.environ["CLARIFAI_API_BASE"] = ctx.obj['base_url']
    elif 'env' in ctx.obj:
        ctx.obj['env'] = ctx.obj.get('env', "prod")
        ctx.obj['base_url'] = _set_base_url(ctx.obj['env'])
        os.environ["CLARIFAI_API_BASE"] = ctx.obj['base_url']
    elif 'CLARIFAI_API_BASE' in os.environ:
        ctx.obj['base_url'] = os.environ["CLARIFAI_API_BASE"]
    
    _dump_yaml(ctx.obj, 'config.yaml')
    
    click.echo("Login successful.")

# Import the model CLI commands to register them
from clarifai.client.cli.model_cli import model  # Ensure this is the correct import path


if __name__ == '__main__':
    cli()
