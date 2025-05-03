"""
Functions and classes related to batching, and shipping data out to event hubs
"""

import threading
import json
from dataclasses import dataclass, field
from typing import Any

from azure.eventhub import EventHubProducerClient, EventDataBatch, EventData
from azure.identity import DefaultAzureCredential


def send_to_eventhub(
    message: dict | str | bytes,
    namespace: str,
    eventhub: str,
    latency: int = 30,
    credential: Any = None,
) -> None:
    """
    Create/load BatchHandler, and send message to eventhub.

    To avoid bottlenecks, messages will be batched up
    and sent in background. `latency` keyword defines the maximum number of
    seconds a message will be held onto before sending to eventhubs.

    Having a latency of 0 will mean that messages are immediately sent in function call,
    but this behaviour is not recommended for performance reasons.

    Note, namespace should be fully qualified of form
    "namespace-name.servicebus.windows.net".

    Optional keyword `credential` can be used to pass in an `azure.identity`
    credential object. Otherwise, will default to `DefaultAzureCredential`.
    """
    BatchHandler.from_namespace(
        namespace,
        eventhub,
        latency=latency,
        credential=credential,
    ).append(message)


_batch_handler_cache: dict[tuple[str, str], "BatchHandler"] = {}


def _cachable_batch_handler_factor(
    namespace: str,
    eventhub: str,
    latency: int | float = 30,
    credential: Any = None,
) -> "BatchHandler":
    """
    Private module function to handle caching of BatchHandler objects
    based on namespace and eventhub.
    """
    existing: BatchHandler | None = _batch_handler_cache.get((namespace, eventhub))
    if existing:
        existing.latency = latency
        return existing
    client: EventHubProducerClient = EventHubProducerClient(
        fully_qualified_namespace=namespace,
        eventhub_name=eventhub,
        credential=credential or DefaultAzureCredential(),
    )
    batch: EventDataBatch = client.create_batch()
    handler = BatchHandler(
        client=client,
        batch=batch,
        latency=latency,
    )
    _batch_handler_cache[(namespace, eventhub)] = handler
    return handler


@dataclass
class BatchHandler:
    """
    Class to handle appending to, and building up of batches for efficient event
    hub use.

    Note: Uses threading locks to avoid race conditions, which will *only* hold
    if called using threading executors rather than asyncio.
    """

    client: EventHubProducerClient
    batch: EventDataBatch
    latency: int | float
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _waiting: bool = False
    _timer: threading.Timer | None = None

    @classmethod
    def from_namespace(
        cls,
        namespace: str,
        eventhub: str,
        latency: int | float = 30,
        credential: Any = None,
    ) -> "BatchHandler":
        """
        Class method to create a batch handler object from a given azure namespace
        and eventhub.
        """
        return _cachable_batch_handler_factor(
            namespace=namespace,
            eventhub=eventhub,
            latency=latency,
            credential=credential,
        )

    def _send_and_flush(self) -> None:
        """
        Send batch, and replace with new empty batch
        """
        with self._lock:
            self._waiting = False
            if self.batch.size_in_bytes <= 0:
                return  # we'll exit out if no data
            with self.client:
                self.client.send_batch(self.batch)
            self.batch = self.client.create_batch()

    def append(self, msg: str | bytes | dict) -> None:
        """
        Append a message onto the batch, sending only if necessary to make space.
        """
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        with self._lock:
            try:
                self.batch.add(EventData(msg))
            except ValueError:  # batch is at max capacity
                self._send_and_flush()
                self.batch.add(EventData(msg))
            if not self._waiting:
                self._timer = threading.Timer(self.latency, self._send_and_flush)
                self._timer.daemon = True
                self._timer.start()
                self._waiting = True
