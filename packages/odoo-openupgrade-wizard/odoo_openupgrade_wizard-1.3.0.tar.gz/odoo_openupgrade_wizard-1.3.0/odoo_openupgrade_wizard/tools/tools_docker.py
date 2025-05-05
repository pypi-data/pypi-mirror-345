import time

import docker
from loguru import logger


def get_docker_client():
    return docker.from_env()


def pull_image(image_name):
    client = get_docker_client()
    client.images.pull(image_name)


def build_image(path, tag, buildargs={}):
    logger.debug(
        f"Building image named based on {path}/Dockerfile."
        " This can take a big while ..."
    )
    debug_docker_command = f"docker build {path} --tag {tag}"
    for arg_name, arg_value in buildargs.items():
        debug_docker_command += f"\\\n --build-arg {arg_name}={arg_value}"

    logger.debug(f"DOCKER COMMAND:\n\n{debug_docker_command}\n")
    docker_client = get_docker_client()

    try:
        image = docker_client.images.build(
            path=str(path),
            tag=tag,
            buildargs=buildargs,
        )
        logger.debug("Image build done.")
    except docker.errors.BuildError as buildError:
        logger.error("\n".join([str(log) for log in buildError.build_log]))
        logger.error("Image build failed.")
        raise buildError

    return image


def run_container(
    image_name,
    container_name,
    command=None,
    ports={},
    volumes={},
    environments={},
    links={},
    detach=False,
    auto_remove=False,
):
    client = get_docker_client()
    if not client.images.list(filters={"reference": image_name}):
        raise Exception(
            f"The image {image_name} is not available on your system."
            " Did you run 'odoo-openupgrade-wizard docker-build' ?"
        )

    logger.debug(f"Launching Docker container named {image_name} ...")
    debug_docker_command = f"docker run --name {container_name}\\\n"

    for k, v in ports.items():
        debug_docker_command += f" --publish {k}:{v}\\\n"
    for k, v in volumes.items():
        debug_docker_command += f" --volume {k}:{v}\\\n"
    for k, v in environments.items():
        debug_docker_command += f" --env {k}={v}\\\n"
    for k, v in links.items():
        debug_docker_command += f" --link {k}:{v}\\\n"
    if auto_remove:
        debug_docker_command += " --rm"
    if detach:
        debug_docker_command += " --detach"
    debug_docker_command += f" {image_name}"
    if command:
        debug_docker_command += f" \\\n{command}"
    logger.debug(f"DOCKER COMMAND:\n{debug_docker_command}")

    container = client.containers.run(
        image_name,
        name=container_name,
        command=command,
        ports={x: y for y, x in ports.items()},
        volumes=[str(k) + ":" + str(v) for k, v in volumes.items()],
        environment=environments,
        links=links,
        detach=detach,
        auto_remove=auto_remove,
    )
    if detach:
        logger.debug(f"Container {image_name} launched.")
    elif auto_remove:
        logger.debug("Container closed.")

    return container


def exec_container(container, command):
    debug_docker_command = f"docker exec {container.name}"
    debug_docker_command += f" \\\n{command}"
    logger.debug(f"DOCKER COMMAND:\n{debug_docker_command}")
    docker_result = container.exec_run(command)
    if docker_result.exit_code != 0:
        raise Exception(
            f"The command failed in the container {container.name}.\n"
            f"- Command : {command}\n"
            f"- Exit Code : {docker_result.exit_code}\n"
            f"- Output: {docker_result.output}"
        )
    return docker_result


def kill_container(container_name):
    # In some situation, containers.list return
    # containers with removal already in progress
    # when we call container.remove(), it is raising an
    # docker.errors.APIError
    # "removal of container xx is already in progress".
    # so, we retry a few seconds after
    # and raise an exception after five failures.
    for i in [1, 5, 10, 60, False]:
        try:
            _kill_container(container_name)
            return
        except docker.errors.APIError as e:
            if not i:
                logger.error(f"Fail to kill {container_name} after 5 retries")
                raise e
            logger.warning(
                f"Fail to kill {container_name}. Retrying in {i} seconds"
            )
            time.sleep(i)


def _kill_container(container_name):
    client = get_docker_client()

    try:
        containers = client.containers.list(
            all=True,
            filters={"name": container_name},
            ignore_removed=True,
        )
    except docker.errors.NotFound as err:
        logger.debug(f"Cannot kill container {container_name}: {err}")
        containers = []

    for container in containers:
        if container.status != "exited":
            logger.debug(
                "Stop container %s, based on image '%s'."
                % (container.name, ",".join(container.image.tags))
            )
            try:
                container.stop()
                container.wait()
                logger.debug(
                    "Container %s status is now '%s'."
                    % (container.name, container.status)
                )
                if container.status != "removed":
                    container.remove()
                container.wait(condition="removed")

            except docker.errors.NotFound as err:
                logger.debug(f"Cannot kill container {container.name}: {err}")
