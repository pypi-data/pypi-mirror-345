"""

    PROJECT: flex_toolbox
    FILENAME: restore_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: restore command functions
"""

import logging
import os
import sys

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


def restore_command_func(**kwargs) -> bool:
    """
    Action on restore command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    environment = Environment.from_env_file(environment=kwargs['in_'])

    # to native type + define filters
    identifier = convert_to_native_type(string=kwargs['object_name'])
    if isinstance(identifier, int):
        filters = {"id": identifier}
    else:
        filters = {"name": identifier, "exactNameMatch": True}

    # load from local
    object_type = ObjectType.from_string(string=kwargs['object_type'])
    objects = Objects(
        object_type=object_type,
        sub_items=SubItems.from_object_type(object_type=object_type),
        filters=filters,
        mode="full",
    ).load_from(environment=environment, backup_name=kwargs['backup_name'])
    
    object = None
    if len(objects) == 0:
        logger.error(f"Cannot find backup with name '{kwargs['backup_name']}' for '{kwargs['object_type']}' with name '{kwargs['object_name']}'. ")
        sys.exit(1)
    else:
        object = objects[0]

    # restore
    object.push_to(environment=environment)

    logger.debug(f"Total HTTP requests: {environment.session.http_requests_count}")

    return True
