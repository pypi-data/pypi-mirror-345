"""

    PROJECT: flex_toolbox
    FILENAME: compare_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024 

    DESCRIPTION: compare command functions
"""

import logging
import os
import sys

import pandas as pd
from rich.logging import RichHandler
from tqdm import tqdm

from src._environment import Environment
from src._objects import ObjectType, Objects, SubItems
from src.utils import FTBX_LOG_LEVELS, compare_dicts_list, create_folder, filters_to_dict, flatten_dict

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def compare_command_func(**kwargs) -> bool:
    """
    Action on compare command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    # invalid
    if len(kwargs["environments"]) <= 1:
        logger.error(
            f"Cannot compare '{kwargs['object_type']}' if number of environments"
            + f" provided is less than 2 (provided: {kwargs['environments']}). "
        )
        sys.exit(1)
    # valid
    else:

        environments = [
            Environment.from_env_file(environment=e) for e in kwargs["environments"]
        ]

        create_folder(
            folder_name=f"compare_{'_'.join(kwargs['environments'])}", ignore_error=True
        )
        create_folder(
            folder_name=os.path.join(
                f"compare_{'_'.join(kwargs['environments'])}", kwargs["object_type"]
            ),
            ignore_error=True,
        )

        # build object request
        object_type = ObjectType.from_string(string=kwargs["object_type"])
        objects_request = Objects(
            object_type=object_type,
            sub_items=SubItems.from_object_type(object_type=object_type),
            filters=filters_to_dict(filters=kwargs['filters']),
            mode="full"
        )

        # fetch
        cmp = {}
        for env in environments:
            objects = objects_request.get_from(environment=env)
            # from objects to dict of object_name/key: dict
            # for accountProperties, use key instead of name
            object_key = "key" if object_type == ObjectType.ACCOUNT_PROPERTIES else "name"
            # ----------------------------------------------
            objects = {o.__dict__.get(object_key): o.to_dict() for o in objects}
            cmp[env.name] = objects

        # create diff df
        # first env provided is the comparand
        for object_name in tqdm(
            cmp[environments[0].name], desc=f"Comparing {kwargs['object_type']}"
        ):
            tmp_compare = {}

            # flatten
            for env in environments:
                tmp_compare[env.name] = flatten_dict(
                    cmp.get(env.name).get(object_name, {})
                )

            # compare
            result = compare_dicts_list(
                dict_list=[d for d in tmp_compare.values()], environments=environments
            )

            # save
            pd.set_option("display.max_colwidth", None)
            pd.set_option("display.max_rows", None)
            if result is not None:
                result.to_csv(
                    os.path.join(
                        f"compare_{'_'.join(kwargs['environments'])}",
                        kwargs["object_type"],
                        f"{object_name}.tsv",
                    ),
                    sep="\t",
                )

        logger.debug(f"Total HTTP requests: {sum([e.session.http_requests_count for e in environments])}")
        
        logger.info(
            "Result of the comparison (if there are any differences) have been saved in "
            f"'compare_{'_'.join(kwargs['environments'])}/{kwargs['object_type']}/<object_name>.tsv'"
        )

        return True
