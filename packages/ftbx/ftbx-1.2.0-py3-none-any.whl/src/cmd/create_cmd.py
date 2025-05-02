"""

    PROJECT: flex_toolbox
    FILENAME: create_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: create command functions
"""

import logging
import os

from rich.logging import RichHandler

from src._encryption import encrypt_pwd
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


def create_command_func(**kwargs):
    """
    Action on create command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    # templates is a mocked environment in ~/.ftbx/templates
    src_environment = Environment(
        name=os.path.join(os.path.expanduser("~"), ".ftbx", "templates"),
        url="mock",
        username="mock",
        password=encrypt_pwd("mock"),
    )
    dest_environment = Environment.from_env_file(environment=kwargs["in_"])

    # check existence of item in the environment
    object_type = ObjectType.from_string(string=kwargs["object_type"])
    objects_request = Objects(
        object_type=object_type,
        sub_items=SubItems.from_object_type(object_type=object_type),
        filters=(
            {"name": kwargs["object_name"], "exactNameMatch": True}
            if object_type != ObjectType.ACCOUNT_PROPERTIES
            else {}
        ),
        post_filters=(
            []
            if object_type != ObjectType.ACCOUNT_PROPERTIES
            else [f"key={kwargs['object_name']}"]
        ),
        mode="full",
        with_dependencies=True,
    )
    matching_objects = objects_request.get_from(environment=dest_environment, log=False)
    logger.info(f"Found {len(matching_objects)} matchs for the given parameters")

    # object doesn't exist in dest env
    if len(matching_objects) == 0:
        # load template
        objects_request.filters = {"name": kwargs["plugin"], "exactNameMatch": True}
        object = objects_request.load_from(environment=src_environment)[0]

        # configure template with new name
        # we reset filters for the load_from to find the object after creating it
        object.filters = {"name": kwargs["object_name"], "exactNameMatch": True}
        if object_type != ObjectType.ACCOUNT_PROPERTIES:
            object.name = kwargs["object_name"]
            object.displayName = kwargs["object_name"]
        else:
            object.key = kwargs["object_name"]
        # push
        object.push_to(environment=dest_environment)

        logger.debug(f"Total HTTP requests: {dest_environment.session.http_requests_count}")
    else:
        logger.error(
            f"Object '{object_type.value}' with name '{kwargs['object_name']}' already exists in '{dest_environment.name}'. "
        )
