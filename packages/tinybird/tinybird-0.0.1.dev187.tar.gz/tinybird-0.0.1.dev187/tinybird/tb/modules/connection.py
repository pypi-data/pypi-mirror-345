# This is a command file for our CLI. Please keep it clean.
#
# - If it makes sense and only when strictly necessary, you can create utility functions in this file.
# - But please, **do not** interleave utility functions and command definitions.

import uuid
from typing import Any, Dict, List, Optional

import click
from click import Context

from tinybird.tb.client import TinyB
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import (
    DataConnectorType,
    _get_setting_value,
    coro,
    echo_safe_humanfriendly_tables_format_smart_table,
    get_gcs_connection_name,
    get_gcs_svc_account_creds,
    get_s3_connection_name,
    production_aws_iamrole_only,
    run_aws_iamrole_connection_flow,
    run_gcp_svc_account_connection_flow,
)
from tinybird.tb.modules.create import (
    generate_aws_iamrole_connection_file_with_secret,
    generate_gcs_connection_file_with_secrets,
)
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.project import Project

DATA_CONNECTOR_SETTINGS: Dict[DataConnectorType, List[str]] = {
    DataConnectorType.KAFKA: [
        "kafka_bootstrap_servers",
        "kafka_sasl_plain_username",
        "kafka_sasl_plain_password",
        "cli_version",
        "endpoint",
        "kafka_security_protocol",
        "kafka_sasl_mechanism",
        "kafka_schema_registry_url",
        "kafka_ssl_ca_pem",
    ],
    DataConnectorType.GCLOUD_SCHEDULER: ["gcscheduler_region"],
    DataConnectorType.SNOWFLAKE: [
        "account",
        "username",
        "password",
        "role",
        "warehouse",
        "warehouse_size",
        "stage",
        "integration",
    ],
    DataConnectorType.BIGQUERY: ["account"],
    DataConnectorType.GCLOUD_STORAGE: [
        "gcs_private_key_id",
        "gcs_client_x509_cert_url",
        "gcs_project_id",
        "gcs_client_id",
        "gcs_client_email",
        "gcs_private_key",
    ],
    DataConnectorType.GCLOUD_STORAGE_HMAC: [
        "gcs_hmac_access_id",
        "gcs_hmac_secret",
    ],
    DataConnectorType.GCLOUD_STORAGE_SA: ["account_email"],
    DataConnectorType.AMAZON_S3: [
        "s3_access_key_id",
        "s3_secret_access_key",
        "s3_region",
    ],
    DataConnectorType.AMAZON_S3_IAMROLE: [
        "s3_iamrole_arn",
        "s3_iamrole_region",
        "s3_iamrole_external_id",
    ],
    DataConnectorType.AMAZON_DYNAMODB: [
        "dynamodb_iamrole_arn",
        "dynamodb_iamrole_region",
        "dynamodb_iamrole_external_id",
    ],
}

SENSITIVE_CONNECTOR_SETTINGS = {
    DataConnectorType.KAFKA: ["kafka_sasl_plain_password"],
    DataConnectorType.GCLOUD_SCHEDULER: [
        "gcscheduler_target_url",
        "gcscheduler_job_name",
        "gcscheduler_region",
    ],
    DataConnectorType.GCLOUD_STORAGE_HMAC: ["gcs_hmac_secret"],
    DataConnectorType.AMAZON_S3: ["s3_secret_access_key", "s3_secret"],
    DataConnectorType.AMAZON_S3_IAMROLE: ["s3_iamrole_arn"],
    DataConnectorType.AMAZON_DYNAMODB: ["dynamodb_iamrole_arn"],
}


@cli.group()
@click.pass_context
def connection(ctx: Context) -> None:
    """Connection commands."""


@connection.command(name="ls")
@click.option("--service", help="Filter by service")
@click.pass_context
@coro
async def connection_ls(ctx: Context, service: Optional[DataConnectorType] = None) -> None:
    """List connections."""
    obj: Dict[str, Any] = ctx.ensure_object(dict)
    client: TinyB = obj["client"]

    connections = await client.connections(connector=service, skip_bigquery=True)
    columns = []
    table = []

    click.echo(FeedbackManager.info_connections())

    if not service:
        sensitive_settings = []
        columns = ["service", "name", "id", "connected_datasources"]
    else:
        sensitive_settings = SENSITIVE_CONNECTOR_SETTINGS.get(service, [])
        columns = ["service", "name", "id", "connected_datasources"]
        if connector_settings := DATA_CONNECTOR_SETTINGS.get(service):
            columns += connector_settings

    for connection in connections:
        row = [_get_setting_value(connection, setting, sensitive_settings) for setting in columns]
        table.append(row)

    column_names = [c.replace("kafka_", "") for c in columns]
    echo_safe_humanfriendly_tables_format_smart_table(table, column_names=column_names)
    click.echo("\n")


@connection.group(name="create")
@click.pass_context
def connection_create(ctx: Context) -> None:
    """Create a connection."""


@connection_create.command(name="s3", short_help="Creates a AWS S3 connection.")
@click.pass_context
@coro
async def connection_create_s3(ctx: Context) -> None:
    """
    Creates a AWS S3 connection.

    \b
    $ tb connection create s3
    """
    project: Project = ctx.ensure_object(dict)["project"]
    obj: Dict[str, Any] = ctx.ensure_object(dict)
    client: TinyB = obj["client"]

    if obj["env"] == "local" and not await client.check_aws_credentials():
        click.echo(
            FeedbackManager.error(
                message="No AWS credentials found. Please run `tb local restart --use-aws-creds` to pass your credentials. "
                "Read more about this in https://www.tinybird.co/docs/forward/get-data-in/connectors/s3#local-environment"
            )
        )
        return

    service = DataConnectorType.AMAZON_S3
    click.echo(FeedbackManager.prompt_s3_connection_header())
    connection_name = get_s3_connection_name(project.folder)
    role_arn, region, bucket_name = await run_aws_iamrole_connection_flow(
        client,
        service=service,
        environment=obj["env"],
        connection_name=connection_name,
    )
    unique_suffix = uuid.uuid4().hex[:8]  # Use first 8 chars of a UUID for brevity
    secret_name = f"s3_role_arn_{connection_name}_{unique_suffix}"
    await client.create_secret(name=secret_name, value=role_arn)

    create_in_cloud = (
        click.confirm(FeedbackManager.prompt_connection_in_cloud_confirmation(), default=True)
        if obj["env"] == "local"
        else False
    )

    if create_in_cloud:
        prod_config = obj["config"]
        host = prod_config["host"]
        token = prod_config["token"]
        prod_client = TinyB(
            token=token,
            host=host,
            staging=False,
        )
        prod_role_arn, _, _ = await production_aws_iamrole_only(
            prod_client,
            service=service,
            region=region,
            bucket_name=bucket_name,
            environment="cloud",
            connection_name=connection_name,
        )
        await prod_client.create_secret(name=secret_name, value=prod_role_arn)

    connection_file_path = await generate_aws_iamrole_connection_file_with_secret(
        name=connection_name,
        service=service,
        role_arn_secret_name=secret_name,
        region=region,
        folder=project.folder,
    )

    click.echo(
        FeedbackManager.prompt_s3_iamrole_success(
            connection_name=connection_name,
            connection_path=str(connection_file_path),
        )
    )


@connection_create.command(name="gcs", short_help="Creates a Google Cloud Storage connection.")
@click.pass_context
@coro
async def connection_create_gcs(ctx: Context) -> None:
    """
    Creates a Google Cloud Storage connection.

    \b
    $ tb connection create gcs
    """
    project: Project = ctx.ensure_object(dict)["project"]
    obj: Dict[str, Any] = ctx.ensure_object(dict)
    client: TinyB = obj["client"]

    service = DataConnectorType.GCLOUD_STORAGE
    click.echo(FeedbackManager.prompt_gcs_connection_header())
    connection_name = get_gcs_connection_name(project.folder)
    _ = await run_gcp_svc_account_connection_flow(environment=obj["env"])
    creds_json = get_gcs_svc_account_creds()
    unique_suffix = uuid.uuid4().hex[:8]  # Use first 8 chars of a UUID for brevity
    secret_name = f"gcs_svc_account_creds_{connection_name}_{unique_suffix}"
    await client.create_secret(name=secret_name, value=creds_json)

    connection_path = await generate_gcs_connection_file_with_secrets(
        name=connection_name,
        service=service,
        svc_account_creds=secret_name,
        folder=project.folder,
    )

    create_in_cloud = (
        click.confirm(FeedbackManager.prompt_connection_in_cloud_confirmation(), default=True)
        if obj["env"] == "local"
        else False
    )

    if create_in_cloud:
        prod_config = obj["config"]
        host = prod_config["host"]
        token = prod_config["token"]
        prod_client = TinyB(
            token=token,
            host=host,
            staging=False,
        )
        creds_json = get_gcs_svc_account_creds()
        secret_name = f"gcs_svc_account_creds_{connection_name}_{unique_suffix}"
        await prod_client.create_secret(name=secret_name, value=creds_json)

    click.echo(
        FeedbackManager.prompt_gcs_success(
            connection_name=connection_name,
            connection_path=connection_path,
        )
    )
