import os
import getpass
import sys
import time
from uuid import uuid4
from pathlib import Path
from itertools import chain
from typing import Sequence

import click

import GPUtil
import psutil
import docker
from tabulate import tabulate
from collections import defaultdict
from palaestrai.experiment import ExperimentRun


@click.group()
def scheduler():
    pass


GPUtilFilter = ["serial", "display_mode", "display_active", "driver"]
TTYCheck = sys.stdin.isatty()
PALUser = getpass.getuser()
PALUid = os.getuid()
PALGid = os.stat(os.getcwd()).st_gid
Client = docker.from_env()
CWD = os.getcwd()


def get_experiments(experiment_paths: Sequence[Path]) -> list:
    experiment_paths = [Path(p) for p in experiment_paths]
    experiments = list(
        chain.from_iterable(
            p.rglob("*.y*ml") if p.is_dir() else [p] for p in experiment_paths
        )
    )
    invalid_experiments = []
    for i in range(len(experiments)):
        syntax_check = ExperimentRun.check_syntax(experiments[i])
        if not (syntax_check):
            click.echo(
                "Skipping the following file because it contains errors: {}".format(
                    experiments[i]
                )
            )
            invalid_experiments.append(experiments[i])
    for experiment in invalid_experiments:
        experiments.remove(experiment)
    if experiments:
        return experiments
    else:
        click.echo(
            "No valid experiments found. The scheduler will terminate now."
        )
        exit(1)


def build_palaestrai_image(branch="development"):
    try:
        click.echo(
            "Starting to build the docker-image, this may take some time."
        )
        response = Client.api.build(
            path="https://gitlab.com/arl2/palaestrai.git#" + branch,
            rm=True,
            decode=True,
            dockerfile="/containers/palaestrai.Dockerfile",
            tag="palaestrai/palaestrai",
        )
        for line in response:
            if list(line)[0] in ("stream", "error"):
                value = list(line.values())[0].strip()
                if value:
                    click.echo(value)
        click.echo("PalaestrAI docker-image succesfully build.")
        exit(0)
    except Exception as error:
        click.echo(
            "Tried to build docker-image from palaestrAI-repository. Procedure failed, the scheduler will terminate now."
        )
        click.echo(error)
        exit(1)


def pull_palaestrai_image():
    try:
        click.echo(
            "Starting to download the docker-image, this may take some time."
        )
        palaestrai_image = Client.images.pull(
            "registry.gitlab.com/arl2/palaestrai/development", "latest"
        )
        click.echo("PalaestrAI docker-image succefully downloaded.")
        palaestrai_image.tag("palaestrai/palaestrai", "latest")
        palaestrai_image.reload()
        for image_tag in palaestrai_image.tags[1:]:
            Client.images.remove(image_tag)
        exit(0)
    except Exception as error:
        click.echo(
            "Tried to download docker-image from palaestrAI-repository. Procedure failed, the scheduler will terminate now."
        )
        click.echo(error)
        exit(1)


def parse_gpu_choice(user_input: str):
    id_list = []
    for element in user_input.split(","):
        sections = [int(x) for x in element.split("-")]

        if len(sections) == 1:
            id_list.append(sections[0])
        else:
            for parts in range(min(sections), max(sections) + 1):
                id_list.append(parts)

    return id_list


def start_container(experiment, gpu, name, volumes_path, docker_image):
    exp = "palaestrai -c palaestrai.conf experiment-start  %s" % (experiment,)
    volumes = {volumes_path.name: {"bind": "/workspace", "mode": "rw"}}
    env = [
        "PALAESTRAI_USER=%s" % (PALUser),
        "PALAESTRAI_UID=%s" % (PALUid),
        "PALAESTRAI_GID=%s" % (PALGid),
        "PYTHONPATH=%s" % (sys.path),
    ]
    c = Client.containers.run(
        docker_image,
        exp,
        device_requests=[
            docker.types.DeviceRequest(
                driver="nvidia", device_ids=[gpu], capabilities=[["gpu"]]
            )
        ],
        volumes=volumes,
        detach=True,
        environment=env,
        name=name,
        network="arl_palaestrai",
    )
    return c


@scheduler.command()
@click.option(
    "--experiments",
    default=CWD,
    help="Path to your experiment(s). Default is current directory.",
)
@click.option(
    "--docker-volume",
    help="Name of the docker volume you want to utilize. If not provided, creates volume with random name.",
)
@click.option(
    "--docker-image",
    default="palaestrai/palaestrai",
    help="Name of your docker image you want to utilize. Default value palaestrai/palaestrai",
)
@click.option(
    "--memory-limit",
    default=35,
    type=int,
    help="Memory limit. Value in percent, the scheduler won't start new experiments when the available memory is below your chosen threshold. Default value 35",
)
@click.option(
    "--experiments-per-gpu",
    "-n",
    default=4,
    type=int,
    help="Parallel experiments per GPU. Default value 4",
)
@click.option(
    "--gpus",
    help="Explicitly choose the GPUs you want to utilize by their ID. If not called, all GPUs will be utilized by default",
)
@click.option(
    "--gpu-dialog",
    is_flag=True,
    help="Flag if you want to choose your GPUs through the built-in dialog",
)
@click.option(
    "--branch",
    default="development",
    type=str,
    help="Specifies the palaestrai branch that you want to build/download.",
)
@click.option(
    "--build-image",
    is_flag=True,
    help="Builds a full-stack palaestrAI docker-image from the palaestrAI repository",
)
@click.option(
    "--pull-image",
    is_flag=True,
    help="Downloads the full-stack palaestrAI docker-image from the palaestrAI repository",
)
@click.option(
    "--force-download",
    is_flag=True,
    help="Forces download of the full-stack palaestrAI docker-image from the palaestrAI repository. Note that this will delete your existing image.",
)
def scheduler_setup(
    experiments,
    docker_volume,
    docker_image,
    memory_limit,
    experiments_per_gpu,
    gpus,
    gpu_dialog,
    branch,
    build_image,
    pull_image,
    force_download,
):
    """Experiment Scheduler for Palaestrai."""

    if build_image:
        build_palaestrai_image(branch)

    if pull_image:
        pull_palaestrai_image()

    if force_download:
        try:
            click.echo("Removing local palaestrAI image.")
            Client.images.remove("palaestrai/palaestrai")
        except:
            click.echo(
                "Tried to remove local palaestrAI image, image not found."
            )
        pull_palaestrai_image()

    try:
        Client.images.get(docker_image)
    except:
        click.echo(
            "Could not find docker-image: %s To build the default image you can run 'palaestrai-scheduler --build-image'. To download a prebuilt image run 'palaestrai-scheduler --pull-image'. The scheduler will terminate now."
            % docker_image
        )
        exit(1)

    try:
        Client.networks.get("arl_palaestrai")
    except:
        Client.networks.create("arl_palaestrai", driver="bridge")

    try:
        gputil_list = GPUtil.getGPUs()
    except Exception as error:
        click.echo(
            "GPUtil could not load available GPUs. The scheduler will terminate now. %s"
            % error
        )
        exit(1)

    gpu_dict = defaultdict()
    i = 0
    for d in gputil_list:
        d_dict = vars(d)
        gpu_dict[i] = d_dict
        i += 1

    for i in range(len(gpu_dict)):
        gpu_dict[i]["active_experiments"] = 0

    gpu_tabulate = defaultdict(list)
    for gpu, values in gpu_dict.items():
        for key, value in values.items():
            gpu_tabulate[key].append(value)
    for key in GPUtilFilter:
        for i in range(len(gpu_dict)):
            gpu_dict[i].pop(key, None)
            gpu_tabulate.pop(key, None)

    if gpu_dialog and gpus:
        click.echo(
            "Please use only one GPU option, either --gpu-dialog or --gpus. The scheduler will terminate now."
        )
        exit(1)

    if gpu_dialog and TTYCheck:
        click.echo("Available GPU(s):\n")
        click.echo(tabulate(gpu_tabulate, headers="keys"))

        user_choice = click.prompt(
            "\nWhich GPU(s) do you want to utilize? (e.g. id 0 or 0-3, seperate the ids by a comma e.g. 2,5,7-12) "
        )
        gpu_choice = parse_gpu_choice(user_choice)

    elif gpus and not (gpu_dialog):
        gpu_choice = parse_gpu_choice(gpus)

    if gpus or gpu_dialog:
        available_ids = gpu_tabulate["id"]
        for i in gpu_choice:
            if i not in available_ids:
                click.echo("ID %d not found." % i)
                exit(1)

        for i in range(len(gpu_dict)):
            if i not in gpu_choice:
                gpu_dict.pop(i)

    if experiments_per_gpu < 0:
        click.echo(
            "Please provide a positive number for the value of parallel experiments per GPU."
        )
        exit(1)

    if 0 <= memory_limit <= 100:
        memory_threshold = memory_limit / 100
    else:
        click.echo("Please provide a memory-limit value between 0 and 100.")
        exit(1)

    experiments = experiments.split()
    new_experiments = get_experiments(experiments)
    gpu_containers = defaultdict(list)
    for gpu_id in gpu_dict:
        gpu_containers[gpu_id] = []

    while new_experiments:
        time.sleep(10)
        for gpu_id, d in gpu_containers.items():
            for container in d:
                container.reload()
                if container.status == "exited":
                    gpu_dict[gpu_id]["active_experiments"] -= 1
                    d.remove(container)

        for gpu_id in gpu_dict:
            while (
                new_experiments
                and gpu_dict[gpu_id]["active_experiments"]
                < experiments_per_gpu
            ):
                stats = psutil.virtual_memory()
                free = getattr(stats, "available") / getattr(stats, "total")
                if free > memory_threshold:
                    if docker_volume:
                        volume = docker_volume
                    else:
                        volume = Client.volumes.create()
                    e = new_experiments.pop()
                    c = start_container(
                        e,
                        gpu_dict[gpu_id]["uuid"],
                        "%s-%s" % (PALUser, uuid4()),
                        volume,
                        docker_image,
                    )
                    click.echo(
                        "Started new Experiment: %s on GPU: %d"
                        % (e, gpu_dict[gpu_id]["id"])
                    )
                    gpu_containers[gpu_id].append(c)
                    gpu_dict[gpu_id]["active_experiments"] += 1
                    time.sleep(60)


if __name__ == "__main__":
    scheduler_setup()
