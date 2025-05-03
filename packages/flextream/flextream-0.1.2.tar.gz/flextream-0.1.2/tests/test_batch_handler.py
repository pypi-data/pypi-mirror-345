from types import MethodType
from typing import Any, TypeVar
from dataclasses import dataclass, field
from time import sleep

from flextream import batch_handler


T = TypeVar("T")


def identity(x: T) -> T:
    return x


class DummyEventClient:
    def __init__(*args, **kwargs): ...
    def create_batch(self, *args, **kwargs): ...
    def send_batch(self, *args, **kwargs): ...
    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs): ...


@dataclass
class DummyBatch:
    size_in_bytes: int = 3
    stuff: list = field(default_factory=list)
    block_add: bool = False

    def add(self, something: Any) -> None:
        if self.block_add:
            raise ValueError
        self.stuff.append(something)


def test_send_to_eventhub_crates_batch_handler_and_calls_append(
    monkeypatch,
) -> None:
    catch_stuff = []

    class DummyHandler:
        @classmethod
        def from_namespace(cls, *args, **kwargs) -> "DummyHandler":
            return cls()

        def append(self, message: dict | str | bytes, to_this=catch_stuff) -> None:
            to_this.append(message)

    monkeypatch.setattr(batch_handler, "BatchHandler", DummyHandler)
    batch_handler.send_to_eventhub("hello world!", "name", "event")
    assert catch_stuff == ["hello world!"]


def test_that_from_namespace_caches_based_on_eventhub_and_namespace(
    monkeypatch,
) -> None:
    monkeypatch.setattr(batch_handler, "EventHubProducerClient", DummyEventClient)
    actual_one = batch_handler.BatchHandler.from_namespace("one", "one", latency=1)
    actual_two = batch_handler.BatchHandler.from_namespace("one", "two", latency=2)
    actual_three = batch_handler.BatchHandler.from_namespace("one", "one", latency=3)
    assert actual_one.latency == 3
    assert actual_two.latency == 2
    assert actual_three.latency == 3


def test_that_send_and_flush_toggles_off_waiting_variable(monkeypatch) -> None:
    bh = batch_handler.BatchHandler(
        client=DummyEventClient(),
        batch=DummyBatch(),
        latency=3,
        _waiting=True,
    )
    bh._send_and_flush()
    assert not bh._waiting


def test_that_append_converts_dictionary_to_json_dump(monkeypatch) -> None:
    monkeypatch.setattr(batch_handler, "EventData", identity)
    bh = batch_handler.BatchHandler(
        client=DummyEventClient(),
        batch=DummyBatch(),
        latency=3,
    )
    bh.append({"hello": "world!"})
    assert "world!" in bh.batch.stuff[0]


def test_that_append_calls_out_to_background_threaded_process(monkeypatch) -> None:
    monkeypatch.setattr(batch_handler, "EventData", identity)
    bh = batch_handler.BatchHandler(
        client=DummyEventClient(),
        batch=DummyBatch(size_in_bytes=0),
        latency=0.5,
    )
    assert not bh._waiting
    bh.append(b"Hello world!")
    assert bh._waiting
    sleep(1)
    assert not bh._waiting


def test_that_append_falls_back_to_send_and_flush_when_value_error_raised_by_add(
    monkeypatch,
):
    monkeypatch.setattr(batch_handler, "EventData", identity)
    bh = batch_handler.BatchHandler(
        client=DummyEventClient(),
        batch=DummyBatch(block_add=True),
        latency=0.5,
    )

    def send_and_flush_patch(self, *args, **kwargs) -> None:
        self._waiting = False
        self.batch.block_add = False

    bh._send_and_flush = MethodType(send_and_flush_patch, bh)
    assert not bh._waiting
    bh.append(b"Hello world!")
    assert bh._waiting
    sleep(1)
    assert not bh._waiting
