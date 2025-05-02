"""

    PROJECT: flex_toolbox
    FILENAME: list_cmd.py
    AUTHOR: David NAISSE
    DATE: August 8th, 2024

    DESCRIPTION: list command functions
"""

import json
import os
import re
import logging
import datetime
import sys
from typing import List

import pandas as pd
from rich.logging import RichHandler

from src._environment import Environment
from src._objects import ObjectType, Objects, SubItems, get_object_type_log_fields
from src.utils import (
    FTBX_LOG_LEVELS,
    clean_filename,
    convert_to_native_type,
    create_folder,
    filters_to_dict,
)

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def list_command_func(**kwargs) -> List[Objects]:
    """
    Action on list command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    environment = Environment.from_env_file(environment=kwargs['from_'])

    # TMP from csv file
    # this give the ability to retrieve objects from a csv file
    # with column 'id'
    if kwargs['from_csv']:
        ids = [str(id) for id in pd.read_csv(kwargs['from_csv'])["id"].tolist()]
        if kwargs['filters']:
            kwargs['filters'].append(f"id={','.join(ids)}")
        else:
            kwargs['filters']= [f"id={','.join(ids)}"]

    # exact name match if name provided - removed temporarily?
    # if kwargs['filters'] and any("name=" in filter for filter in kwargs['filters']):
    #   kwargs['filters'].append("exactNameMatch=true")

    # get objects
    object_type = ObjectType.from_string(string=kwargs['object_type'])
    objects_request = Objects(
        object_type=object_type,
        sub_items=SubItems.from_object_type(object_type=object_type),
        filters=filters_to_dict(filters=kwargs['filters']),
        post_filters=kwargs['post_filters'] if kwargs['post_filters']else [],
        mode="partial",
    )
    objects = objects_request.get_from(environment=environment, batch_size=kwargs['batch_size'] or 500)

    if len(objects) < 1:
        logger.warn(f"No object found for the given parameters.")
        sys.exit(1)

    # log fields
    log_fields = get_object_type_log_fields(object_type=object_type)
    if kwargs['post_filters']:
        for post_filter in kwargs['post_filters']:
            if "script" not in post_filter:
                for op in ["!=", ">=", "<=", "~", "=", "<", ">"]:
                    if op in post_filter:
                        post_filter = post_filter.split(op)[0]
                        log_fields.append(post_filter)
                        break
    logger.info(f"CSV will contain the following log fields: {log_fields}")

    # build CSV and JSON filenames
    create_folder(folder_name="lists", ignore_error=True)
    dt = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename = kwargs['name']
    if filename is None:
        filename_args = [dt, environment.name, object_type.value]
        if kwargs['filters']:
            filename_args.extend([filter for filter in kwargs['filters'] if kwargs['filters']])
        if kwargs['post_filters']:
            filename_args.extend(
                [post_filter for post_filter in kwargs['post_filters'] if kwargs['post_filters']]
            )
        filename = "_".join(filename_args)
    filename = clean_filename(filename)
    filename = os.path.join("lists", filename)

    # save result as JSON before creating csv
    # if it fails at df creation user will have the json
    with open(f"{filename}.json", "w") as result_file:
        objects_json = [object.to_dict() for object in objects]
        json.dump(objects_json, result_file, indent=4)
        logger.info(f"Saved objects to '{filename}.json'")
        logger.info(f"Saved objects to '{filename}.csv'")

    logger.debug(f"Total HTTP requests: {environment.session.http_requests_count}")

    # TODO: refactor this
    # create and display dataframe
    rows = []
    for object in objects:
        object_dict = object.to_dict()
        row = []
        # extract field
        for log_field in log_fields:
            if "." not in log_field:
                row.append(str(object_dict.get(log_field)))
            else:
                tmp = object_dict
                for subfield in log_field.split("."):
                    try:
                        if "[" in subfield and "]" in subfield:
                            if "[text]" in subfield:
                                tmp = tmp.get(str(subfield.split("[")[0]))
                            elif re.search(r"\[-?\d+\]", subfield):
                                match = int(
                                    re.search(r"\[-?\d+\]", subfield).group(0)[1:-1]
                                )
                                tmp = tmp.get(subfield.split("[")[0])[match]
                        else:
                            tmp = tmp.get(subfield)
                            # replace line breaks otherwise csv is broken
                            if isinstance(tmp, str):
                                tmp = tmp.replace("\n", " ")
                    except:
                        pass
                row.append(str(tmp))
        rows.append(row)

    # display dataframe
    table = pd.DataFrame(rows, columns=log_fields)
    table = table.loc[:, ~table.columns.duplicated()]
    pd.set_option("display.colheader_justify", "center")
    pd.set_option("display.max_colwidth", 75)
    pd.set_option("display.max_rows", 50)
    table.index += 1
    pd.DataFrame.to_csv(table, f"{filename}.csv")
    print(table)

    return objects
