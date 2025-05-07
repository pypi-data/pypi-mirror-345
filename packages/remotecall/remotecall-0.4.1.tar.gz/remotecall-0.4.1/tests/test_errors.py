import pytest
import threading

from remotecall import Server
from remotecall import BaseClient


class UserError(Exception):
    """User error."""


@pytest.fixture
def server_address():
    return "127.0.0.1", 8000


@pytest.fixture
def server(server_address):
    def raise_runtime_error():
        raise RuntimeError

    def raise_user_error():
        raise UserError("User error")

    with Server(server_address) as server:
        server.expose(raise_runtime_error)
        server.expose(raise_user_error)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        yield server
        server.shutdown()
        server_thread.join()


@pytest.fixture
def client(server_address):
    return BaseClient(server_address)


def test_raise_standard_error(server, client):
    with pytest.raises(RuntimeError):
        client.call("raise_runtime_error")


def test_registered_user_exception(server, client):
    client.register_exception(UserError)

    with pytest.raises(UserError):
        client.call("raise_user_error")

    try:
        client.call("raise_user_error")
    except UserError as error:
        assert str(error) == "User error"


def test_unregistered_user_error(server, client):
    with pytest.raises(RuntimeError):
        client.call("raise_user_error")
