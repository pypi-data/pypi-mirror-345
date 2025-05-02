"""

    PROJECT: flex_toolbox
    FILENAME: init_cmd.py
    AUTHOR: David NAISSE
    DATE: December 15, 2023

    DESCRIPTION: init command functions
"""

import logging
import os
import platform

from rich.logging import RichHandler

from src.utils import FTBX_LOG_LEVELS, update_toolbox_resources

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def init_command_func():
    """
    Action on init command.
    """

    logger.debug(f"Entering {__name__}")

    # get os
    user_os = platform.system()
    logger.info(f"OS: {user_os.upper()}")

    # create dotfolder
    os.makedirs(os.path.join(os.path.expanduser("~"), ".ftbx"), exist_ok=True)
    logger.info(f"Directory '~/.ftbx' has been created successfully.")

    # fetch resources
    update_toolbox_resources()
