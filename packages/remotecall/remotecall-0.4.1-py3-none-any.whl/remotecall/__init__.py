from __future__ import annotations

import requests
from typing import Optional
from typing import Tuple
import urllib

from .exceptions import ClientError
from .exceptions import ServerError
from .server import Server
from .client import BaseClient
from .codecs import Codec
from .constants import headers
from .constants import statuscodes


def fetch_api(url: str, cert_file: Optional[str] = None, timeout: Optional[float] = None) -> dict:
    """Fetch API definition from URL."""
    hostname, port = _parse_hostname_and_port(url)
    response = requests.get(url=url, verify=cert_file, timeout=timeout)
    definition = response.json()
    definition["address"] = {"hostname": hostname, "port": port}
    return definition


def _parse_hostname_and_port(url: str) -> Tuple[str, int]:
    url_obj = urllib.parse.urlparse(url)
    return url_obj.hostname, url_obj.port


def generate_client(definition: dict, class_name: Optional[str] = None):
    from .clientfactory import ClientFactory
    factory = ClientFactory(definition, class_name=class_name)
    return factory.generate()
