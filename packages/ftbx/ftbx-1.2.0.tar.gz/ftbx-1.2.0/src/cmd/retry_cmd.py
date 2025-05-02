"""

    PROJECT: flex_toolbox
    FILENAME: retry_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: retry command functions
"""

import json
import logging
import os
import sys

import pandas as pd
from rich.logging import RichHandler
from tqdm import tqdm

from src._environment import Environment
from src._objects import ObjectType, Objects
from src.utils import FTBX_LOG_LEVELS, filters_to_dict

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()],
)
logger = logging.getLogger(__name__)


def retry_command_func(**kwargs) -> bool:
    """
    Action on retry command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    environment = Environment.from_env_file(environment=kwargs["in_"])

    # add specific filters
    kwargs["filters"].append("status=Failed")

    # input is file
    objects = []
    if kwargs["file"]:

        # csv
        if ".csv" in kwargs["file"].lower():
            df = pd.read_csv(kwargs["file"])
            for id in tqdm(df["id"], desc=f"Retrying {kwargs['object_type']}"):
                object = Objects(
                    object_type=ObjectType.from_string(string=kwargs["object_type"]),
                    sub_items=[],
                    config={"id": id},
                )
                object.retry(environment=environment)
                objects.append(object)

        # json
        elif ".json" in kwargs["file"].lower():
            with open(kwargs["file"], "r") as json_file:
                instances = json.load(json_file)
            for instance in tqdm(instances, desc=f"Retrying {kwargs['object_type']}"):
                object = Objects(
                    object_type=ObjectType.from_string(string=kwargs["object_type"]),
                    sub_items=[],
                    config={"id": instances[instance].get("id")},
                )
                object.retry(environment=environment)
                objects.append(object)

        else:
            logger.error(
                f"'{kwargs['file']}' doesn't belong to the supported formats. Please try with .json or .csv instead."
            )
            sys.exit(1)

    # input is filters
    else:
        objects_request = Objects(
            object_type=ObjectType.from_string(string=kwargs["object_type"]),
            sub_items=[],
            filters=filters_to_dict(filters=kwargs["filters"]),
            post_filters=[]
        )
        objects = objects_request.get_from(environment=environment)

        for object in tqdm(objects, desc=f"Retrying {kwargs['object_type']}"):
            object.retry(environment=environment)

    logger.debug(f"Total HTTP requests: {environment.session.http_requests_count}")

    return True
