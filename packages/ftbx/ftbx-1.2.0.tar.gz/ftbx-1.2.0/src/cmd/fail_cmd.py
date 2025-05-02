"""

    PROJECT: flex_toolbox
    FILENAME: fail_cmd.py
    AUTHOR: David NAISSE
    DATE: November 12th, 2024

    DESCRIPTION: fail command functions
"""

import logging
import os
import sys
import pandas
import json
from datetime import datetime
from tqdm import tqdm
from rich.logging import RichHandler

from src._environment import Environment
from src.utils import FTBX_LOG_LEVELS

# Constants
FAILED = "FAILED"
SYSTEM_JOB_CLASSES = ["MioSystemActionJob", "MioTimeActionJob"]

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()],
)
logger = logging.getLogger(__name__)

def fail_command_func(**kwargs) -> bool:
    """
    Action on fail command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    if kwargs["in_"] == "default":
        kwargs["in_"] = Environment.get_default_environment_alias()

    environment = Environment.from_env_file(environment=kwargs["in_"])
    logger.debug(f"Environment: '{environment.name}'. ")

    # check if database connection is available
    if not environment.database:
        logger.error("Database connection is not available. Please check your environment file at '~/.ftbx/environments' and ensure `consul_token` and `consul_host` are configured for your environment. Note that you also need to be connected to the servers to run this command.")
        sys.exit(1)

    # check if object ids or from file is provided
    if not kwargs["object_ids"] and not kwargs["from_file"]:
        logger.error("No object ids provided. Please provide object ids or a file containing object ids.")
        sys.exit(1)
    elif kwargs["from_file"]:
        # csv
        if kwargs["from_file"].endswith(".csv"):
            objects = pandas.read_csv(kwargs["from_file"])
            kwargs["object_ids"] = objects["id"].tolist()
        # json
        elif kwargs["from_file"].endswith(".json"):
            with open(kwargs["from_file"], "r") as file:
                objects = json.load(file)
            kwargs["object_ids"] = [object["id"] for object in objects]
        else:
            logger.error("The provided file is not a csv or json file.")
            sys.exit(1)

    with environment.database.session() as db_session:
        # fail jobs
        failed_jobs = db_session.fail_jobs(job_ids=kwargs["object_ids"])
        logger.info(f"Successfully failed {len(failed_jobs)} {kwargs['object_type']}.")

        # publish events
        # try as not mandatory
        try:
            with environment.rabbitmq.session() as rabbitmq_session:
                for failed_job in tqdm(failed_jobs, desc="Publishing failure events"):
                    event = {
                        "timestamp": int(datetime.now().timestamp() * 1000),  # epoch milliseconds
                        "userDefinedObjectType": False,
                        "type": FAILED,
                        "subType": "Default",
                        "priority": "Error",
                        "objectId": failed_job["ID_"],
                        "objectTypeId": 6, 
                        "correlationId": failed_job["ACTION_CONFIG_"],
                        "accountId": failed_job["ACCOUNT_"],
                        "workspaceId": failed_job["WORKSPACE_"],
                        "userId": -1, # system user
                        "exceptionMessage": "Failed via flex-toolbox",
                        "objectTypeName": "job",
                        "persistent": True
                    }
                    
                    rabbitmq_session.publish_event(
                        routing_key=f"flex.events.{FAILED}.JOB.ERROR",
                        event=event
                    )

            logger.info(f"Successfully published {len(failed_jobs)} failure events.")
        except Exception as e:
            logger.warning(f"Failed to publish failure events: {str(e)}")

    return True
