"""

    PROJECT: flex_toolbox
    FILENAME: query_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: query command functions
"""

import json
import logging
import os

from rich.logging import RichHandler

from src._environment import Environment
from src.utils import FTBX_LOG_LEVELS, convert_to_native_type

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def query_command_func(**kwargs) -> bool:
    """
    Action on query command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    # get environment
    env = Environment.from_env_file(environment=kwargs['from_'])

    # get payload if needed
    if kwargs['payload']:
        # file
        if len(kwargs['payload']) == 1 and ".json" in kwargs['payload'][0]:
            with open(kwargs['payload'][0], "r") as payload_file:
                payload = json.load(payload_file)
        # command line args
        else:
            payload = dict()
            for param in kwargs['payload']:
                key, value = param.split("=")[0], param.split("=")[1]
                payload[key] = convert_to_native_type(value)
    else:
        payload = None

    # format url based on input
    if "api" in kwargs['url']:
        url = f"{env.url}/{kwargs['url']}"
    else:
        url = f"{env.url}/api/{kwargs['url']}"

    if not kwargs['stdout']:
        logger.info(f"URL: '{url}'")

    # query
    query_result = env.session.request(method=kwargs['method'], url=url, data=payload)

    # save
    with open("query.json", "w") as query_result_file:
        json.dump(query_result, query_result_file, indent=4)
        if not kwargs['stdout']:
            logger.info("Result of the query has been saved in 'query.json'")

    if kwargs['stdout']:
        print(json.dumps(query_result, indent=4))

    logger.debug(f"Total HTTP requests: {env.session.http_requests_count}")

    return True 
