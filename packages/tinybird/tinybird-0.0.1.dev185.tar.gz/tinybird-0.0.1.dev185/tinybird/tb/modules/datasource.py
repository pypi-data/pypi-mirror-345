# This is a command file for our CLI. Please keep it clean.
#
# - If it makes sense and only when strictly necessary, you can create utility functions in this file.
# - But please, **do not** interleave utility functions and command definitions.

import asyncio
import json
import os
import re
from typing import Optional

import click
import humanfriendly
from click import Context

from tinybird.tb.client import AuthNoTokenException, DoesNotExistException, TinyB
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import (
    _analyze,
    coro,
    echo_safe_humanfriendly_tables_format_smart_table,
    get_format_from_filename_or_url,
    load_connector_config,
    push_data,
)
from tinybird.tb.modules.datafile.common import get_name_version
from tinybird.tb.modules.datafile.fixture import persist_fixture
from tinybird.tb.modules.exceptions import CLIDatasourceException
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.project import Project


@cli.group()
@click.pass_context
def datasource(ctx):
    """Data source commands."""


@datasource.command(name="ls")
@click.option("--match", default=None, help="Retrieve any resources matching the pattern. For example, --match _test")
@click.option(
    "--format",
    "format_",
    type=click.Choice(["json"], case_sensitive=False),
    default=None,
    help="Force a type of the output",
)
@click.pass_context
@coro
async def datasource_ls(ctx: Context, match: Optional[str], format_: str):
    """List data sources"""

    client: TinyB = ctx.ensure_object(dict)["client"]
    ds = await client.datasources()
    columns = ["shared from", "name", "row_count", "size", "created at", "updated at", "connection"]
    table_human_readable = []
    table_machine_readable = []
    pattern = re.compile(match) if match else None

    for t in ds:
        stats = t.get("stats", None)
        if not stats:
            stats = t.get("statistics", {"bytes": ""})
            if not stats:
                stats = {"bytes": ""}

        tk = get_name_version(t["name"])
        if pattern and not pattern.search(tk["name"]):
            continue

        if "." in tk["name"]:
            shared_from, name = tk["name"].split(".")
        else:
            shared_from, name = "", tk["name"]

        table_human_readable.append(
            (
                shared_from,
                name,
                humanfriendly.format_number(stats.get("row_count")) if stats.get("row_count", None) else "-",
                humanfriendly.format_size(int(stats.get("bytes"))) if stats.get("bytes", None) else "-",
                t["created_at"][:-7],
                t["updated_at"][:-7],
                t.get("service", ""),
            )
        )
        table_machine_readable.append(
            {
                "shared from": shared_from,
                "name": name,
                "row_count": stats.get("row_count", None) or "-",
                "size": stats.get("bytes", None) or "-",
                "created at": t["created_at"][:-7],
                "updated at": t["updated_at"][:-7],
                "connection": t.get("service", ""),
            }
        )

    if not format_:
        click.echo(FeedbackManager.info_datasources())
        echo_safe_humanfriendly_tables_format_smart_table(table_human_readable, column_names=columns)
        click.echo("\n")
    elif format_ == "json":
        click.echo(json.dumps({"datasources": table_machine_readable}, indent=2))
    else:
        raise CLIDatasourceException(FeedbackManager.error_datasource_ls_type())


@datasource.command(name="append")
@click.argument("datasource_name", required=True)
@click.argument("url", nargs=-1, required=True)
@click.option("--concurrency", help="How many files to submit concurrently", default=1, hidden=True)
@click.pass_context
@coro
async def datasource_append(
    ctx: Context,
    datasource_name: str,
    url,
    concurrency: int,
):
    """
    Appends data to an existing data source from URL, local file  or a connector

    - Load from URL `tb datasource append [datasource_name] https://url_to_csv`

    - Load from local file `tb datasource append [datasource_name] /path/to/local/file`
    """

    client: TinyB = ctx.obj["client"]
    await push_data(
        client,
        datasource_name,
        url,
        mode="append",
        concurrency=concurrency,
    )


@datasource.command(name="replace")
@click.argument("datasource_name", required=True)
@click.argument("url", nargs=-1, required=True)
@click.option("--sql-condition", default=None, help="SQL WHERE condition to replace data", hidden=True)
@click.option("--skip-incompatible-partition-key", is_flag=True, default=False, hidden=True)
@click.pass_context
@coro
async def datasource_replace(
    ctx: Context,
    datasource_name,
    url,
    sql_condition,
    skip_incompatible_partition_key,
):
    """
    Replaces the data in a data source from a URL, local file or a connector

    - Replace from URL `tb datasource replace [datasource_name] https://url_to_csv --sql-condition "country='ES'"`

    - Replace from local file `tb datasource replace [datasource_name] /path/to/local/file --sql-condition "country='ES'"`
    """

    replace_options = set()
    if skip_incompatible_partition_key:
        replace_options.add("skip_incompatible_partition_key")
    client: TinyB = ctx.obj["client"]
    await push_data(
        client,
        datasource_name,
        url,
        mode="replace",
        sql_condition=sql_condition,
        replace_options=replace_options,
    )


@datasource.command(name="analyze")
@click.argument("url_or_file")
@click.option(
    "--connector",
    type=click.Choice(["bigquery", "snowflake"], case_sensitive=True),
    help="Use from one of the selected connectors. In this case pass a table name as a parameter instead of a file name or an URL",
    hidden=True,
)
@click.pass_context
@coro
async def datasource_analyze(ctx, url_or_file, connector):
    """Analyze a URL or a file before creating a new data source"""
    client = ctx.obj["client"]

    _connector = None
    if connector:
        load_connector_config(ctx, connector, False, check_uninstalled=False)
        if connector not in ctx.obj:
            raise CLIDatasourceException(FeedbackManager.error_connector_not_configured(connector=connector))
        else:
            _connector = ctx.obj[connector]

    def _table(title, columns, data):
        row_format = "{:<25}" * len(columns)
        click.echo(FeedbackManager.info_datasource_title(title=title))
        click.echo(FeedbackManager.info_datasource_row(row=row_format.format(*columns)))
        for t in data:
            click.echo(FeedbackManager.info_datasource_row(row=row_format.format(*[str(element) for element in t])))

    analysis, _ = await _analyze(
        url_or_file, client, format=get_format_from_filename_or_url(url_or_file), connector=_connector
    )

    columns = ("name", "type", "nullable")
    if "columns" in analysis["analysis"]:
        _table(
            "columns",
            columns,
            [
                (t["name"], t["recommended_type"], "false" if t["present_pct"] == 1 else "true")
                for t in analysis["analysis"]["columns"]
            ],
        )

    click.echo(FeedbackManager.info_datasource_title(title="SQL Schema"))
    click.echo(analysis["analysis"]["schema"])

    values = []

    if "dialect" in analysis:
        for x in analysis["dialect"].items():
            if x[1] == " ":
                values.append((x[0], '" "'))
            elif type(x[1]) == str and ("\n" in x[1] or "\r" in x[1]):  # noqa: E721
                values.append((x[0], x[1].replace("\n", "\\n").replace("\r", "\\r")))
            else:
                values.append(x)

        _table("dialect", ("name", "value"), values)


@datasource.command(name="truncate")
@click.argument("datasource_name", required=True)
@click.option("--yes", is_flag=True, default=False, help="Do not ask for confirmation")
@click.option(
    "--cascade", is_flag=True, default=False, help="Truncate dependent DS attached in cascade to the given DS"
)
@click.pass_context
@coro
async def datasource_truncate(ctx, datasource_name, yes, cascade):
    """Truncate a data source"""

    client = ctx.obj["client"]
    if yes or click.confirm(FeedbackManager.warning_confirm_truncate_datasource(datasource=datasource_name)):
        try:
            await client.datasource_truncate(datasource_name)
        except AuthNoTokenException:
            raise
        except DoesNotExistException:
            raise CLIDatasourceException(FeedbackManager.error_datasource_does_not_exist(datasource=datasource_name))
        except Exception as e:
            raise CLIDatasourceException(FeedbackManager.error_exception(error=e))

        click.echo(FeedbackManager.success_truncate_datasource(datasource=datasource_name))

        if cascade:
            try:
                ds_cascade_dependencies = await client.datasource_dependencies(
                    no_deps=False,
                    match=None,
                    pipe=None,
                    datasource=datasource_name,
                    check_for_partial_replace=True,
                    recursive=False,
                )
            except Exception as e:
                raise CLIDatasourceException(FeedbackManager.error_exception(error=e))

            cascade_dependent_ds = list(ds_cascade_dependencies.get("dependencies", {}).keys()) + list(
                ds_cascade_dependencies.get("incompatible_datasources", {}).keys()
            )
            for cascade_ds in cascade_dependent_ds:
                if yes or click.confirm(FeedbackManager.warning_confirm_truncate_datasource(datasource=cascade_ds)):
                    try:
                        await client.datasource_truncate(cascade_ds)
                    except DoesNotExistException:
                        raise CLIDatasourceException(
                            FeedbackManager.error_datasource_does_not_exist(datasource=datasource_name)
                        )
                    except Exception as e:
                        raise CLIDatasourceException(FeedbackManager.error_exception(error=e))
                    click.echo(FeedbackManager.success_truncate_datasource(datasource=cascade_ds))


@datasource.command(name="delete")
@click.argument("datasource_name")
@click.option("--sql-condition", default=None, help="SQL WHERE condition to remove rows", hidden=True, required=True)
@click.option("--yes", is_flag=True, default=False, help="Do not ask for confirmation")
@click.option("--wait", is_flag=True, default=False, help="Wait for delete job to finish, disabled by default")
@click.option("--dry-run", is_flag=True, default=False, help="Run the command without deleting anything")
@click.pass_context
@coro
async def datasource_delete_rows(ctx, datasource_name, sql_condition, yes, wait, dry_run):
    """
    Delete rows from a datasource

    - Delete rows with SQL condition: `tb datasource delete [datasource_name] --sql-condition "country='ES'"`

    - Delete rows with SQL condition and wait for the job to finish: `tb datasource delete [datasource_name] --sql-condition "country='ES'" --wait`
    """

    client: TinyB = ctx.ensure_object(dict)["client"]
    if (
        dry_run
        or yes
        or click.confirm(
            FeedbackManager.warning_confirm_delete_rows_datasource(
                datasource=datasource_name, delete_condition=sql_condition
            )
        )
    ):
        try:
            res = await client.datasource_delete_rows(datasource_name, sql_condition, dry_run)
            if dry_run:
                click.echo(
                    FeedbackManager.success_dry_run_delete_rows_datasource(
                        rows=res["rows_to_be_deleted"], datasource=datasource_name, delete_condition=sql_condition
                    )
                )
                return
            job_id = res["job_id"]
            job_url = res["job_url"]
            click.echo(FeedbackManager.info_datasource_delete_rows_job_url(url=job_url))
            if wait:
                progress_symbols = ["-", "\\", "|", "/"]
                progress_str = "Waiting for the job to finish"
                # TODO: Use click.echo instead of print and see if the behavior is the same
                print(f"\n{progress_str}", end="")  # noqa: T201

                def progress_line(n):
                    print(f"\r{progress_str} {progress_symbols[n % len(progress_symbols)]}", end="")  # noqa: T201

                i = 0
                while True:
                    try:
                        res = await client._req(f"v0/jobs/{job_id}")
                    except Exception:
                        raise CLIDatasourceException(FeedbackManager.error_job_status(url=job_url))
                    if res["status"] == "done":
                        print("\n")  # noqa: T201
                        click.echo(
                            FeedbackManager.success_delete_rows_datasource(
                                datasource=datasource_name, delete_condition=sql_condition
                            )
                        )
                        break
                    elif res["status"] == "error":
                        print("\n")  # noqa: T201
                        raise CLIDatasourceException(FeedbackManager.error_exception(error=res["error"]))
                    await asyncio.sleep(1)
                    i += 1
                    progress_line(i)

        except AuthNoTokenException:
            raise
        except DoesNotExistException:
            raise CLIDatasourceException(FeedbackManager.error_datasource_does_not_exist(datasource=datasource_name))
        except Exception as e:
            raise CLIDatasourceException(FeedbackManager.error_exception(error=e))


@datasource.command(
    name="data",
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True,
    ),
)
@click.argument("datasource")
@click.option("--limit", type=int, default=5, help="Limit the number of rows to return")
@click.pass_context
@coro
async def datasource_data(ctx: Context, datasource: str, limit: int):
    """Print data returned by an endpoint

    Syntax: tb datasource data <datasource_name>
    """

    client: TinyB = ctx.ensure_object(dict)["client"]
    try:
        res = await client.query(f"SELECT * FROM {datasource} LIMIT {limit} FORMAT JSON")
    except AuthNoTokenException:
        raise
    except Exception as e:
        raise CLIDatasourceException(FeedbackManager.error_exception(error=str(e)))

    if not res["data"]:
        click.echo(FeedbackManager.info_no_rows())
    else:
        echo_safe_humanfriendly_tables_format_smart_table(
            data=[d.values() for d in res["data"]], column_names=res["data"][0].keys()
        )


@datasource.command(name="export")
@click.argument("datasource")
@click.option(
    "--format",
    "format_",
    type=click.Choice(["csv", "ndjson"], case_sensitive=False),
    default="ndjson",
    help="Output format (csv or ndjson)",
)
@click.option("--rows", type=int, default=100, help="Number of rows to export (default: 100)")
@click.option("--where", type=str, default=None, help="Condition to filter data")
@click.option("--target", type=str, help="Target file path (default: datasource_name.{format})")
@click.pass_context
@coro
async def datasource_export(
    ctx: Context,
    datasource: str,
    format_: str,
    rows: int,
    where: Optional[str],
    target: Optional[str],
):
    """Export data from a datasource to a file in CSV or NDJSON format

    Example usage:
    - Export all rows as CSV: tb datasource export my_datasource
    - Export 1000 rows as NDJSON: tb datasource export my_datasource --format ndjson --rows 1000
    - Export to specific file: tb datasource export my_datasource --target ./data/export.csv
    """
    client: TinyB = ctx.ensure_object(dict)["client"]
    project: Project = ctx.ensure_object(dict)["project"]

    # Build query with optional row limit
    query = f"SELECT * FROM {datasource} WHERE {where or 1} LIMIT {rows}"

    click.echo(FeedbackManager.highlight(message=f"\n» Exporting {datasource}"))

    try:
        if format_ == "csv":
            query += " FORMAT CSVWithNames"
        else:
            query += " FORMAT JSONEachRow"

        res = await client.query(query)

        target_path = persist_fixture(datasource, res, project.folder, format=format_, target=target)
        file_size = os.path.getsize(target_path)

        click.echo(
            FeedbackManager.success(
                message=f"✓ Exported data to {str(target_path).replace(project.folder, '')} ({humanfriendly.format_size(file_size)})"
            )
        )

    except Exception as e:
        raise CLIDatasourceException(FeedbackManager.error(message=str(e)))


@datasource.command(name="sync")
@click.argument("datasource_name")
@click.option("--yes", is_flag=True, default=False, help="Do not ask for confirmation")
@click.pass_context
@coro
async def datasource_sync(ctx: Context, datasource_name: str, yes: bool):
    try:
        client: TinyB = ctx.obj["client"]
        ds = await client.get_datasource(datasource_name)

        warning_message = FeedbackManager.warning_datasource_sync_bucket(datasource=datasource_name)

        if yes or click.confirm(warning_message):
            await client.datasource_sync(ds["id"])
            click.echo(FeedbackManager.success_sync_datasource(datasource=datasource_name))
    except AuthNoTokenException:
        raise
    except Exception as e:
        raise CLIDatasourceException(FeedbackManager.error_syncing_datasource(datasource=datasource_name, error=str(e)))
