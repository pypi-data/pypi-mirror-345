from __future__ import annotations

import logging
import typing

from .authenticator import Authenticator
from .authenticator import BasicAuthenticator
from .authenticator import AuthenticationError

if typing.TYPE_CHECKING:
    from ..requesthandler import HTTPRequestHandler


logger = logging.getLogger(__name__)


def authenticate(function):
    def wrapper(request: HTTPRequestHandler, *args, **kwargs):
        server = request.get_server()
        authenticator_ = server.get_authenticator()

        if authenticator_:
            try:
                authenticator_.authenticate(request)
            except AuthenticationError as err:
                logger.warning(err)
                return

        function(request, *args, **kwargs)

    return wrapper
