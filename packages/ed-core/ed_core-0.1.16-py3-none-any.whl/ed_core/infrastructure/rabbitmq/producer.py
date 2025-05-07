from typing import Generic, TypeVar

import jsons
from pika.adapters import BlockingConnection
from pika.connection import ConnectionParameters, URLParameters

from ed_core.application.contracts.infrastructure.message_queue.abc_producer import (
    ABCProducer,
)
from ed_core.common.logging_helpers import get_logger

LOG = get_logger()

TMessageSchema = TypeVar("TMessageSchema")


class RabbitMQProducer(Generic[TMessageSchema], ABCProducer[TMessageSchema]):
    def __init__(self, url: str, queue: str):
        self._queue = queue
        self._connection = self._connect_with_url_parameters(url)

    def start(self) -> None:
        LOG.info("Starting producer...")
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self._queue, durable=True)

    def stop(self) -> None:
        LOG.info("Stopping producer...")
        self._connection.close()

    def publish(self, message: TMessageSchema) -> None:
        assert "_channel" in self.__dict__, "Producer has not been started"

        try:
            body = jsons.dumps(message)  # type: ignore
            self._channel.basic_publish(exchange="", routing_key=self._queue, body=body)
            LOG.info(f" [x] Sent '{message}'")
        except jsons.SerializationError as e:
            LOG.error(f"Error serializing message: {e}")
        except Exception as e:
            LOG.error(f"Error publishing message: {e}")

    def _connect_with_connection_parameters(
        self, host: str, port: int
    ) -> BlockingConnection:
        connection_parameters = ConnectionParameters(host, port)
        return BlockingConnection(connection_parameters)

    def _connect_with_url_parameters(self, url: str) -> BlockingConnection:
        connection_parameters = URLParameters(url)
        return BlockingConnection(connection_parameters)
