from __future__ import annotations

import logging
import re
import typing
from dataclasses import dataclass
from typing import BinaryIO
from typing import Optional

from .constants import headers
from .constants.headers import CONTENT_DISPOSITION
from .constants.headers import CONTENT_TYPE
from .exceptions import BadRequestError
from .exceptions import NotFoundError
from .exceptions import ServerError
from .exceptions import ServiceUnavailableError
from .response import Response

if typing.TYPE_CHECKING:
    from .endpoint import Endpoint
    from .requesthandler import HTTPRequestHandler


logger = logging.getLogger(__name__)


@dataclass
class MultiPartFormDataField:
    name: str
    content_type: str
    data: bytes


class PostHandler:
    def __init__(self, request: HTTPRequestHandler):
        self.request = request
        self._server = self.request.get_server()
        self._codecs = self._server.codecs

    def handle(self) -> Response:  # pylint: disable=broad-exception-caught
        endpoint_name = self.request.path_component

        try:
            endpoint = self._server.endpoints[endpoint_name]
        except KeyError as err:
            raise NotFoundError(f"Unknown endpoint: '{endpoint_name}'") from err

        if not endpoint.enabled:
            raise ServiceUnavailableError("Endpoint disabled.")

        try:
            arguments = self.get_arguments(endpoint)
        except ValueError as err:
            logger.exception(err)
            raise BadRequestError(f"Failed to parse request arguments: {err}") from err

        try:
            return_value = endpoint(**arguments)
        except TypeError as err:
            logger.exception(err)
            raise TypeError(str(err)) from err

        try:
            codec = self._codecs.get_codec_by_value(return_value)
            logger.debug("Using %s to decode return value.", codec)
            data_bytes, content_type = codec.encode(return_value)
            response = Response(data_bytes, content_type)
        except Exception as err:
            logger.exception(err)
            raise ServerError(f"Failed to encode return value: {err}") from err

        return response

    def get_arguments(self, endpoint: Endpoint) -> dict:
        logger.debug("Get arguments.")

        arguments = {}
        request = self.request

        if not request.headers.get(CONTENT_TYPE):
            logger.debug("No arguments ('content-type' not set).")
            return arguments

        # Note: get_content_type() returns default content type (most often "text/plain") if not set or is invalid.
        if request.headers.get_content_type() != headers.MULTIPART_FORM_DATA:
            raise BadRequestError(f"Invalid content-type: '{request.headers.get_content_type()}'.")

        boundary = request.headers.get_boundary()

        if not boundary:
            raise BadRequestError("Boundary not defined.")

        fields = self.read_multipart_form_data(request.rfile, request.content_length, boundary)

        for field in fields:
            arguments[field.name] = self.decode_multipart_form_data(field, endpoint)

        return arguments

    @classmethod
    def decode_multipart_form_data(cls, field: MultiPartFormDataField, endpoint: Endpoint):
        field_name = field.name
        logger.debug("Decoding multipart/form-data '%s'." % field_name)

        try:
            parameter = endpoint.parameters[field_name]
        except KeyError as err:
            raise BadRequestError(
                f"{endpoint.name}() got unexpected parameter: {field_name}"
            ) from err

        content_type = field.content_type

        if not content_type:
            raise BadRequestError(
                f"Multipart/form-data field '{field_name}' is missing 'content-type'. Content-type "
                "is needed to select the correct codec to decode the field data."
            )

        logger.debug("Content-type of '%s' field: '%s'.", field_name, content_type)
        codec = parameter.get_codec_by_content_type(content_type)
        logger.debug("Using %s to decode '%s'.", codec, field_name)
        return codec.decode(field.data, content_type)

    @classmethod
    def read_multipart_form_data(
        cls, rfile: BinaryIO, length: int, boundary: str
    ) -> list[MultiPartFormDataField]:
        """
        Example:
            b'--40c00dbb9994e1de1cf94bce01c4e734'
            b'Content-Disposition: form-data; name="text"'
            b'Content-Type: application/str'
            b''
            b'Hello world'
            b'--40c00dbb9994e1de1cf94bce01c4e734--'
            b''
        """

        def read_lines(rfile: BinaryIO, length: int) -> list[bytes]:
            bytes_count = 0

            for line in rfile:
                yield line

                bytes_count += len(line)
                if bytes_count >= length:
                    break

        def get_name(text: str) -> Optional[str]:
            # Example:
            #   Content-Disposition: form-data; name="a"; filename="a"
            try:
                return re.search('name="(.+?)"', text).group(1)
            except AttributeError:
                logger.warning("Expecting name field in '%s'.", text)
                return None

        def get_content_type(text: str) -> str:
            return text.split(":")[1].strip()

        fields = []
        name = None
        content_type = None
        delimiter = b"--" + boundary.encode()
        expect_data = False
        data = []

        for line in read_lines(rfile, length):
            # logger.debug(line)

            # Note: this will also catch the end delimiter with trailing dashes ('--').
            if line.startswith(delimiter):
                if expect_data:
                    fields.append(
                        MultiPartFormDataField(
                            name, content_type, b"\r\n".join(data).rstrip()
                        )
                    )
                    data.clear()

                expect_data = False
                continue

            if expect_data:
                data.append(line)
                continue

            if not line or line == b"\r\n":
                expect_data = True
                continue

            text = line.decode().lower()

            if text.startswith(CONTENT_DISPOSITION):
                name = get_name(text)
            elif text.startswith(CONTENT_TYPE):
                content_type = get_content_type(text)

        return fields
