import pytest
import threading

from requests.auth import HTTPBasicAuth

from remotecall import Server
from remotecall.authentication import BasicAuthenticator
from remotecall import BaseClient
from remotecall import ClientError


@pytest.fixture
def server_address():
    return "127.0.0.1", 8000


@pytest.fixture
def server(server_address):
    def foo(a: int, b: str = "foo") -> bool:
        """Foo.

        Test docstring.
        """
        return True

    with Server(server_address) as server:
        server.expose(foo)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        yield server
        server.shutdown()
        server_thread.join()


@pytest.fixture
def client(server_address):
    return BaseClient(server_address)


def test_create_server(server_address):
    Server(server_address)


def test_ssl_enabled(server):
    assert server.ssl_enabled is False


def test_url(server, server_address):
    hostname, port = server_address
    scheme = "https" if server.ssl_enabled else "http"
    assert server.url == f"{scheme}://{hostname}:{port}"


def test_get_enpoint(server):
    ep = server.endpoints["foo"]
    assert ep.name == "foo"


def test_authentication(server, client):
    username = "user"
    password = "pass"

    client.call("foo", a=1)

    authenticator = BasicAuthenticator(username, password)
    server.set_authenticator(authenticator)
    assert server.get_authenticator() == authenticator

    with pytest.raises(ClientError):
        client.call("foo", a=1)

    client.set_authentication(HTTPBasicAuth(username, password))
    client.call("foo", a=1)
