import configparser
import csv
import os
import sys
import traceback
from pathlib import Path

import yaml
from loguru import logger

from odoo_openupgrade_wizard.configuration_version_dependant import (
    get_base_module_folder,
    get_manifest_name,
    get_odoo_folder,
    get_odoo_run_command,
    get_server_wide_modules_upgrade,
    skip_addon_path,
)
from odoo_openupgrade_wizard.tools.tools_docker import (
    kill_container,
    run_container,
)
from odoo_openupgrade_wizard.tools.tools_postgres import get_postgres_container
from odoo_openupgrade_wizard.tools.tools_system import get_script_folder

DEFAULT_ODOO_HTTP_PORT = 8069


def get_repo_file_path(ctx, odoo_version: float) -> Path:
    """return the relative path of the repos.yml file
    of a given odoo version"""
    repo_file = False
    # Check if submodule path exists
    version_cfg = (
        ctx.obj["config"]["odoo_version_settings"][odoo_version] or {}
    )
    submodule_path = get_odoo_env_path(ctx, odoo_version) / "repo_submodule"

    if submodule_path.exists():
        repo_file = submodule_path / version_cfg["repo_file_path"]
        if repo_file.exists():
            return repo_file
        else:
            logger.warning(f"Unable to find the repo file {repo_file}.")
    repo_file = get_odoo_env_path(ctx, odoo_version) / Path("repos.yml")
    if not repo_file.exists():
        raise Exception(f"Unable to find the repo file {repo_file}.")
    return repo_file


def get_odoo_addons_path(
    ctx,
    odoo_env_path: Path,
    migration_step: dict,
    execution_context: str = False,
) -> str:
    """Return
    - addons_path: a list of Path of that contains odoo module
      for the current migration_step,
      based on the analysis of the repos.yml file
    - empty_addons_path: a list of Path of empty folders.
      (without any odoo module)"""
    repo_file = get_repo_file_path(ctx, migration_step["version"])
    base_module_folder = get_base_module_folder(migration_step)
    stream = open(repo_file, "r")
    data = yaml.safe_load(stream)
    data = data

    addons_path = []
    empty_addons_path = []
    odoo_folder = get_odoo_folder(migration_step, execution_context)
    for key in data.keys():
        path = Path(key)
        if str(path).endswith(odoo_folder):
            # Add two folder for odoo folder
            addons_path.append(path / Path("addons"))
            addons_path.append(
                path / Path(base_module_folder) / Path("addons")
            )
        elif skip_addon_path(migration_step, path):
            pass
        elif is_addons_path(ctx, odoo_env_path / path, migration_step):
            addons_path.append(path)
        else:
            empty_addons_path.append(path)

    return addons_path, empty_addons_path


def is_addons_path(ctx, path: Path, migration_step: dict):
    for folder in [x for x in path.iterdir() if x.is_dir()]:
        if (folder / "__init__.py").exists() and (
            folder / get_manifest_name(migration_step)
        ).exists():
            return True
    return False


def get_odoo_env_path(ctx, odoo_version: float) -> Path:
    folder_name = "env_%s" % str(odoo_version).rjust(4, "0")
    return ctx.obj["src_folder_path"] / folder_name


def get_docker_image_tag(ctx, odoo_version: float) -> str:
    """Return a docker image tag, based on project name and odoo version"""
    return "odoo-openupgrade-wizard-image__%s__%s" % (
        ctx.obj["config"]["project_name"],
        str(odoo_version).rjust(4, "0"),
    )


def get_docker_container_name(ctx, database: str, migration_step: dict) -> str:
    """Return a docker container name, based on project name, database name,
    odoo version and migration step"""
    return "oow-{project}-{database}-{version}-step-{step}".format(
        project=ctx.obj["config"]["project_name"],
        database=database,
        # FIXME: version should be a string, but it is a float
        version=str(migration_step["version"]).rjust(4, "0"),
        step=str(migration_step["name"]).rjust(2, "0"),
    )


def generate_odoo_command_options(
    ctx,
    migration_step: dict,
    execution_context: str,
    database: str,
    demo: bool = False,
    update: str = False,
    init: str = False,
    stop_after_init: bool = False,
) -> list:
    """
    Generate Odoo command options as a list of string to append to any command.
    """
    odoo_env_path = get_odoo_env_path(ctx, migration_step["version"])

    # Compute 'server_wide_modules'
    custom_odoo_config_file = odoo_env_path / "odoo.conf"
    parser = configparser.RawConfigParser()
    parser.read(custom_odoo_config_file)
    server_wide_modules = parser.get(
        "options", "server_wide_modules", fallback=[]
    )
    server_wide_modules += get_server_wide_modules_upgrade(
        migration_step, execution_context
    )

    # Compute 'addons_path'
    addons_path_list, empty_addons_path_list = get_odoo_addons_path(
        ctx, odoo_env_path, migration_step, execution_context
    )
    addons_path = ",".join(
        [str(Path("/odoo_env") / x) for x in addons_path_list]
    )
    for empty_addons_path in empty_addons_path_list:
        logger.info(
            "Skipping addons path"
            f" '{(odoo_env_path / empty_addons_path).resolve()}'"
            " because it doesn't contain any odoo module."
        )

    # Compute 'log_file'
    log_file_name = (
        f"{ctx.obj['log_prefix']}____{migration_step['complete_name']}.log"
    )
    log_file_docker_path = f"/env/log/{log_file_name}"

    # Build options string
    options = [
        "--config=/odoo_env/odoo.conf",
        "--data-dir=/env/filestore/",
        f"--addons-path={addons_path}",
        f"--logfile={log_file_docker_path}",
        "--db_host=db",
        "--db_port=5432",
        "--db_user=odoo",
        "--db_password=odoo",
        "--workers=0",
        f"{'--without-demo=all' if not demo else ''}",
        f"{'--load ' + ','.join(server_wide_modules) if server_wide_modules else ''}",  # noqa
        f"{'--database=' + database if database else ''}",
        f"{'--update ' + update if update else ''}",
        f"{'--init ' + init if init else ''}",
        f"{'--stop-after-init' if stop_after_init else ''}",
    ]

    # remove empty strings
    return [x for x in options if x]


def generate_odoo_command(
    ctx,
    migration_step: dict,
    execution_context: str,
    database: str,
    demo: bool = False,
    update: str = False,
    init: str = False,
    stop_after_init: bool = False,
    shell: bool = False,
) -> str:
    """
    Generate the full Odoo command using options from
    generate_odoo_command_options.
    """
    options = generate_odoo_command_options(
        ctx,
        migration_step,
        execution_context,
        database,
        demo,
        update,
        init,
        stop_after_init,
    )

    base_command = (
        Path("/odoo_env")
        / Path(get_odoo_folder(migration_step, execution_context))
        / Path(get_odoo_run_command(migration_step))
    )

    options_as_string = " ".join(options)
    if shell:
        return f"{base_command} shell {options_as_string}"
    else:
        return f"{base_command} {options_as_string}"


def run_odoo(
    ctx,
    migration_step: dict,
    detached_container: bool = False,
    database: str = False,
    update: str = False,
    init: str = False,
    stop_after_init: bool = False,
    shell: bool = False,
    demo: bool = False,
    execution_context: str = False,
    alternative_xml_rpc_port: int = False,
    links: dict = {},
    publish_ports: bool = False,
):
    # Ensure that Postgres container exist
    get_postgres_container(ctx)
    logger.info(
        "Launching Odoo Container (Version {version}) for {db_text}"
        " in {execution_context} mode. Demo Data is {demo_text}"
        " {stop_text} {init_text} {update_text}".format(
            version=migration_step["version"],
            db_text=database and "database '%s'" % database or "any databases",
            execution_context=execution_context
            or migration_step["execution_context"],
            demo_text=demo and "enabled" or "disabled",
            stop_text=stop_after_init and " (stop-after-init)" or "",
            init_text=init and " (Init : %s)" % init or "",
            update_text=update and " (Update : %s)" % update or "",
        )
    )

    command = generate_odoo_command(
        ctx,
        migration_step,
        execution_context,
        database,
        demo=demo,
        update=update,
        init=init,
        stop_after_init=stop_after_init,
        shell=shell,
    )

    return run_container_odoo(
        ctx,
        migration_step,
        command,
        detached_container=detached_container,
        database=database,
        execution_context=execution_context,
        alternative_xml_rpc_port=alternative_xml_rpc_port,
        links=links,
        publish_ports=publish_ports,
    )


def run_container_odoo(
    ctx,
    migration_step: dict,
    command: str,
    detached_container: bool = False,
    database: str = False,
    alternative_xml_rpc_port: int = False,
    execution_context: str = False,
    links: dict = {},
    publish_ports: bool = False,
):
    env_path = ctx.obj["env_folder_path"]
    odoo_env_path = get_odoo_env_path(ctx, migration_step["version"])

    host_xmlrpc_port = (
        alternative_xml_rpc_port
        and alternative_xml_rpc_port
        or ctx.obj["config"]["odoo_host_xmlrpc_port"]
    )

    links.update({ctx.obj["config"]["postgres_container_name"]: "db"})

    if publish_ports:
        ports = {host_xmlrpc_port: DEFAULT_ODOO_HTTP_PORT}
    else:
        ports = {}

    return run_container(
        get_docker_image_tag(ctx, migration_step["version"]),
        get_docker_container_name(ctx, database, migration_step),
        command=command,
        ports=ports,
        volumes={
            env_path: "/env/",
            odoo_env_path: "/odoo_env/",
        },
        links=links,
        detach=detached_container,
        auto_remove=True,
    )


def kill_odoo(ctx, database, migration_step: dict):
    kill_container(get_docker_container_name(ctx, database, migration_step))


def execute_click_odoo_python_files(
    ctx,
    database: str,
    migration_step: dict,
    python_files: list = [],
    execution_context: str = False,
):
    if not python_files:
        # Get post-migration python scripts to execute
        script_folder = get_script_folder(ctx, migration_step)
        python_files = [
            Path("scripts") / Path(migration_step["complete_name"]) / Path(f)
            for f in os.listdir(script_folder)
            if os.path.isfile(os.path.join(script_folder, f))
            and f[-3:] == ".py"
        ]
        python_files = sorted(python_files)

    base_command = generate_odoo_command(
        ctx,
        migration_step,
        execution_context,
        database,
        shell=True,
    )

    for python_file in python_files:
        command = f"/bin/bash -c 'cat /env/{python_file} | {base_command}'"
        try:
            logger.info(
                f"Step {migration_step['complete_name']}."
                f" Executing script {python_file} ..."
            )
            run_container_odoo(
                ctx,
                migration_step,
                command,
                detached_container=False,
                database=database,
            )

        except Exception as e:
            traceback.print_exc()
            logger.error(
                "An error occured. Exiting. %s\n%s"
                % (e, traceback.print_exception(*sys.exc_info()))
            )
            raise e
        finally:
            kill_odoo(ctx, database, migration_step)


def get_odoo_modules_from_csv(module_file_path: Path) -> list:
    logger.debug(f"Reading '{module_file_path}' file ...")
    module_names = []
    csvfile = open(module_file_path, "r")
    spamreader = csv.reader(csvfile, delimiter=",", quotechar='"')
    for row in spamreader:
        # Try to guess that a line is not correct
        if not row:
            continue
        if not row[0]:
            continue
        if " " in row[0]:
            continue
        if any([x.isupper() for x in row[0]]):
            continue
        module_names.append(row[0])
    return module_names
