"""

    PROJECT: flex_toolbox
    FILENAME: pull_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: pull command functions
"""

import logging
import os

from rich.logging import RichHandler
from src._environment import Environment
from src._objects import ObjectType, Objects, SubItems
from src.utils import FTBX_LOG_LEVELS, convert_to_native_type, filters_to_dict

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()],
)
logger = logging.getLogger(__name__)


def pull_command_func(**kwargs) -> bool:
    """
    Action on pull command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    # object_name_or_id
    if kwargs["object_name_or_id"]:
        identifier = convert_to_native_type(string=kwargs["object_name_or_id"])
        if kwargs["object_type"] == "accountProperties":
            kwargs["post_filters"].append(f"key={kwargs['object_name_or_id']}")
        elif isinstance(identifier, int):
            kwargs["filters"].append(f"id={identifier}")
        else:
            kwargs["filters"].append(f"name={identifier}")
            kwargs["filters"].append(f"exactNameMatch=True")

    # add exactNameMatch=true when name is provided - removed temporarily?
    # if kwargs["filters"]:
    #    if any("name=" in f for f in kwargs["filters"]) and not any(
    #        "fql" in f for f in kwargs["filters"]
    #    ):
    #        kwargs["filters"].append("exactNameMatch=true")

    # multi-envs
    environments = [Environment.from_env_file(environment=e) for e in kwargs["from_"]]
    for environment in environments:
        # for pull all
        if kwargs["object_type"] == "all":
            for object_type in ObjectType:
                objects = Objects(
                    object_type=object_type,
                    sub_items=SubItems.from_object_type(object_type=object_type),
                    filters={},
                    post_filters=[],
                    mode="full",
                    with_dependencies=False,
                    save_results=True,
                )

                # no instances (assets, jobs, events...)
                if not objects.is_instance:
                    objects.get_from(environment=environment)
        else:
            # get objects
            object_type = ObjectType.from_string(string=kwargs["object_type"])
            objects = Objects(
                object_type=object_type,
                sub_items=SubItems.from_object_type(object_type=object_type),
                filters=filters_to_dict(filters=kwargs['filters']),
                post_filters=kwargs["post_filters"] if kwargs["post_filters"] else [],
                mode="full",
                with_dependencies=kwargs["with_dependencies"],
                save_results=True,
            )
            objects.get_from(environment=environment)

    logger.debug(f"Total HTTP requests: {sum([e.session.http_requests_count for e in environments])}")

    return True
