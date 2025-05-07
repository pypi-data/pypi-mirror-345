from __future__ import annotations

from typing import Any
from typing import Type
from typing import Union
from typing import Optional
import logging
from collections import defaultdict

import requests

from .codecs import Codec
from .codecs import Codecs
from .constants import headers
from .exceptions import ConnectTimeoutError
from .exceptions import ConnectionReadTimeoutError
from .exceptions import create_exception_registry_with_built_in_exceptions


logger = logging.getLogger(__name__)


ConnectTimeout = Union[None, int, float]
ReadTimeout = Union[None, int, float]


class BaseClient:
    DEFAULT_SERVER_ADDRESS = ("localhost", 8000)

    def __init__(self, server_address: tuple[str, int] = DEFAULT_SERVER_ADDRESS):
        self.server_address = server_address
        self._codecs = Codecs(Codec.subclasses)
        self._ssl_enabled = False
        self._cert_file = None
        self._authentication = None
        self._session = requests.Session()
        self._default_timeout: Optional[int] = None  # seconds
        self._timeouts = defaultdict(lambda: self._default_timeout)
        self._exception_registry = create_exception_registry_with_built_in_exceptions()

    @property
    def server_url(self) -> str:
        """Get server URL."""
        host, port = self.server_address
        scheme = "https" if self._ssl_enabled else "http"
        return f"{scheme}://{host}:{port}"

    @property
    def ssl_enabled(self) -> bool:
        """Is SSL enabled."""
        return self._ssl_enabled

    def use_ssl(self, cert_file: str):
        """Enable SSL."""
        self._cert_file = cert_file
        self._ssl_enabled = True

    def set_authentication(self, authentication):
        """Set authentication method."""
        self._authentication = authentication

    def set_timeout(
        self,
        timeout: Union[None, int, float, tuple[ConnectTimeout, ReadTimeout]],
        function: Optional[str] = None,
    ):
        """Set connection timeout in seconds.

        Timeout value is considered as a global connection timeout if the function name is omitted:

            set_timeout(1.0)

        By default, timeout is None.

        Timeout can be set also per function:

            set_timeout(1.0, function_name)

        Connect and read timeouts can be defined apart by using tuple notation instead of scalar:

            set_timeout((connect_timeout, read_timeout))
        """
        if function:
            self._timeouts[function] = timeout
        else:
            self._default_timeout = timeout

    def get_timeout(
        self, function: Optional[str] = None
    ) -> Union[None, int, float, tuple[ConnectTimeout, ReadTimeout]]:
        """Get timeout.

        Works similarly as set_timeout().
        """
        if function not in self._timeouts:
            return self._default_timeout
        return self._timeouts[function]

    def call(self, function: str, **kwargs):
        """Call remote function with arguments."""
        logger.debug("Preparing to call %s.", function)

        url = self._get_url(function)
        multipart_form_data = self._encode_multipart_form_data(fields=kwargs)
        timeout = self.get_timeout(function)

        logger.debug("Sending POST request %s with timeout %s seconds.", url, timeout)

        try:
            response = self._session.post(
                url=url,
                files=multipart_form_data,
                verify=self._cert_file,
                auth=self._authentication,
                timeout=timeout,
            )
        except requests.exceptions.ConnectTimeout as error:
            raise ConnectTimeoutError(
                f"Failed to establish a connection to '{url}' in given timeout ({timeout} seconds). "
                f"Use set_timeout(timeout, function_name) to set the timeout in seconds."
            ) from error
        except requests.exceptions.ReadTimeout as error:
            raise ConnectionReadTimeoutError(
                f"Calling '{function}' took longer than expected ({timeout} seconds). "
                f"Use set_timeout(timeout, function_name) to set the timeout in seconds."
            ) from error
        except requests.exceptions.ConnectionError as error:
            raise ConnectionError(
                f"Failed to call '{function}' due a connection error: {error}"
            ) from error

        logger.debug("Received status code: %s.", response.status_code)

        content_type = self._get_content_type(response)

        if not content_type:
            raise RuntimeError(
                f"Response of calling '{function}' is missing content type."
            )

        if response.status_code < 400:
            return self._get_response_value(response)

        try:
            error_name = content_type.partition("application/")[2]
            error_class = self._exception_registry.get(error_name)
        except KeyError as error:
            logger.error(
                "Undefined error '%s' occurred while calling '%s'."
                % (error_name, function)
            )
            logger.warning("Use 'register_error()' to register user defined errors.")

            self._log_response(response)

            raise RuntimeError(
                "Undefined error '%s' occurred while calling '%s'."
                % (error_name, function)
            )

        raise error_class(response.text)

    def register_type(self, class_object: Type):
        """Register a type class.

        Codecs can use registered class objects to encode and decode that type of objects.

        For example, by registering Enum, dataclass or namedtuple makes it possible to use these
        as arguments or return types.
        """
        codec = self._codecs.get_codec_by_type(class_object)
        codec.register_type(class_object.__name__, class_object)

    def register_exception(
        self, class_object: Type[Exception], name: Optional[str] = None
    ):
        """Register exceptions that may occur while calling server functions."""
        self._exception_registry.register(class_object, name)

    def _get_url(self, command: str) -> str:
        return f"{self.server_url}/{command}"

    def _encode_multipart_form_data(self, fields: dict[str, Any]) -> dict[str, tuple]:
        logger.debug("Encoding multipart/form-data ...")
        form_data = {}

        for name, value in fields.items():
            logger.debug("Get codec for '%s.", type(value))
            codec = self._codecs.get_codec_by_value(value)

            logger.debug("Encoding '%s' with %s.", name, codec)
            encoded_value, content_type = codec.encode(value)
            form_data[name] = (None, encoded_value, content_type)

        return form_data

    @classmethod
    def _log_response(cls, response: requests.Response):
        logger.debug("Response:")
        logger.debug("  status: %s", response.status_code)
        logger.debug("  headers: %s", response.headers)
        logger.debug("  text: %s", response.text)

    def _get_response_value(self, response: requests.Response):
        content_type = self._get_content_type(response)

        if not content_type:
            return response.content

        codec = self._codecs.get_codec_by_content_type(content_type)
        logger.debug("Using %s to decode '%s' response.", codec, content_type)
        return codec.decode(response.content, content_type)

    @classmethod
    def _get_content_type(cls, response: requests.Response) -> str:
        """Get the content type of the response."""
        return response.headers.get(str(headers.CONTENT_TYPE))
