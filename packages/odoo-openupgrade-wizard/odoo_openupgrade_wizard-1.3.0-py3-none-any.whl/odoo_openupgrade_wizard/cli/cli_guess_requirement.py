from pathlib import Path

import click

from odoo_openupgrade_wizard.tools.tools_odoo import (
    get_odoo_env_path,
    get_odoo_modules_from_csv,
)
from odoo_openupgrade_wizard.tools.tools_odoo_module import Analysis
from odoo_openupgrade_wizard.tools.tools_system import (
    ensure_file_exists_from_template,
)


@click.command()
@click.option(
    "--extra-modules",
    "extra_modules_list",
    # TODO, add a callback to check the quality of the argument
    help="Coma separated modules to analyse. If not set, the modules.csv"
    " file will be used to define the list of module to analyse."
    "Ex: 'account,product,base'",
)
@click.pass_context
def guess_requirement(ctx, extra_modules_list):
    # Analyse
    analysis = Analysis(ctx)

    if extra_modules_list:
        module_list = extra_modules_list.split(",")
    else:
        module_list = get_odoo_modules_from_csv(ctx.obj["module_file_path"])

    analysis.analyse_module_version(ctx, module_list)
    analysis.analyse_missing_module()
    result = analysis.get_requirements(ctx)

    for odoo_version in [x for x in ctx.obj["config"]["odoo_versions"]]:
        path_version = get_odoo_env_path(ctx, odoo_version)
        ensure_file_exists_from_template(
            path_version / Path("addons_python_requirements.txt"),
            "odoo/addons_python_requirements.txt.j2",
            dependencies=result[odoo_version]["python"],
        )

        ensure_file_exists_from_template(
            path_version / Path("addons_debian_requirements.txt"),
            "odoo/addons_debian_requirements.txt.j2",
            dependencies=result[odoo_version]["bin"],
        )
