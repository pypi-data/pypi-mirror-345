"""

    PROJECT: flex_toolbox
    FILENAME: metadata_designer_cmd.py
    AUTHOR: David NAISSE
    DATE: April 15th, 2024

    DESCRIPTION: metadata designer command functions
"""

import logging
import os
import webbrowser

from rich.logging import RichHandler

from src._environment import Environment
from src._objects import ObjectType, Objects, SubItems
from src.utils import FTBX_LOG_LEVELS

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def metadata_designer_command_func(**kwargs):
    """
    Action on metadataDesigner command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    environment = Environment.from_env_file(environment=kwargs['in_'])

    # workflow request
    metadata_definition_request = Objects(
        object_type=ObjectType.METADATA_DEFINITIONS,
        sub_items=SubItems.METADATA_DEFINITIONS,
    )
    metadata_definitions = metadata_definition_request.get_from(environment=environment, log=False)
    assert len(metadata_definitions) >= 1, logger.error(
        f"Couldn't find any metadata definition in remote '{environment.name}'. "
    )
    metadata_definition = metadata_definitions[0]

    # define url
    url_parts = [
        "/".join(metadata_definition.href.split("/")[:3]),
        "/metadata/a/",
        metadata_definition.account.get("name"),
        "#/home",
    ]

    # join
    url = "".join(url_parts)
    logger.info(f"Opening '{url}' in your default web browser...")

    # open
    webbrowser.open_new_tab(url)
