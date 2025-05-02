"""

    PROJECT: flex_toolbox
    FILENAME: _rabbitmq.py
    AUTHOR: David NAISSE
    DATE: November 15th, 2024

    DESCRIPTION: rabbitmq class
"""

import json
import logging
import os
from typing import Any, Dict, Generator
from contextlib import contextmanager

import pika
from rich.logging import RichHandler

from src._consul import Consul
from src.utils import FTBX_LOG_LEVELS

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()],
)
logger = logging.getLogger(__name__)

# Set Pika logging to WARNING level
logging.getLogger("pika").setLevel(logging.WARNING)


class RabbitMQSession:
    """RabbitMQ session wrapper"""
    
    def __init__(self, connection, channel):
        self.connection = connection
        self.channel = channel

    def publish_event(self, routing_key: str, event: Dict[str, Any]) -> None:
        """Publish an event to RabbitMQ"""
        try:
            # publish message to existing exchange
            exchange_name = "flex.events.exchange"
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(event),
                mandatory=True,
                properties=pika.BasicProperties(
                    content_type='application/json',
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
            raise


class RabbitMQ:
    """RabbitMQ client wrapper"""

    def __init__(self, consul: Consul) -> None:
        """Initialize RabbitMQ client"""
        self.consul = consul
        logger.debug("Initialized RabbitMQ connection")

    def _create_connection(self) -> tuple[Any, Any]:
        """Create a new RabbitMQ connection and channel"""
        try:
            # get credentials from consul
            credentials = self.consul.get_rabbitmq_credentials()
            
            # create credentials object
            credentials_obj = pika.PlainCredentials(
                credentials["username"],
                credentials["password"]
            )
            parameters = pika.ConnectionParameters(
                host=credentials["host"],
                port=credentials["port"],
                credentials=credentials_obj,
                connection_attempts=3,
                retry_delay=1,
            )
            
            # establish connection
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            logger.debug("RabbitMQ connection established")
            return connection, channel
            
        except Exception as e:
            logger.error(f"Failed to establish RabbitMQ connection: {str(e)}")
            raise

    @contextmanager
    def session(self) -> Generator[RabbitMQSession, None, None]:
        """Create a RabbitMQ session context manager"""
        connection, channel = self._create_connection()
        try:
            yield RabbitMQSession(connection, channel)
        finally:
            channel.close()
            connection.close()
            logger.debug("RabbitMQ connection closed")
