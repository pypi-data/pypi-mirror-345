from __future__ import annotations

import typing
import logging

from .response import JsonResponse
from .endpoint import Endpoint, Parameter, NoDefault
from .codecs import Codec


if typing.TYPE_CHECKING:
    from .requesthandler import HTTPRequestHandler
    from .server import Server


logger = logging.getLogger(__name__)


class GetHandler:
    def __init__(self, request: HTTPRequestHandler):
        self.request = request

    def handle(self) -> JsonResponse:
        generator = APIDefinitionGenerator(self.request.get_server())
        return JsonResponse(generator.generate())


class APIDefinitionGenerator:
    def __init__(self, server: Server):
        self._server = server

    def generate(self) -> dict:
        server = self._server
        return {
            "endpoints": [self._endpoint_as_dict(e) for e in server.endpoints.values()],
            "ssl_enabled": server.ssl_enabled,
        }

    def _endpoint_as_dict(self, endpoint: Endpoint) -> dict:
        """Convert Endpoint instance into dictionary."""
        definition = {
            "name": endpoint.name,
            "documentation": endpoint.doc,
            "parameters": self._create_parameters_definition(
                endpoint.parameters.values()
            ),
        }

        if "return" in endpoint.parameters:
            codecs = endpoint.parameters["return"].codecs
            definition["returnAnnotation"] = self._get_type_annotation(codecs)
        else:
            definition["returnAnnotation"] = []

        return definition

    def _create_parameters_definition(self, parameters: list[Parameter]) -> list:
        return [
            self._get_parameter_as_dict(p) for p in parameters if p.name != "return"
        ]

    def _get_parameter_as_dict(self, parameter: Parameter):
        logger.debug("Converting '%s' parameter to dict.", parameter)
        definition = {
            "name": parameter.name,
            "annotation": self._get_type_annotation(parameter.codecs),
            "optional": parameter.optional,
        }

        try:
            definition["default"] = repr(parameter.get_default()).strip("'")
        except NoDefault:
            pass

        return definition

    def _get_type_annotation(self, codecs: list[Codec]) -> typing.Union[str, list[str]]:
        types = [codec.get_encode_type().__name__ for codec in codecs]
        # Removing possible duplicates. Representing e.g., dataclasses as tuples may
        # cause duplicates.
        #
        #   @dataclass
        #   class A:
        #       a: int
        #
        #   @dataclass
        #   class B:
        #       b: int
        #
        #   function c() -> typing.Union[A, B] gets converted into
        #   function c() -> typing.Union[tuple, tuple].
        return list(dict.fromkeys(types))
