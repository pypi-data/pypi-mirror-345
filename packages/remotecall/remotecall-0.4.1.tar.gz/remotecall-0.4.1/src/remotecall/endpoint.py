from __future__ import annotations

import logging
import typing
import types
import inspect
from inspect import signature, getdoc, cleandoc
from typing import get_type_hints
from enum import Enum

from .codecs import Codec, Codecs


logger = logging.getLogger(__name__)


def is_optional(type_hint: type):
    """Is type hinted parameter optional.

    Returns True if a parameter is optional.

    For example,

        def sample(a: Optional[int] = 1):
            pass
    """
    origin = typing.get_origin(type_hint)
    return origin is typing.Union and type(None) in typing.get_args(type_hint)


def is_union(type_hint: type):
    """Is type hint union."""
    return typing.get_origin(type_hint) is typing.Union


class EndpointNotFound(Exception):
    """Raised if endpoint is not found by name."""


class NoDefault(Exception):
    """Raised if default value is not defined."""


class Endpoint:
    def __init__(self, name: str, handler: typing.Callable):
        self.name = name
        self.handler = handler
        self.signature = signature(self.handler)
        self.enabled = True
        self.parameters: dict[str, Parameter] = {}

    def __str__(self) -> str:
        return f"Endpoint('{self.name}')"

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    @property
    def doc(self) -> str:
        doc = getdoc(self.handler)
        return cleandoc(doc) if doc else ""

    def setup(self, codecs: Codecs):
        try:
            type_hints = get_type_hints(self.handler)  # , globalns=globals())
        except NameError as error:
            raise ValueError(
                f"Failed to get type hints of '{self.handler}': {error}."
                "Check parameter types are available in runtime."
            ) from error

        for parameter_name, type_hint in type_hints.items():
            parameter = Parameter(parameter_name, self)

            if is_optional(type_hint):
                parameter.optional = True

                for class_object in typing.get_args(type_hint):
                    if isinstance(class_object, types.GenericAlias):
                        # E.g., list[int], tuple[str, int]
                        codec = codecs.get_codec_by_type(
                            typing.get_origin(class_object)
                        )
                    else:
                        codec = codecs.get_codec_by_type(class_object)

                    parameter.add_codec(codec)

            elif is_union(type_hint):
                for class_object in typing.get_args(type_hint):
                    codec = codecs.get_codec_by_type(class_object)
                    parameter.add_codec(codec)

            elif isinstance(type_hint, types.GenericAlias):
                # E.g., list[int], tuple[str, int]
                class_object = typing.get_origin(type_hint)
                codec = codecs.get_codec_by_type(class_object)
                parameter.add_codec(codec)

            else:
                codec = codecs.get_codec_by_type(type_hint)
                parameter.add_codec(codec)

            self.parameters[parameter_name] = parameter


class Parameter:
    def __init__(self, name: str, endpoint: Endpoint):
        self.name = name
        self._endpoint = endpoint
        self.codecs: list[Codec] = []
        self.optional = False

    def __str__(self):
        return self.name

    def add_codec(self, codec: Codec):
        self.codecs.append(codec)

    def get_codec_by_content_type(self, content_type: str) -> Codec:
        for codec in self.codecs:
            if codec.is_matching_content_type(content_type):
                return codec
        raise ValueError(
            f"Parameter '{self}' does not have a codec for content-type '{content_type}'."
        )

    def get_default(self) -> str:
        parameter = signature(self._endpoint.handler).parameters[self.name]
        default = parameter.default

        if default is inspect.Parameter.empty:
            raise NoDefault

        if isinstance(default, Enum):
            return default.name

        return str(default) if default is not inspect.Parameter.empty else ""
