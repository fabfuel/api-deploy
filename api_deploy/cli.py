import click

from api_deploy.client import ApiGatewayClient
from api_deploy.processors import ProcessManager
from api_deploy.schema import Schema

process_options = dict(
    base_uri='https://${stageVariables.host}',
    connection_id='${stageVariables.connectionId}',
    allow_headers=[
        'Content-Type',
        'Authorization',
        'x-datadog-origin',
        'x-datadog-sampling-priority',
        'x-datadog-parent-id',
        'x-datadog-trace-id'
    ],
)


@click.group()
@click.version_option(version='0.0.1', prog_name='api-deploy')
def api():  # pragma: no cover
    pass


@click.command('compile')
@click.argument('source_file')
@click.argument('target_file')
def compile_file(source_file, target_file):
    source_schema = Schema.from_file(source_file)
    target_schema = _compile(source_schema)
    target_schema.to_file(target_file)


@click.command()
@click.argument('api_id')
@click.argument('stage_name')
@click.argument('source_file')
@click.option('--region', required=False, help='AWS region (e.g. eu-central-1)')
@click.option('--access-key-id', required=False, help='AWS access key id')
@click.option('--secret-access-key', required=False, help='AWS secret access key')
@click.option('--profile', required=False, help='AWS configuration profile name')
@click.option('--account', required=False, help='Target AWS account id to deploy in')
@click.option('--assume-role', required=False, help='AWS Role to assume in target account')
def deploy(api_id, stage_name, source_file, region, access_key_id, secret_access_key, profile, account, assume_role):
    client = _get_client(access_key_id, secret_access_key, region, profile, account, assume_role)

    click.secho(f'Deploying API "{api_id}", stage "{stage_name}"\n')
    click.secho(f'Compiling OpenAPI file: "{source_file}"')

    source_schema = Schema.from_file(source_file)
    target_schema = _compile(source_schema)

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


def _compile(source_schema):
    manager = ProcessManager.default(**process_options)
    return manager.process(source_schema)


def _get_client(access_key_id, secret_access_key, region, profile, assume_account, assume_role):
    return ApiGatewayClient(access_key_id, secret_access_key, region, profile, None, assume_account, assume_role)


api.add_command(compile_file)
api.add_command(deploy)
