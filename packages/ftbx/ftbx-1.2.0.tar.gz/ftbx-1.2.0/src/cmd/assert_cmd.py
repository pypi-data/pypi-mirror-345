"""

    PROJECT: flex_toolbox
    FILENAME: assert_cmd.py
    AUTHOR: David NAISSE
    DATE: August 28th, 2024 

    DESCRIPTION: assert command functions
"""

import logging
import os

from rich.logging import RichHandler

from src._environment import Environment
from src._objects import ObjectType, Objects, SubItems
from src.utils import FTBX_LOG_LEVELS, convert_to_native_type

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def assert_command_func(**kwargs) -> bool:
    """
    Action on assert command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    environment = Environment.from_env_file(environment=kwargs["in_"])

    # to native type + define filters
    identifier = convert_to_native_type(string=kwargs["object_name_or_id"])
    if isinstance(identifier, int):
        filters = {"id": identifier}
    else:
        filters = {"name": identifier, "exactNameMatch": True}

    # get objects
    object_type = ObjectType.from_string(string=kwargs["object_type"])
    objects_request = Objects(
        object_type=object_type,
        sub_items=SubItems.from_object_type(object_type=object_type),
        filters=filters,
        post_filters=kwargs["assertions"],
        mode="full",
    )
    objects = objects_request.get_from(environment=environment, log=False)

    logger.debug(f"Total HTTP requests: {environment.session.http_requests_count}")

    if len(objects) == 1:
        print("True")
        return True
    else:
        print("False")
        return False
