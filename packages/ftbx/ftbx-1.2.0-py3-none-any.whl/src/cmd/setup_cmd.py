"""

    PROJECT: flex_toolbox
    FILENAME: setup_cmd.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: connect command
"""

import os
import re
import logging
import sys

from rich.logging import RichHandler
from src.utils import FTBX_LOG_LEVELS, download_file, get_sdk_version_mapping

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


def setup_command_func(**kwargs):
    """
    Action on setup command.
    """

    logger.debug(f"Entering {__name__} with args: {kwargs}. ")

    version = kwargs['version']
    version_x = re.sub(
        r"\b(\d{4}\.\d{1,2})\.\d{1,2}\b", lambda x: x.group(1) + ".x", version
    )
    logger.info(f"VERSION: {version} ({version_x})")

    # create our dirs for docs and sdk
    os.makedirs("docs", exist_ok=True)
    os.makedirs("sdks", exist_ok=True)

    # find related sdk
    sdk_version_mapping = get_sdk_version_mapping()
    sdk = sdk_version_mapping.get(version_x).get("flex-sdk-external.version", "")
    if not sdk:
        logger.error(
            f"Cannot find '{version}' nor '{version_x}' in the variables.yml.\nPlease check the information provided. "
        )
        sys.exit(1)

    # download doc
    download_file(
        url=f"https://help.dalet.com/daletflex/apis/flex-api-{version}.yml",
        destination=os.path.join("docs", f"{version}.yml"),
    )
    logger.info(
        f"DOCUMENTATION: {version}.yml has been downloaded to docs/{version}.yml"
    )

    # download sdk
    try:
        filenames = [
            f"flex-sdk-external-{sdk}.jar",
            f"flex-sdk-external-{sdk}-javadoc.jar",
            f"flex-sdk-external-{sdk}-sources.jar",
        ]

        for filename in filenames:
            download_file(
                url=f"https://nexus-internal.ooflex.net/repository/maven/com/ooyala/flex/flex-sdk-external/{sdk}/{filename}",
                destination=os.path.join("sdks", f"{filename}"),
            )
            logger.info(
                f"SDK: 'flex-sdk-external-{sdk}.jar' has been downloaded to 'sdks/flex-sdk-external-{sdk}.jar'."
            )
    except Exception:
        logger.error("Failed to download the sdk. Please connect to the 'dlt-fw-uk-UDP4-1120-full-config' VPN.")
