"""

    PROJECT: flex_toolbox
    FILENAME: workflow_designer_cmd.py
    AUTHOR: David NAISSE
    DATE: April 15th, 2024

    DESCRIPTION: workflow designer command functions
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


def workflow_designer_command_func(**kwargs):
    """
    Action on workflowDesigner command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    environment = Environment.from_env_file(environment=kwargs['in_'])

    # workflow request
    workflow_definition_request = Objects(
        object_type=ObjectType.WORKFLOW_DEFINITIONS,
        sub_items=SubItems.WORKFLOW_DEFINITIONS,
        filters={"name": kwargs['workflow_name'], "exactNameMatch": True},
        mode="partial"
    )
    workflow_definitions = workflow_definition_request.get_from(environment=environment)
    if len(workflow_definitions) != 1:
        raise ValueError(f"Couldn't find workflow definition with name {kwargs['workflow_name']} in remote {environment.name}.")

    workflow_definition = workflow_definitions[0]

    # define url
    url_parts = [
        "/".join(workflow_definition.href.split("/")[:3]),
        "/workflow/a/",
        workflow_definition.account.get("name"),
        "/edit?id=",
        str(workflow_definition.id),
    ]

    # join
    url = "".join(url_parts)
    logger.info(f"Opening '{url}' in your default web browser...")

    # open
    webbrowser.open_new_tab(url)
