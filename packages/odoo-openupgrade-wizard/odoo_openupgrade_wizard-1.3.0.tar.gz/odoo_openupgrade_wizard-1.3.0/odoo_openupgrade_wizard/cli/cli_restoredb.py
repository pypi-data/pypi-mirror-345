from pathlib import Path

import click

from odoo_openupgrade_wizard.cli.cli_options import database_option_required
from odoo_openupgrade_wizard.tools.tools_postgres import execute_pg_restore
from odoo_openupgrade_wizard.tools.tools_system import restore_filestore


@click.command()
@database_option_required
@click.option(
    "--database-path",
    required=True,
    type=click.Path(readable=True, resolve_path=True, exists=True),
    help="Path to the database dump relative project folder.",
)
@click.option(
    "--database-format",
    required=True,
    type=click.Choice(("c", "d", "t", "p")),
    default="c",
    help="Database format (see pg_dump options): "
    "custom format compressed (c), directory (d), tar file (t),"
    " plain sql text (p).",
)
@click.option(
    "--filestore-path",
    required=True,
    type=click.Path(readable=True, resolve_path=True, exists=True),
    help="Path to the filestore backup.",
)
@click.option(
    "--filestore-format",
    required=True,
    type=click.Choice(("d", "t", "tgz")),
    default="tgz",
    help="Filestore format: directory (d), tar file (t), "
    "tar file compressed with gzip (tgz)",
)
@click.pass_context
def restoredb(
    ctx,
    database,
    database_path,
    database_format,
    filestore_path,
    filestore_format,
):
    """Restore an Odoo database and associated filestore."""

    database_path = Path(database_path)
    filestore_path = Path(filestore_path)

    # Check that database_path is inside the env_folder_path
    absolute_env_folder_path = ctx.obj["env_folder_path"].resolve().absolute()
    if not str(database_path).startswith(str(absolute_env_folder_path)):
        ctx.fail(
            "database-path should be inside the project path to allow "
            "postgresql to read to it."
        )

    # Restore the database
    output = execute_pg_restore(
        ctx,
        database_path.relative_to(absolute_env_folder_path),
        database,
        database_format,
    )
    if output:
        click.echo(output)

    # Restore the filestore
    restore_filestore(
        ctx,
        database,
        filestore_path,
        filestore_format,
    )
