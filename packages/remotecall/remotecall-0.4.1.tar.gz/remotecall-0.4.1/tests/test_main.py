import pytest

from remotecall import Server
from remotecall.__main__ import main


def test_fetch_api(server: Server):
    main(["fetch_api", server.url])


def test_generate_client(server: Server):
    main(["generate_client", server.url])
