import typing

import pytest
import threading
from enum import Enum, auto
from collections import namedtuple
from dataclasses import dataclass
from dataclasses import is_dataclass

from remotecall import Server
from remotecall import BaseClient
from remotecall.exceptions import BadRequestError
from remotecall.exceptions import NotFoundError


class FooEnum(Enum):
    A = auto()
    B = auto()
    C = auto()


FooNamedTuple = namedtuple("Item", "name, value")


@dataclass
class FooDataClass:
    name: str
    value: float


@pytest.fixture
def server_address():
    return "127.0.0.1", 8000


@pytest.fixture
def server(server_address):

    def foo(a: int) -> int:
        return a

    def enum_as_parameter(value: FooEnum):
        assert isinstance(value, FooEnum)

    def enum_as_return_type() -> FooEnum:
        return FooEnum.A

    def namedtuple_as_parameter(value: FooNamedTuple):
        assert isinstance(value, FooNamedTuple)

    def namedtuple_as_return_type() -> FooNamedTuple:
        return FooNamedTuple("A", 42)

    def dataclass_as_parameter(value: FooDataClass):
        assert is_dataclass(value)

    def dataclass_as_return_type() -> FooDataClass:
        return FooDataClass("A", 42)

    def optional_arg(value: typing.Optional[int] = None):
        assert value is None or isinstance(value, int)

    with Server(server_address) as server:
        server.expose(foo)
        server.expose(enum_as_parameter)
        server.expose(enum_as_return_type)
        server.expose(namedtuple_as_parameter)
        server.expose(namedtuple_as_return_type)
        server.expose(dataclass_as_parameter)
        server.expose(dataclass_as_return_type)
        server.expose(optional_arg)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        yield server
        server.shutdown()
        server_thread.join()


@pytest.fixture
def client(server_address):
    client = BaseClient(server_address)
    return client


def test_server_url(client):
    hostname, port = client.server_address
    scheme = "https" if client.ssl_enabled else "http"
    assert client.server_url == f"{scheme}://{hostname}:{port}"


def test_call(server, client):
    assert client.call("foo", a=1) == 1

    with pytest.raises(NotFoundError):
        client.call("non_existing_function")

    with pytest.raises(BadRequestError):
        client.call("foo", non_existing_parameter=1)

    with pytest.raises(TypeError):
        client.call()

    client.register_type(FooEnum)
    client.register_type(FooNamedTuple)
    client.register_type(FooDataClass)

    client.call("enum_as_parameter", value=FooEnum.A)
    client.call("enum_as_parameter", value="A")
    foo_enum = client.call("enum_as_return_type")
    assert isinstance(foo_enum, str)
    assert foo_enum == FooEnum.A.name

    client.call("namedtuple_as_parameter", value=FooNamedTuple("A", 42))
    client.call("namedtuple_as_parameter", value=("A", 42))
    client.call("namedtuple_as_parameter", value={"name": "A", "value": 42})
    foo_namedtuple = client.call("namedtuple_as_return_type")
    assert isinstance(foo_namedtuple, tuple)
    assert foo_namedtuple[0] == "A"
    assert foo_namedtuple[1] == 42

    client.call("dataclass_as_parameter", value=FooDataClass("A", 42))
    client.call("dataclass_as_parameter", value=("A", 42))
    client.call("dataclass_as_parameter", value={"name": "A", "value": 42})
    foo_dataclass = client.call("dataclass_as_return_type")
    assert isinstance(foo_dataclass, dict)
    assert foo_dataclass["name"] == "A"
    assert foo_dataclass["value"] == 42

    client.call("optional_arg", value=42)
    client.call("optional_arg")

    from remotecall import fetch_api
    import json

    definition = fetch_api(url=server.url)
    # JSON library transforms data to valid ascii objects by default (ensure_ascii=True). Thus,
    # non-ASCII characters are ASCII encoded (e.g., 'Ä' is \u00c4).
    print(json.dumps(definition, indent=4, ensure_ascii=True))
