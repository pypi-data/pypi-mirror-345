import click

from odoo_openupgrade_wizard.cli.cli_options import database_option_required
from odoo_openupgrade_wizard.tools import (
    tools_click_odoo_contrib as click_odoo_contrib,
)


@click.command()
@database_option_required
@click.pass_context
def dropdb(ctx, database):
    """Delete a database and its filestore."""
    click_odoo_contrib.dropdb(ctx, database)
