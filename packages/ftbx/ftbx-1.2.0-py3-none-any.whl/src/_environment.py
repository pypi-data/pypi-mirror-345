"""

    PROJECT: flex_toolbox
    FILENAME: environment.py
    AUTHOR: David NAISSE
    DATE: August 7th, 2024 

    DESCRIPTION: environment class
"""

import sys
from src.utils import FTBX_LOG_LEVELS
from src._session import Session
from src._consul import Consul
from src._database import Database
from src._rabbitmq import RabbitMQ

import time
import os
import json
import logging

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


class Environment:

    def __init__(
        self, name: str, url: str, username: str, password: str, version: str = "latest",
        consul_host: str = None, consul_token: str = None
    ) -> None:

        self.name = name
        self.url = url
        self.username = username
        self.password = password
        self.version = version

        # HTTP session
        self.session = Session(
            url=self.url, username=self.username, password=self.password
        )
        
        # Consul, Database and RabbitMQ
        self.consul = Consul(consul_host, consul_token) if consul_host and consul_token else None
        self.database = Database(self.consul) if self.consul else None
        self.rabbitmq = RabbitMQ(self.consul) if self.consul else None

    @classmethod
    def from_env_file(
        cls,
        environment: str,
    ):
        """
        Init environment from environment file.

        :param environment: alias of the environment
        :param environment_file_path: path to the environment file

        :return: Environment
        """

        # if default, get alias
        if environment == "default":
            environment = Environment.get_default_environment_alias()

        envs = Environment.read_environments_file()

        try:
            env_data = envs["environments"][environment]
        # env doesn't exist in file
        except KeyError:
            logger.error(
                f"Couldn't find any '{environment}' environment in environments file. Please use 'ftbx env' to list all available environments."
            )
            sys.exit(1)

        env = Environment(
            name=environment,
            url=env_data["url"],
            username=env_data["username"],
            password=env_data["password"],
            version=env_data["version"] if "version" in env_data else "latest",
            consul_host=env_data["consul_host"] if "consul_host" in env_data else None,
            consul_token=env_data["consul_token"] if "consul_token" in env_data else None
        )

        logger.debug(f"Environment {vars(env)} has been loaded. ")

        return env

    @staticmethod
    def read_environments_file(
        env_file_path: str = os.path.join(
            os.path.expanduser("~"), ".ftbx", "environments"
        )
    ) -> dict:
        """
        Read or creates the environments file.

        :param env_file_path: env file path
        """

        logger.debug(f"Trying to read '{env_file_path}'...")
        try:
            # read existing json
            with open(env_file_path, "r") as file:
                environments = json.load(file)
        except FileNotFoundError:
            logger.debug(f"File '{env_file_path}' couldn't be found, creating it...")
            # if the file doesn't exist, create it with the default content
            environments = {"environments": {}}
            with open(env_file_path, "w") as file:
                json.dump(environments, file, indent=4)

        return environments

    def connect(self) -> bool:
        """
        Tries to connect to an environment.
        """

        start_time = time.time()
        # this will raise an exception if failure
        # see session.py
        self.session.request(method="GET", url=f"{self.url}/api/accounts")
        end_time = time.time()

        delta = round(end_time - start_time, 3)
        logger.info(f"STATUS: Connection successful ({delta} seconds)")

        return True

    def save(
        self,
        env_file_path: str = os.path.join(
            os.path.expanduser("~"), ".ftbx", "environments"
        ),
    ) -> None:
        """
        Save environment.
        """

        environments = Environment.read_environments_file()
        environments["environments"][self.name] = {
            "url": self.url,
            "username": self.username,
            "password": self.password,
            "version": self.version,
            "consul_host": self.consul.host if self.consul else None,
            "consul_token": self.consul.token if self.consul else None
        }

        with open(env_file_path, "w") as environments_file:
            json.dump(environments, environments_file, indent=4, sort_keys=True)

        logger.debug(f"Environment '{self.name}' has been saved. ")

    def set_default(
        self,
        env_file_path: str = os.path.join(
            os.path.expanduser("~"), ".ftbx", "environments"
        ),
    ) -> None:
        """
        Set environment as default.
        """

        environments = Environment.read_environments_file()
        environments["environments"]["default"] = {
            "url": self.url,
            "username": self.username,
            "password": self.password,
            "version": self.version,
            "consul_host": self.consul.host if self.consul else None,
            "consul_token": self.consul.token if self.consul else None
        }

        with open(env_file_path, "w") as environments_file:
            json.dump(environments, environments_file, indent=4, sort_keys=True)

        logger.info(
            f"DEFAULT ENVIRONMENT: {self.url} [{self.name}] as '{self.username}'."
        )

    def get_default_account_id(self) -> int:
        """
        Get the environment default account id.
        """

        accounts = self.session.request(
            method="GET", url=f"{self.url}/api/accounts"
        ).get("accounts")
        assert len(accounts) > 0, "/!\\ CANNOT FIND ANY ACCOUNT. EXITING... /!\\"

        # get default
        if len(accounts) == 1:
            default_account_id = accounts[0].get("id")
        else:
            default_account_id = next(
                account.get("id")
                for account in accounts
                if account.get("name") != "master"
            )

        return default_account_id

    @staticmethod
    def get_default_environment_alias():
        """
        Get the default environment alias.
        """

        environments = Environment.read_environments_file().get("environments")
        assert environments

        default_env_url = environments.get("default").get("url")
        default_env_username = environments.get("default").get("username")

        for k, v in environments.items():
            if (
                k != "default"
                and v.get("url") == default_env_url
                and v.get("username") == default_env_username
            ):
                return k

        logger.error(f"Could not retrieve default environment alias. ")
        sys.exit(1)
