import dataclasses
import json
import typing

from collections import namedtuple
from enum import Enum

from remotecall import Server
from remotecall import fetch_api
from remotecall import generate_client
from remotecall.gethandler import APIDefinitionGenerator


def test_fetch_api(server: Server):
    definition = fetch_api(url=server.url)
    # JSON library transforms data to valid ascii objects by default (ensure_ascii=True). Thus,
    # non-ASCII characters are ASCII encoded (e.g., 'Ä' is \u00c4).
    print(json.dumps(definition, indent=4, ensure_ascii=True))


def test_generate_api(server: Server):
    definition = fetch_api(url=server.url)
    code = generate_client(definition)
    print(code)


def test_generate_api_definition(server_address):
    @dataclasses.dataclass
    class MyDataclass:
        name: str
        value: int

    MyNamedtuple = namedtuple("MyNamedtuple", "name, value")

    class MyEnum(Enum):
        A = 1
        B = 2

    def no_args(): pass
    def int_arg(value: int): pass
    def float_arg(value: float): pass
    def bool_arg(value: bool): pass
    def bytes_arg(value: bytes): pass
    def str_arg(value: str): pass
    def list_arg(value: list, value2: list[int]): pass
    def tuple_arg(value: tuple, value2: tuple[str, int]): pass
    def dict_arg(value: dict, value2: dict[str, int]): pass
    def dataclass_arg(value: MyDataclass): pass
    def namedtuple_arg(value: MyNamedtuple): pass
    def enum_arg(value: MyEnum): pass
    def optional_arg(value: typing.Optional[int] = None): pass
    # def optional_arg(value: typing.Optional[str] = None, value2: str | None = None): pass

    with Server(("localhost", 8001)) as server:
        server.expose(no_args)
        server.expose(int_arg)
        server.expose(float_arg)
        server.expose(bool_arg)
        server.expose(bytes_arg)
        server.expose(str_arg)
        server.expose(list_arg)
        server.expose(tuple_arg)
        server.expose(dict_arg)
        server.expose(dataclass_arg)
        server.expose(namedtuple_arg)
        server.expose(enum_arg)
        server.expose(optional_arg)

    generator = APIDefinitionGenerator(server)
    api_definition = generator.generate()
    print(api_definition)
    endpoints = api_definition["endpoints"]
    print(endpoints)

    assert endpoints[0]["name"] == "no_args"
    assert endpoints[0]["documentation"] == ""
    assert endpoints[0]["parameters"] == []
    assert endpoints[0]["returnAnnotation"] == []

    assert endpoints[1]["name"] == "int_arg"
    assert endpoints[1]["parameters"][0]["name"] == "value"
    assert endpoints[1]["parameters"][0]["annotation"] == ["int"]

    assert endpoints[2]["name"] == "float_arg"
    assert endpoints[2]["parameters"][0]["name"] == "value"
    assert endpoints[2]["parameters"][0]["annotation"] == ["float"]

    assert endpoints[3]["name"] == "bool_arg"
    assert endpoints[3]["parameters"][0]["name"] == "value"
    assert endpoints[3]["parameters"][0]["annotation"] == ["bool"]

    assert endpoints[4]["name"] == "bytes_arg"
    assert endpoints[4]["parameters"][0]["name"] == "value"
    assert endpoints[4]["parameters"][0]["annotation"] == ["bytes"]

    assert endpoints[5]["name"] == "str_arg"
    assert endpoints[5]["parameters"][0]["name"] == "value"
    assert endpoints[5]["parameters"][0]["annotation"] == ["str"]

    assert endpoints[6]["name"] == "list_arg"
    assert endpoints[6]["parameters"][0]["name"] == "value"
    assert endpoints[6]["parameters"][0]["annotation"] == ["list"]
    assert endpoints[6]["parameters"][1]["annotation"] == ["list"]

    assert endpoints[7]["name"] == "tuple_arg"
    assert endpoints[7]["parameters"][0]["name"] == "value"
    assert endpoints[7]["parameters"][0]["annotation"] == ["tuple"]
    assert endpoints[7]["parameters"][1]["annotation"] == ["tuple"]

    assert endpoints[8]["name"] == "dict_arg"
    assert endpoints[8]["parameters"][0]["name"] == "value"
    assert endpoints[8]["parameters"][0]["annotation"] == ["dict"]
    assert endpoints[8]["parameters"][1]["annotation"] == ["dict"]

    assert endpoints[9]["name"] == "dataclass_arg"
    assert endpoints[9]["parameters"][0]["name"] == "value"
    assert endpoints[9]["parameters"][0]["annotation"] == ["dict"]

    assert endpoints[10]["name"] == "namedtuple_arg"
    assert endpoints[10]["parameters"][0]["name"] == "value"
    assert endpoints[10]["parameters"][0]["annotation"] == ["tuple"]

    assert endpoints[11]["name"] == "enum_arg"
    assert endpoints[11]["parameters"][0]["name"] == "value"
    assert endpoints[11]["parameters"][0]["annotation"] == ["str"]

    assert endpoints[12]["name"] == "optional_arg"
    assert endpoints[12]["parameters"][0]["name"] == "value"
    assert endpoints[12]["parameters"][0]["annotation"] == ["int", "NoneType"]
