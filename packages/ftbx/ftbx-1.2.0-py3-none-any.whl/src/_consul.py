"""

    PROJECT: flex_toolbox
    FILENAME: _consul.py
    AUTHOR: David NAISSE
    DATE: November 12th, 2024

    DESCRIPTION: consul class
"""

import logging
import os
from typing import Any, Dict, Optional, List, Tuple

import consul
from rich.logging import RichHandler
import random

from src.utils import FTBX_LOG_LEVELS

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()],
)
logger = logging.getLogger(__name__)


class Consul:
    """Consul client wrapper"""

    def __init__(self, host: str, token: str) -> None:
        """Initialize Consul client"""
        self.host = host
        self.token = token
        self.client = consul.Consul(host=self.host, token=self.token)
        logger.debug("Initialized Consul client")

    def get_value(self, key: str) -> Optional[str]:
        """Get value from Consul KV store"""
        try:
            _, data = self.client.kv.get(key)
            if data and 'Value' in data:
                return data['Value'].decode('utf-8')
            return None
        except Exception as e:
            logger.error(f"Failed to get value for key {key}: {str(e)}")
            return None

    def get_db_credentials(self) -> Dict[str, Any]:
        """Get database credentials from Consul"""
        try:
            credentials = {
                "user": self.get_value("flex/shared/flex-enterprise/mysql/username"),
                "password": self.get_value("flex/shared/flex-enterprise/mysql/password"),
                "database": self.get_value("flex/shared/flex-enterprise/mysql/database"),
                "host": self.get_value("flex/shared/mysql/host"),
                "port": int(self.get_value("flex/shared/mysql/port"))
            }
            
            if None in credentials.values():
                raise ValueError("One or more required database credentials not found in Consul")
                
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to get database credentials: {str(e)}")
            raise
    
    def get_rabbitmq_credentials(self) -> Dict[str, Any]:
        """Get RabbitMQ credentials from Consul"""
        try:
            # get credentials
            username = self.get_value("flex/shared/rabbitmq/username")
            password = self.get_value("flex/shared/rabbitmq/password")
            
            # get service details
            _, services = self.client.catalog.service("rabbitmq-5672")
            if not services:
                raise ValueError("No RabbitMQ services found in Consul")
            
            # randomly select a host
            service = random.choice(services)
            host = service["ServiceAddress"] or service["Address"]
            port = service["ServicePort"]
            
            credentials = {
                "username": username,
                "password": password,
                "host": host,
                "port": port
            }
            
            if None in credentials.values():
                raise ValueError("One or more required RabbitMQ credentials not found in Consul")
                
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to get RabbitMQ credentials: {str(e)}")
            raise

    def check_service_health(self, service_name: str) -> Tuple[bool, List[str]]:
        """Check if a service is healthy using Consul's health API"""
        try:
            # get service health checks
            index, checks = self.client.health.checks(service_name)
            
            messages = []
            all_passing = True
            
            for check in checks:
                status = check['Status']
                check_id = check['CheckID']
                messages.append(f"Check {check_id}: {status}")
                
                if status != 'passing':
                    all_passing = False
                    logger.warning(f"Service {service_name} check {check_id} status: {status}")
            
            if all_passing:
                logger.debug(f"Service {service_name} is healthy")
            else:
                logger.error(f"Service {service_name} has failing health checks")
            
            return all_passing, messages
            
        except Exception as e:
            logger.error(f"Failed to check health for service {service_name}: {str(e)}")
            return False, [f"Error checking service health: {str(e)}"]
