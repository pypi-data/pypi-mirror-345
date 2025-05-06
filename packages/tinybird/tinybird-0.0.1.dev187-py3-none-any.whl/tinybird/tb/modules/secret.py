import re
from typing import Optional

import click

from tinybird.tb.client import TinyB
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import coro, echo_safe_humanfriendly_tables_format_smart_table
from tinybird.tb.modules.feedback_manager import FeedbackManager


@cli.group()
@click.pass_context
def secret(ctx):
    """Secret commands."""


@secret.command(name="ls")
@click.option("--match", default=None, help="Retrieve any secrets matching the pattern. For example, --match _test")
@click.pass_context
@coro
async def secret_ls(ctx: click.Context, match: Optional[str]):
    """List secrets"""

    client: TinyB = ctx.ensure_object(dict)["client"]
    secrets = await client.secrets()
    columns = ["name", "created_at", "updated_at"]
    table_human_readable = []
    table_machine_readable = []
    pattern = re.compile(match) if match else None

    for secret in secrets:
        name = secret["name"]

        if pattern and not pattern.search(name):
            continue

        created_at = secret["created_at"]
        updated_at = secret["updated_at"]

        table_human_readable.append((name, created_at, updated_at))
        table_machine_readable.append({"name": name, "created at": created_at, "updated at": updated_at})

    click.echo(FeedbackManager.info(message="** Secrets:"))
    echo_safe_humanfriendly_tables_format_smart_table(table_human_readable, column_names=columns)
    click.echo("\n")


@secret.command(name="set")
@click.argument("name")
@click.argument("value", required=False)
@click.pass_context
@coro
async def secret_set(ctx: click.Context, name: str, value: Optional[str]):
    """Create or update secrets"""
    try:
        value = value or click.prompt("Enter value", hide_input=True)
        click.echo(FeedbackManager.highlight(message=f"\n» Setting secret '{name}'..."))

        client: TinyB = ctx.ensure_object(dict)["client"]
        existing_secret = None
        try:
            existing_secret = await client.get_secret(name)
        except Exception:
            pass

        if existing_secret:
            await client.update_secret(name, value)
        else:
            await client.create_secret(name, value)
        click.echo(FeedbackManager.success(message=f"\n✓ Secret '{name}' set"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"✗ Error: {e}"))


@secret.command(name="rm")
@click.argument("name")
@click.pass_context
@coro
async def secret_rm(ctx: click.Context, name: str):
    """Delete a secret"""
    try:
        click.echo(FeedbackManager.highlight(message=f"\n» Deleting secret '{name}'..."))
        client: TinyB = ctx.ensure_object(dict)["client"]
        await client.delete_secret(name)
        click.echo(FeedbackManager.success(message=f"\n✓ Secret '{name}' deleted"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"✗ Error: {e}"))
