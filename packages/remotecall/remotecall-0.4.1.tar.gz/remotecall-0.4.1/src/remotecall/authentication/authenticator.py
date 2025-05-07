from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from base64 import b64encode
import logging

from http.server import BaseHTTPRequestHandler

from ..exceptions import AuthenticationError


logger = logging.getLogger(__name__)


class Authenticator(ABC):

    @abstractmethod
    def authenticate(self, request: BaseHTTPRequestHandler):
        """Do the authentication."""


class BasicAuthenticator(Authenticator):

    @classmethod
    def _create_key(cls, username: str, password: str) -> str:
        return b64encode(f"{username}:{password}".encode()).decode()

    def __init__(self, username: str, password: str, realm: str = ""):
        self._key = self._create_key(username, password)
        self.realm = realm

    def authenticate(self, request: BaseHTTPRequestHandler):
        logger.debug("Using HTTP basic authentication.")

        authorization = request.headers.get("Authorization")

        if not authorization:
            self._handle_authentication_required(request)
            raise AuthenticationError("Authentication required.")

        if not self._is_authorized(authorization):
            self._handle_authentication_failed(request)
            raise AuthenticationError("Invalid username or password.")

        self._handle_authentication_succeeded(request)

    def _is_authorized(self, authorization: str) -> bool:
        return authorization.endswith(self._key)

    def _handle_authentication_required(self, request: BaseHTTPRequestHandler):
        logger.debug("HTTP basic authentication required.")

        request.send_response(401)
        request.send_header("WWW-Authenticate", f"Basic realm='{self.realm}'")
        request.send_header("Content-type", f"application/AuthenticationError")
        request.send_header("content-length", "0")
        request.end_headers()

    def _handle_authentication_failed(self, request: BaseHTTPRequestHandler):
        logger.debug("HTTP basic authentication failed.")

        request.send_response(401)
        request.send_header("WWW-Authenticate", f"Basic realm='{self.realm}'")
        request.send_header("Content-type", "text/html")
        request.send_header("content-length", "0")
        request.end_headers()

    def _handle_authentication_succeeded(self, request: BaseHTTPRequestHandler):
        logger.debug("HTTP basic authentication successes.")
