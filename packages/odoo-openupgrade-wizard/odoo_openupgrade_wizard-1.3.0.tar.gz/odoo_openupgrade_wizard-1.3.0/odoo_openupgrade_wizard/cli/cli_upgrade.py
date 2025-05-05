import click
from loguru import logger

from odoo_openupgrade_wizard.cli.cli_options import (
    database_option_required,
    demo_option,
    first_step_option,
    get_migration_steps_from_options,
    last_step_option,
)
from odoo_openupgrade_wizard.tools.tools_odoo import (
    execute_click_odoo_python_files,
    kill_odoo,
    run_odoo,
)
from odoo_openupgrade_wizard.tools.tools_postgres import (
    execute_sql_files_pre_migration,
)


@click.command()
@first_step_option
@last_step_option
@database_option_required
@demo_option
@click.pass_context
def upgrade(ctx, first_step, last_step, database, with_demo):
    migration_steps = get_migration_steps_from_options(
        ctx, first_step, last_step
    )
    for migration_step in migration_steps:
        execute_sql_files_pre_migration(ctx, database, migration_step)
        if migration_step.get("update", True):
            try:
                run_odoo(
                    ctx,
                    migration_step,
                    database=database,
                    detached_container=False,
                    update="all",
                    stop_after_init=True,
                    demo=with_demo,
                )
            except (KeyboardInterrupt, SystemExit):
                logger.info("Received Keyboard Interrupt or System Exiting...")
            finally:
                kill_odoo(ctx, database, migration_step)
        elif migration_step.get("execution_context") == "openupgrade":
            raise ValueError(
                "Incorrect setting 'update: True'"
                " and 'execution_context: openupgrade'"
            )
        else:
            logger.info(
                "Skip update=all for"
                f" step {migration_step.get('complete_name')}"
            )

        execute_click_odoo_python_files(ctx, database, migration_step)
