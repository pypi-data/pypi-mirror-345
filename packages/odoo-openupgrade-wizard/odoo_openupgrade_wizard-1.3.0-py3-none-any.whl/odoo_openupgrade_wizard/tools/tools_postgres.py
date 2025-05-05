import os
import shlex
import time
from pathlib import Path

import docker
from loguru import logger

from odoo_openupgrade_wizard.tools.tools_docker import (
    exec_container,
    get_docker_client,
    run_container,
)
from odoo_openupgrade_wizard.tools.tools_system import get_script_folder


def get_postgres_container(ctx):
    client = get_docker_client()
    image_name = ctx.obj["config"]["postgres_image_name"]
    container_name = ctx.obj["config"]["postgres_container_name"]
    volume_name = ctx.obj["config"]["postgres_volume_name"]

    # Check if container exists
    containers = client.containers.list(
        all=True,
        filters={"name": container_name},
        ignore_removed=True,
    )
    if containers:
        container = containers[0]
        if container.status == "exited":
            logger.warning(
                f"Found container {container_name} in a exited status."
                " Removing it..."
            )
            if container.status != "removed":
                container.remove()
            container.wait(condition="removed")
        else:
            return container

    # Check if volume exists
    try:
        client.volumes.get(volume_name)
        logger.debug(f"Recovering existing postgres volume: {volume_name}")
    except docker.errors.NotFound:
        logger.info(f"Creating Postgres volume: {volume_name}")
        client.volumes.create(volume_name)

    command = "postgres"
    postgres_extra_settings = ctx.obj["config"].get("postgres_extra_settings")
    if postgres_extra_settings:
        for key, value in postgres_extra_settings.items():
            command += f" -c {key}={value}"

    logger.info(f"Launching Postgres Container. (Image {image_name})")

    # base environement variables
    environments = {
        "POSTGRES_USER": "odoo",
        "POSTGRES_PASSWORD": "odoo",
        "POSTGRES_DB": "postgres",
        "PGDATA": "/var/lib/postgresql/data/pgdata",
    }

    # if postgresql version is >= 14 and odoo <= 12 we need to use md5 for auth
    # method and password encryption
    try:
        postgres_version = float(image_name.split(":")[1])
    except ValueError:
        raise Exception(
            "Unable to extract postgres version "
            f"from image name {image_name}. "
            "Define version in the image name is mandatory."
        )

    try:
        odoo_start_version = float(ctx.obj["config"]["odoo_versions"][0])
    except ValueError:
        raise Exception(
            "Unable to extract start odoo version from odoo_versions "
            f"{ctx.obj['config']['odoo_versions']}"
        )

    if odoo_start_version <= 12 and postgres_version >= 14:
        environments |= {
            "POSTGRES_HOST_AUTH_METHOD": "md5",
            "POSTGRES_INITDB_ARGS": "--auth-host=md5",
        }

        command += " -c password_encryption=md5"

    container = run_container(
        image_name,
        container_name,
        command=command,
        environments=environments,
        volumes={
            # Data volume
            volume_name: "/var/lib/postgresql/data/pgdata/",
            # main folder path (to pass files)
            ctx.obj["env_folder_path"].absolute(): "/env/",
        },
        detach=True,
    )
    # TODO, improve me.
    # Postgres container doesn't seems available immediately.
    # check in odoo container, i remember that there is
    # some script to do the job
    time.sleep(5)
    return container


def execute_sql_file(ctx, database, sql_file):
    container = get_postgres_container(ctx)

    # Recreate relative path to make posible to
    # call psql in the container
    if str(ctx.obj["env_folder_path"]) not in str(sql_file):
        raise Exception(
            f"The SQL file {sql_file} is not in the"
            f" main folder {ctx.obj['env_folder_path']} available"
            " in the postgres container."
        )
    relative_path = Path(
        str(sql_file).replace(str(ctx.obj["env_folder_path"]), ".")
    )

    container_path = Path("/env/") / relative_path
    command = (
        "psql --username=odoo --dbname={database} --file {file_path}"
    ).format(database=database, file_path=container_path)
    logger.info(
        f"Executing the script '{relative_path}' in postgres container"
        f" on database {database}"
    )
    exec_container(container, command)


def execute_sql_request(ctx, request, database="postgres"):
    psql_args = ("--tuples-only",)
    output = execute_psql_command(ctx, request, database, psql_args)
    lines = output.split("\n")
    result = []
    for line in lines:
        if not line:
            continue
        result.append([x.strip() for x in line.split("|")])
    return result


def execute_psql_command(
    ctx, request: str, database: str = None, psql_args: tuple = ()
):
    """Execute psql request in postgres container with psql_args on database"""
    container = get_postgres_container(ctx)
    command = (
        "psql"
        " --username=odoo"
        f" --dbname={database or 'postgres'}"
        f" --command {shlex.quote(request)}"
        f" {' '.join(psql_args)}"
    )
    logger.debug(
        f"Executing the following command in postgres container\n{command}"
    )
    docker_result = exec_container(container, command)
    return docker_result.output.decode("utf-8")


def check_db_exist(ctx, database: str, raise_exception=False):
    """
    - Connect to postgres container.
    - Check if the database exist.
    - Return True if exists, False otherwise.
    - raise_exception paramater used for source database checking
    """
    request = "select datname FROM pg_database WHERE datistemplate = false;"
    result = execute_sql_request(ctx, request)
    if [database] in result:
        return True
    if raise_exception:
        raise Exception(f"Database '{database}' not found.")
    return False


def ensure_database(ctx, database: str, state="present", template: str = ""):
    """
    - Connect to postgres container.
    - Check if the database exist.
    - if doesn't exists and state == 'present', create it.
    - if exists and state == 'absent', drop it.
    """
    if state == "present":
        if check_db_exist(ctx, database):
            return

        if template:
            logger.info(f'Copy database "{template}" into "{database}"...')
            request = (
                f'CREATE DATABASE "{database}" WITH TEMPLATE "{template}";'
            )
        else:
            logger.info(f"Create database '{database}'...")
            request = f'CREATE DATABASE "{database}" OWNER odoo;'
        execute_psql_command(ctx, request)

    else:
        if not check_db_exist(ctx, database):
            return

        logger.info(f'Drop database "{database}"...')
        request = f'DROP DATABASE "{database}";'
        execute_psql_command(ctx, request)


def execute_sql_files_pre_migration(
    ctx, database: str, migration_step: dict, sql_files: list = []
):
    ensure_database(ctx, database, state="present")
    if not sql_files:
        script_folder = get_script_folder(ctx, migration_step)
        sql_files = [
            script_folder / Path(f)
            for f in os.listdir(script_folder)
            if os.path.isfile(os.path.join(script_folder, f))
            and f[-4:] == ".sql"
        ]
        sql_files = sorted(sql_files)

    for sql_file in sql_files:
        execute_sql_file(ctx, database, sql_file)


def chown_to_local_user(ctx, filepath: os.PathLike):
    """Chown a filepath in the postgres container to the local user"""
    container = get_postgres_container(ctx)
    user_uid = os.getuid()
    command = "chown -R {uid}:{uid} {filepath}".format(
        uid=user_uid, filepath=filepath
    )
    logger.debug(
        f"Executing the following command in postgres container:\n{command}"
    )
    chown_result = exec_container(container, command)
    return chown_result.output.decode("utf8")


def execute_pg_dump(
    ctx,
    database: str,
    dumpformat: str,
    filename: str,
    pg_dump_args="--no-owner",
):
    """Execute pg_dump command on the postgres container and dump the
    result to dumpfile.
    """
    if pg_dump_args and not isinstance(pg_dump_args, str):
        pg_dump_args = " ".join(pg_dump_args)
    container = get_postgres_container(ctx)
    # Generate path for the output file
    filepath = Path("/env") / Path(filename)
    # Generate pg_dump command
    command = (
        "pg_dump"
        " --username=odoo"
        " --format {dumpformat}"
        " --file {filepath}"
        " {pg_dump_args}"
        " {database}"
    ).format(
        dumpformat=dumpformat,
        filepath=filepath,
        database=database,
        pg_dump_args=pg_dump_args,
    )
    logger.debug(
        f"Executing the following command in postgres container:\n{command}"
    )
    pg_dump_result = exec_container(container, command)

    chown_to_local_user(ctx, filepath)
    return pg_dump_result.output.decode("utf8")


def execute_pg_restore(
    ctx,
    filepath: Path,
    database: str,
    database_format: str,
):
    """Execute pg_restore command on the postgres container"""
    container = get_postgres_container(ctx)
    ensure_database(ctx, database, "absent")
    ensure_database(ctx, database, "present")
    if database_format == "p":
        command = (
            "psql"
            f" --file='{Path('/env') / filepath}'"
            " --username odoo"
            f" --dbname={database}"
        )
    else:
        command = (
            "pg_restore"
            f" {Path('/env') / filepath}"
            f" --dbname={database}"
            " --schema=public"
            " --username=odoo"
            " --no-owner"
            f" --format {database_format}"
        )
    logger.info(f"Restoring database '{database}'...")
    pg_dump_result = exec_container(container, command)
    return pg_dump_result.output.decode("utf8")
