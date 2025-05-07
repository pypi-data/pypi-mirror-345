from __future__ import annotations

import http.server
import logging
import typing
from typing import Optional
import inspect
from .endpoint import Endpoint
from .requesthandler import HTTPRequestHandler
from .codecs import Codec
from .codecs import Codecs
from .authentication import Authenticator


logger = logging.getLogger(__name__)


class Server(http.server.ThreadingHTTPServer):
    """Server."""

    def __init__(self, server_address: tuple[str, int]):
        super().__init__(
            server_address=server_address, RequestHandlerClass=HTTPRequestHandler
        )
        self._ssl_enabled = False
        self._authenticator: Optional[Authenticator] = None
        self.codecs = Codecs(Codec.subclasses)
        self.endpoints: typing.Dict[str, Endpoint] = {}

    @property
    def url(self) -> str:
        """Server URL."""
        hostname, port = self.server_address
        scheme = "https" if self.ssl_enabled else "http"
        return f"{scheme}://{hostname}:{port}"

    @classmethod
    def _create_endpoint(cls, callable: typing.Callable, name: str = None):
        """Create endpoint."""
        if not isinstance(callable, typing.Callable):
            raise ValueError(f"Expecting callable but got '{callable}'.")

        if not inspect.isroutine(callable):
            if not name:
                name = callable.__name__
            # Expecting a callable to be class implementing __call__.
            return cls._create_endpoint(getattr(callable, "__call__"), name)

        if not name:
            try:
                name = callable.__name__
            except AttributeError as err:
                logger.warning(
                    "Endpoint name is optional if the value can be read from "
                    "the provided function by calling function.__name__."
                )
                raise ValueError(
                    "Endpoint name not provided and exposed function raised the "
                    f"following error when calling function.__name__: {err}"
                ) from err

        return Endpoint(name, callable)

    def expose(self, function: typing.Callable, name: str = None):
        """Expose a function with given name.

        Name of the callable shall be used if name is not given. The name is resolved by calling
        __name__ of the callable.
        """
        logger.debug("Exposing %s ...", function)

        endpoint = self._create_endpoint(function, name)
        endpoint.setup(self.codecs)
        self.endpoints[endpoint.name] = endpoint

    @property
    def ssl_enabled(self) -> bool:
        """Is SLL enabled."""
        return self._ssl_enabled

    def use_ssl(self, cert_file: str, key_file: str, password=None):
        """Use SSL.

        Use SSL to secure server to client transactions.
        """
        import ssl

        logger.debug("Setting up SSL context.")
        logger.debug("  Certificate file: %s", cert_file)
        logger.debug("  Key file: %s", key_file)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.check_hostname = False
        context.load_cert_chain(certfile=cert_file, keyfile=key_file, password=password)

        self.socket = context.wrap_socket(self.socket, server_side=True)
        self._ssl_enabled = True

        logger.debug("SSL enabled.")

    def set_authenticator(self, authenticator: Authenticator):
        """Set authenticator."""
        self._authenticator = authenticator

    def get_authenticator(self) -> Authenticator:
        """Get authenticator."""
        return self._authenticator
