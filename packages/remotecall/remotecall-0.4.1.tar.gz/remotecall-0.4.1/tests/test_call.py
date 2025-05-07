import pytest
import threading

from remotecall import Server
from remotecall.client import BaseClient


@pytest.fixture
def server_address():
	return ("localhost", 8000)


@pytest.fixture
def server(server_address):
	def no_arguments():
		pass

	def with_str_argument(a: str, b: str = "foo"):
		pass

	def with_bytes_argument(a: bytes):
		pass

	def with_int_argument(a: int):
		pass

	def with_float_argument(a: float):
		pass

	def with_bool_argument(a: bool):
		pass

	def with_list_argument(a: list):
		pass

	def with_tuple_argument(a: tuple):
		pass

	def with_dict_argument(a: dict):
		pass

	def with_two_arguments_and_return_value(a: int, b: int) -> int:
		return a + b

	def no_arguments_with_return_value() -> int:
		return 1

	with Server(server_address) as server:
		server.expose(no_arguments)
		server.expose(with_str_argument)
		server.expose(with_bytes_argument)
		server.expose(with_int_argument)
		server.expose(with_float_argument)
		server.expose(with_bool_argument)
		server.expose(with_list_argument)
		server.expose(with_tuple_argument)
		server.expose(with_dict_argument)
		server.expose(no_arguments_with_return_value)
		server.expose(with_two_arguments_and_return_value)

		server_thread = threading.Thread(target=server.serve_forever)
		server_thread.daemon = True
		server_thread.start()
		yield server
		server.shutdown()
		server_thread.join()


@pytest.fixture
def client(server_address):
	return BaseClient(server_address)


def test_register_callable(server_address):
	def foo():
		pass

	server = Server(server_address)
	server.expose(foo)


def test_register_callable_with_name(server_address):
	def foo():
		pass

	server = Server(server_address)
	server.expose(foo, "foo")


def test_unregister_callable(server_address):
	def foo():
		pass

	server = Server(server_address)
	server.expose(foo, "foo")


def test_call_without_arguments(server, client):
	client.call("no_arguments")


def test_cal_with_str_argument(server, client):
	client.call("with_str_argument", a="test")

def test_cal_with_bytes_argument(server, client):
	client.call("with_bytes_argument", a=b'a')


def test_call_with_float_argument(server, client):
	client.call("with_float_argument", a=1.0)


def test_call_with_int_argument(server, client):
	client.call("with_int_argument", a=1)


def test_call_with_bool_argument(server, client):
	client.call("with_bool_argument", a=True)


def test_call_with_list_argument(server, client):
	client.call("with_list_argument", a=[])


def test_call_with_tuple_argument(server, client):
	client.call("with_tuple_argument", a=())


def test_call_with_dict_argument(server, client):
	client.call("with_dict_argument", a=dict())


def test_calling_without_arguments_with_return_value(server, client):
	assert client.call("no_arguments_with_return_value") == 1, "Expecting 1 as return value."


def test_calling_with_two_arguments_and_return_value(server, client):
	assert (client.call("with_two_arguments_and_return_value", a=1, b=2) == 3,
								"Expecting 3 as return value")
