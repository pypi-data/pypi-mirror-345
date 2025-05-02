"""

    PROJECT: flex_toolbox
    FILENAME: update_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: update command functions
"""

import logging
import subprocess
import os

from rich.logging import RichHandler

from src.utils import FTBX_LOG_LEVELS, update_toolbox_resources

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def update_command_func():
    """
    Action on update command.
    """

    logger.debug(f"Entering {__name__}")

    # fetch latest version
    subprocess.run(
        [
            "pipx",
            "upgrade",
            "ftbx",
            "--quiet"
        ],
        check=True,
    )

    # fetch updated resources
    update_toolbox_resources()
