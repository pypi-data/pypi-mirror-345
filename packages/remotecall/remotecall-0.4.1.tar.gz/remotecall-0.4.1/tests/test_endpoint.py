from __future__ import annotations

import pytest

from typing import Optional
from enum import Enum

from remotecall.endpoint import Endpoint
from remotecall.endpoint import NoDefault
from remotecall.codecs import Codec, Codecs
from remotecall.codecs import APPLICATION_INT
from remotecall.codecs import APPLICATION_FLOAT
from remotecall.codecs import APPLICATION_ENUM


class FooEnum(Enum):
    A = 1
    B = 2
    C = 3


@pytest.fixture
def endpoint():
    def foo(a: int, b: float = 1.0, c: FooEnum = FooEnum.C) -> bool:
        """Foo"""
        return True

    return Endpoint("foo", foo)


def test_setup(endpoint):
    codecs = Codecs(Codec.subclasses)
    endpoint.setup(codecs)

    endpoint.parameters["a"].get_codec_by_content_type(APPLICATION_INT)
    endpoint.parameters["b"].get_codec_by_content_type(APPLICATION_FLOAT)
    endpoint.parameters["c"].get_codec_by_content_type(APPLICATION_ENUM)

    with pytest.raises(ValueError):
        endpoint.parameters["a"].get_codec_by_content_type(APPLICATION_FLOAT)

    parameter_a = endpoint.parameters["a"]
    parameter_b = endpoint.parameters["b"]
    parameter_c = endpoint.parameters["c"]

    with pytest.raises(NoDefault):
        parameter_a.get_default()

    assert parameter_b.get_default() == "1.0"
    assert parameter_c.get_default() == "C"


def test_doc(endpoint):
    assert endpoint.doc == "Foo", "Expecting 'Foo'."
