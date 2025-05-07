from typing import Optional
import logging


logger = logging.getLogger(__name__)


def _get_standard_exceptions() -> list[type[BaseException]]:
    """Get Python standard built-in exceptions."""
    # See also https://docs.python.org/3/library/exceptions.html#exception-hierarchy.
    return [
        GeneratorExit,
        KeyboardInterrupt,
        SystemExit,
        Exception,
        ArithmeticError,
        FloatingPointError,
        OverflowError,
        ZeroDivisionError,
        AssertionError,
        AttributeError,
        BufferError,
        EOFError,
        EnvironmentError,
        IOError,
        OSError,
        BlockingIOError,
        ChildProcessError,
        ConnectionError,
        BrokenPipeError,
        ConnectionAbortedError,
        ConnectionRefusedError,
        ConnectionResetError,
        FileExistsError,
        FileNotFoundError,
        InterruptedError,
        IsADirectoryError,
        NotADirectoryError,
        PermissionError,
        ProcessLookupError,
        TimeoutError,
        ImportError,
        ModuleNotFoundError,
        LookupError,
        IndexError,
        KeyError,
        MemoryError,
        NameError,
        UnboundLocalError,
        ReferenceError,
        RuntimeError,
        NotImplementedError,
        RecursionError,
        StopAsyncIteration,
        StopIteration,
        SyntaxError,
        IndentationError,
        TabError,
        SystemError,
        TypeError,
        ValueError,
        UnicodeError,
        UnicodeDecodeError,
        UnicodeEncodeError,
        UnicodeTranslateError,
        StopIteration,
    ]


def _get_library_exceptions() -> list[type[Exception]]:
    """Get library exceptions."""
    return [
        # Client errors.
        ClientError,
        BadRequestError,
        NotFoundError,
        AuthenticationError,
        ContentLengthRequiredError,
        # Server errors.
        ServerError,
        ServiceUnavailableError,
    ]


class ExceptionRegistry:
    """Exception registry."""

    def __init__(self, class_objects: Optional[list[type[Exception]]] = None):
        """Initialize exception registry."""
        self._classes_by_name: dict[str, type[Exception]] = {}

        if class_objects:
            for error in class_objects:
                self.register(error)

    def register(self, class_object: type[Exception], name: Optional[str] = None):
        """Register an exception class."""
        if not name:
            name = class_object.__name__
        self._classes_by_name[name] = class_object

    def get(self, name: str) -> type[Exception]:
        """Get an exception class."""
        return self._classes_by_name[name]


def create_exception_registry_with_built_in_exceptions() -> ExceptionRegistry:
    """Create an error registry with built-in exceptions.

    Creates an error registry with pre-registered Python and library exceptions.
    """
    built_in_exceptions = _get_library_exceptions() + _get_standard_exceptions()
    return ExceptionRegistry(built_in_exceptions)


class ConnectionTimeoutError(ConnectionError):
    """Raised when a connection fails due a timeout error."""


class ConnectTimeoutError(ConnectionTimeoutError):
    """Failed to establishing a connection in given time.

    Use set_timeout(timeout) to set a proper timeout. Note that connect_timeout
    and read_timeout can be defined as a tuple (connect_timeout, read_timeout).
    """


class ConnectionReadTimeoutError(ConnectionTimeoutError):
    """Failed to read data from a connection within given time out.

    Use set_timeout(timeout) to set a proper timeout. Note that connect_timeout
    and read_timeout can be defined as a tuple (connect_timeout, read_timeout).
    """


class ClientError(Exception):
    """4xx: Client error.

    Error occurred in the server side but should be fixed on the client side.
    For example, a client tried to call a function with incorrect arguments.
    """

    STATUS_CODE = 400

    @property
    def status_code(self) -> int:
        return self.STATUS_CODE


class BadRequestError(ClientError):
    """400: Bad request."""

    STATUS_CODE = 400


class AuthenticationError(ClientError):
    """401: Authentication error."""

    STATUS_CODE = 401


class NotFoundError(ClientError):
    """404: Not found error."""

    STATUS_CODE = 404


class ConflictError(ClientError):
    """409: Conflict error."""

    STATUS_CODE = 409


class ContentLengthRequiredError(ClientError):
    """411: Content length required."""

    STATUS_CODE = 411


class ServerError(Exception):
    """5xx: Server error.

    An error occurred on the server side.
    """

    STATUS_CODE = 500

    @property
    def status_code(self) -> int:
        return self.STATUS_CODE


class ServiceUnavailableError(ServerError):
    """503: Service unavailable."""

    STATUS_CODE = 503
