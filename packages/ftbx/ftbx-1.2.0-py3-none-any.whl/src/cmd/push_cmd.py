"""

    PROJECT: flex_toolbox
    FILENAME: push_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: push command functions
"""

import json
import logging
import os

from pandas import pandas
from rich.logging import RichHandler
from tqdm import tqdm
import typer


from src._encryption import encrypt_pwd
from src._environment import Environment
from src._objects import ObjectType, Objects, SubItems
from src.utils import FTBX_LOG_LEVELS, convert_to_native_type

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()],
)
logger = logging.getLogger(__name__)


def push_command_func(**kwargs) -> bool:
    """
    Action on push command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    if kwargs["from_"] == "default":
        kwargs["from_"] = Environment.get_default_environment_alias()

    # for src_environment use an offline one to allow deployment or upgrade folders
    src_environment = Environment(
        name=kwargs["from_"], url="mock", username="mock", password=encrypt_pwd("mock")
    )
    logger.debug(f"Source environment: '{src_environment.name}'. ")

    dest_environments = [Environment.from_env_file(environment=e) for e in kwargs["to"]]
    logger.debug(f"Destination environments: {[e.name for e in dest_environments]}. ")

    objects = []
    # load objects from local
    for object_name in kwargs["object_names"]:
        # to native type + define filters
        identifier = convert_to_native_type(string=object_name)
        if isinstance(identifier, int):
            filters = {"id": identifier}
        else:
            filters = {"name": identifier, "exactNameMatch": True}

        # load
        object_type = ObjectType.from_string(string=kwargs["object_type"])
        object = Objects(
            object_type=object_type,
            sub_items=SubItems.from_object_type(object_type=object_type),
            filters=filters,
            post_filters=[],
            mode="full",
            with_dependencies=kwargs["with_dependencies"],
        ).load_from(environment=src_environment)[0]
        objects.append(object)

    # push objects to envs
    for dst_env in tqdm(dest_environments, desc=f"Pushing {kwargs['object_type']}"):
        for object in objects:
            object.push_to(
                environment=dst_env,
                with_dependencies_from=(
                    src_environment if kwargs["with_dependencies"] else None
                ),
            )

    # --retry
    if (
        kwargs["retry"]
        and kwargs["object_type"] == ObjectType.JOBS.value
        and len(objects) == 1
        and len(dest_environments) == 1
    ):
        objects[0].retry(environment=dest_environments[0])

    # --listen
    if (
        kwargs["listen"]
        and kwargs["object_type"] == ObjectType.JOBS.value
        and len(objects) == 1
        and len(dest_environments) == 1
    ):
        status = objects[0].listen(environment=dest_environments[0])

        # offer to propagate changes to the actions
        if status == "Completed":
            typer.confirm(
                f"\nJob '{objects[0].name}' [id:{objects[0].id}] completed. Would you like to update the '{objects[0].name}' action?",
                abort=True,
            )
            action = Objects(
                object_type=ObjectType.ACTIONS,
                sub_items=["configuration"],
                filters={"name": objects[0].name, "exactNameMatch": True},
                mode="full",
            ).get_from(environment=dest_environments[0], log=False)[0]
            action.configuration = objects[0].configuration
            action.push_to(environment=dest_environments[0])
            logger.info(f"Action '{action.name}' has been updated successfully. ")

    # --push-to-failed-jobs
    if (
        kwargs["push_to_failed_jobs"]
        and kwargs["object_type"] == ObjectType.ACTIONS.value
        and len(objects) == 1
        and len(dest_environments) == 1
    ):

        failed_job_ids = []
        failed_jobs = []

        # from file
        if (
            isinstance(kwargs["push_to_failed_jobs"], str)
            and kwargs["push_to_failed_jobs"] != "all"
        ):
            filename = kwargs["push_to_failed_jobs"].lower()
            if any(filename.endswith(ext) for ext in [".csv", ".json"]):
                # csv
                if filename.endswith(".csv"):
                    df = pandas.read_csv(kwargs["push_to_failed_jobs"])
                    for id in df["id"]:
                        failed_job_ids.append(id)
                # json
                elif filename.endswith(".json"):
                    with open(kwargs["push_to_failed_jobs"], "r") as json_file:
                        instances = json.load(json_file)
                        for instance in instances:
                            failed_job_ids.append(instance.get("id"))
            else:
                raise NameError(
                    f"{kwargs['push_to_failed_jobs']} doesn't belong to the supported formats. Please use file with .json or .csv instead. "
                )

            # get objects
            logger.debug(f"Failed job ids: {failed_job_ids}")
            for failed_job_id in failed_job_ids:
                failed_jobs.extend(
                    Objects(
                        object_type=ObjectType.JOBS,
                        sub_items=SubItems.JOBS,
                        filters={
                            "status": "Failed",
                            "id": failed_job_id,
                        },
                        mode="full"
                    ).get_from(environment=dest_environments[0], log=False)
                )

        # from api
        else:
            failed_jobs = Objects(
                object_type=ObjectType.JOBS,
                sub_items=SubItems.JOBS,
                filters={
                    "status": "Failed",
                    "name": objects[0].name,
                    "exactNameMatch": True,
                },
                mode="full",
            ).get_from(environment=dest_environments[0], log=False)

        # push & retry
        for failed_job in tqdm(
            failed_jobs, desc=f"Updating and retrying failed {objects[0].name} jobs"
        ):
            failed_job.filters["id"] = failed_job.id
            failed_job.configuration = objects[0].configuration
            failed_job.push_to(environment=dest_environments[0])
            failed_job.retry(environment=dest_environments[0])

    logger.debug(
        f"Total HTTP requests: {sum([e.session.http_requests_count for e in dest_environments])}"
    )

    return True
