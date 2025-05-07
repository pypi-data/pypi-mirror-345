import pytest

from remotecall.client import BaseClient
from remotecall.exceptions import ConnectTimeoutError
from remotecall.exceptions import ConnectionTimeoutError
from remotecall.exceptions import ConnectionReadTimeoutError


def test_set_timeout(server_address):
    c = BaseClient(server_address)

    assert c.get_timeout() is None

    c.set_timeout(0.1)
    assert c.get_timeout() == 0.1

    c.set_timeout((1, 2))
    assert c.get_timeout() == (1, 2)

    assert c.get_timeout(function="foo") == (1, 2)

    c.set_timeout(timeout=3, function="foo")
    assert c.get_timeout(function="foo") == 3


def test_connection_error(server_address):
    c = BaseClient(server_address)
    c.set_timeout(0.1)

    with pytest.raises(ConnectionError):
        c.call("no_arguments")


def test_connect_timeout_error(server, server_address):
    c = BaseClient(server_address)
    c.set_timeout((0.0001, 2.0))

    # ConnectionError ← ConnectionTimeoutError ← ConnectTimeoutError

    # with pytest.raises(ConnectionError):
    #    c.call("no_arguments")

    # with pytest.raises(ConnectionTimeoutError):
    #    c.call("no_arguments")

    # with pytest.raises(ConnectTimeoutError):
    #    c.call("no_arguments")


def test_connection_timeout_error(server, server_address):
    c = BaseClient(server_address)
    c.set_timeout((0.1, 0.5))

    # with pytest.raises(ConnectionError):
    #    c.call("sleep", seconds=1.0)

    # with pytest.raises(ConnectionTimeoutError):
    #     c.call("sleep", seconds=1.0)

    # with pytest.raises(ConnectionReadTimeoutError):
    #    c.call("sleep", seconds=1.0)
