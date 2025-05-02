"""

    PROJECT: flex_toolbox
    FILENAME: launch_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: Launch command functions
"""

import json
import logging
import os
import sys

from rich.logging import RichHandler
import typer

from src._environment import Environment
from src._objects import ObjectType, Objects, SubItems
from src.utils import FTBX_LOG_LEVELS

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()],
)
logger = logging.getLogger(__name__)


def launch_command_func(**kwargs) -> Objects:
    """
    Action on launch command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    environment = Environment.from_env_file(environment=kwargs["in_"])

    # check that config instance exists
    object_type = ObjectType.from_string(
        string="actions" if kwargs["object_type"] == "jobs" else "workflowDefinitions"
    )
    objects_request = Objects(
        object_type=object_type,
        sub_items=SubItems.from_object_type(object_type=object_type),
        filters={"name": kwargs["object_name"], "exactNameMatch": True},
    )
    matching_objects = objects_request.get_from(environment=environment)

    if not len(matching_objects) == 1:
        logger.error(
            f"Couldn't find any '{object_type.value}' object "
            + f"with name '{kwargs['object_name']}' in remote '{environment.name}'. "
        )
        sys.exit(1)

    # set main payload param
    payload = {}
    payload["actionId" if object_type.value == "actions" else "definitionId"] = (
        matching_objects[0].id
    )

    # arg params or file params
    if kwargs["from_file"] and not kwargs["params"]:
        # read params from json
        if ".json" in kwargs["from_file"]:
            with open(kwargs["from_file"]) as launch_config_file:
                tmp_payload = json.load(launch_config_file)
                # remove actionId and definitionId since we already have this info
                for key, value in tmp_payload.items():
                    if key != "actionId" and key != "definitionId":
                        payload[key] = value
        else:
            logger.error(
                f"File '{kwargs['from_file']}' is not supported. Please use a JSON file instead.\n"
            )
            sys.exit(1)

    # read params from args
    elif kwargs["params"] and not kwargs["from_file"]:
        for param in kwargs["params"]:
            key, value = param.split("=")[0], param.split("=")[1]
            # remove actionId and definitionId since we already have this info
            if key != "actionId" and key != "definitionId":
                payload[key] = value

    # handle --use-local
    if kwargs["use_local"]:
        matches = objects_request.load_from(environment=environment)
        if len(matches) != 1:
            logger.error(
                f"Cannot find any '{object_type.value}' with name '{kwargs['object_name']}' in local '{environment.name}'."
            )
            sys.exit(1)
        matches[0].push_to(environment=environment)

    # launch instance
    instance = environment.session.request(
        method="POST",
        url=f"{environment.url}/api/{kwargs['object_type']}",
        data=payload,
    )
    instance_object_type = ObjectType.from_string(string=kwargs["object_type"])
    instance_request = Objects(
        object_type=instance_object_type,
        sub_items=SubItems.from_object_type(object_type=instance_object_type),
        filters={"id": instance.get("id"), "name": instance.get("name")},
        mode="full",
        save_results=True,
    )
    instance = instance_request.get_from(environment=environment)[0]
    logger.info(
        f"Instance ID {instance.id} [{kwargs['object_type'][:-1]}]: '{instance.name}' has been launched successfully."
    )

    # --listen
    if kwargs["listen"] and object_type == ObjectType.ACTIONS:
        instance.listen(environment=environment)

    logger.debug(f"Total HTTP requests: {environment.session.http_requests_count}")

    return instance
