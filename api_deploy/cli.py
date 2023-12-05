import click

from api_deploy import VERSION
from api_deploy.client import ApiGatewayClient
from api_deploy.config import Config
from api_deploy.converters import ProcessManager
from api_deploy.schema import Schema


@click.group()
@click.version_option(version=VERSION, prog_name='api-deploy')
def api():  # pragma: no cover
    pass


@click.command('compile')
@click.argument('config_file', type=click.Path(exists=True, resolve_path=True))
@click.argument('source_file', type=click.Path(exists=True))
@click.argument('target_file', type=click.Path(exists=False))
def compile_file(config_file, source_file, target_file):
    try:
        config = Config.from_file(config_file)
        source_schema = Schema.from_file(source_file)
        target_schema = _compile(source_schema, config)
        target_schema.to_file(target_file)
        click.secho(f'Successfully compiled OpenAPI file: {target_file}', fg='green')

    except Exception as e:
        click.secho('Failed to compile OpenAPI file.', fg='red')
        click.secho(str(e), fg='red')


@click.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('api_id')
@click.argument('stage_name')
@click.argument('source_file', type=click.Path(exists=True))
@click.option("--no-compile", is_flag=True, show_default=True, default=False, help="No compilation before deployment")
@click.option('--region', required=False, help='AWS region (e.g. eu-central-1)')
@click.option('--access-key-id', required=False, help='AWS access key id')
@click.option('--secret-access-key', required=False, help='AWS secret access key')
@click.option('--profile', required=False, help='AWS configuration profile name')
@click.option('--account', required=False, help='Target AWS account id to deploy in')
@click.option('--assume-role', required=False, help='AWS Role to assume in target account')
def deploy(config_file,
           api_id,
           stage_name,
           source_file,
           no_compile,
           region,
           access_key_id,
           secret_access_key,
           profile,
           account,
           assume_role,
           ):
    client = _get_client(access_key_id, secret_access_key, region, profile, account, assume_role)
    config = Config.from_file(config_file)
    source_schema = Schema.from_file(source_file)

    click.secho(f'Deploying API "{api_id}", stage "{stage_name}"\n')

    if no_compile:
        target_schema = source_schema
    else:
        click.secho(f'Compiling OpenAPI file: "{source_file}"')

        # Always remove scopes when deploying to Amazon API Gateway
        config['gateway']['remove_scopes'] = True

        target_schema = _compile(source_schema, config)
        click.secho('Successfully compiled OpenAPI file.\n', fg='green')

    click.secho(f'Importing OpenAPI file to API Gateway "{api_id}"')

    client.import_openapi(target_schema, api_id)

    click.secho('Successfully imported OpenAPI file.\n', fg='green')
    click.secho(f'Deploying API configuration to stage "{stage_name}"')

    client.deploy_to_stage(
        api_id,
        stage_name
    )

    click.secho('Successfully deployed API configuration.\n', fg='green')


def _compile(source_schema: Schema, config: Config):
    manager = ProcessManager.default(config)
    return manager.process(source_schema)


def _get_client(access_key_id, secret_access_key, region, profile, assume_account, assume_role):
    return ApiGatewayClient(access_key_id, secret_access_key, region, profile, None, assume_account, assume_role)


api.add_command(compile_file)
api.add_command(deploy)
