"""

    PROJECT: flex_toolbox
    FILENAME: env_cmd.py
    AUTHOR: David NAISSE
    DATE: August 7th, 2024 

    DESCRIPTION: environment file functions
"""

import logging
import os

import pandas as pd
from rich.logging import RichHandler

from src._environment import Environment
from src.utils import FTBX_LOG_LEVELS

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def env_command_func() -> bool:
    """
    Action on env command.
    """

    logger.debug(f"Entering {__name__}")
    
    # retrieve environments
    environments = Environment.read_environments_file().get('environments')
    assert environments, f"Environment file is empty. Please connect to an environment first using the 'ftbx connect' command. "
    default_environment = environments["default"]

    # configure dataframe
    pd.set_option("display.colheader_justify", "center")
    env_df = pd.DataFrame(columns=["DEFAULT", "ALIAS", "VERSION", "URL", "USERNAME"])
    environments.pop("default")

    for env_alias, env_config in environments.items():
        is_default = default_environment["url"] == env_config["url"] and default_environment["username"] == env_config["username"]

        env_df.loc[len(env_df)] = {
            "DEFAULT": "X" if is_default else "-",
            "ALIAS": env_alias,
            "VERSION": env_config.get("version") if 'version' in env_config else "latest",
            "URL": env_config.get("url"),
            "USERNAME": env_config.get("username"),
        }

    # display
    print(env_df.to_string(index=False))

    return True
