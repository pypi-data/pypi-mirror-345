"""

    PROJECT: flex_toolbox
    FILENAME: connect_cmd.py
    AUTHOR: David NAISSE
    DATE: August 7th, 2024

    DESCRIPTION: connect command
"""

from rich.logging import RichHandler
from src._encryption import encrypt_pwd
from src._environment import Environment

from getpass import getpass
import logging
import os

from src.utils import FTBX_LOG_LEVELS

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def connect_command_func(**kwargs) -> bool:
    """
    Action on connect command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    # connect to existing env
    if kwargs["env_or_url"] and not any(
        arg for arg in [kwargs["username"], kwargs["password"], kwargs["alias"]]
    ):
        env = Environment.from_env_file(environment=kwargs["env_or_url"])
        env.connect()
        # save to force migration to newest ftbx version
        # will force 'version' field in environments
        env.save()
        env.set_default()

        return True

    # config/reconfig env
    elif all(arg for arg in [kwargs["env_or_url"], kwargs["username"]]):
        # remove trailing slash if needed
        if kwargs["env_or_url"].endswith("/"):
            kwargs["env_or_url"] = kwargs["env_or_url"][:-1]

        # create env object
        env = Environment(
            name=(
                kwargs["alias"]
                if kwargs["alias"]
                else kwargs["env_or_url"].replace("https://", "")
            ),
            url=kwargs["env_or_url"],
            username=kwargs["username"],
            password=(
                encrypt_pwd(kwargs["password"])
                if kwargs["password"]
                else encrypt_pwd(getpass(f"Password for [{kwargs['username']}]: "))
            ),
            version=kwargs["version"] if kwargs["version"] else "latest",
        )

        # try to connect
        can_connect = env.connect()

        # save and set default
        if can_connect:
            env.save()
            env.set_default()

        return True

    # unexpected
    else:
        logger.error(f"Unexpected scenario. Please contact FTBX admin. ")
        return False
