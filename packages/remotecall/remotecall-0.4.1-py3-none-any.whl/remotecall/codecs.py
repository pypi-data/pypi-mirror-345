from __future__ import annotations

import abc
import json
from typing import Type
from dataclasses import asdict
from dataclasses import astuple
from dataclasses import is_dataclass
from enum import Enum
import typing
from typing import Any
from typing import Generic
from typing import TypeVar


from .utils import is_namedtuple


APPLICATION_NONE = "application/none"
APPLICATION_BYTES = "application/bytes"
APPLICATION_STR = "application/str"
APPLICATION_INT = "application/int"
APPLICATION_FLOAT = "application/float"
APPLICATION_BOOL = "application/bool"
APPLICATION_DICT = "application/dict"
APPLICATION_LIST = "application/list"
APPLICATION_TUPLE = "application/tuple"
APPLICATION_DATACLASS = "application/dataclass"
APPLICATION_NAMEDTUPLE = "application/namedtuple"
APPLICATION_ENUM = "application/enum"


T = TypeVar("T")


class NotFoundError(Exception):
    pass


class MissingTypeError(Exception):
    pass


class ContentTypeError(Exception):
    pass


class TypeRegistry:
    def __init__(self):
        self._types_by_name: typing.Dict[str, Type] = {}

    def put(self, name: str, item: Type):
        for key, value in self._types_by_name.items():
            if value is item:
                self._types_by_name.pop(key)
                break
        self._types_by_name[name] = item

    def get(self, name: str) -> Type:
        return self._types_by_name[name]


class Codecs:
    def __init__(self, codecs: list[Type[Codec]]):
        self._codecs = codecs

    def register(self, codec: Type[Codec]):
        """Register codec type."""
        if not issubclass(codec, Codec):
            raise ValueError(
                f"Expecting type subclassed from Codec. Got {type(codec)}."
            )

        if codec in self._codecs:
            return

        self._codecs.append(codec)

    def unregister(self, codec: Type[Codec]):
        """Unregister codec type."""
        self._codecs.remove(codec)

    def clear(self):
        """Clear all registered codec types."""
        self._codecs.clear()

    def get_codec_by_value(self, obj: Any) -> Codec:
        """Get codec by Python object."""
        for codec in self._codecs:
            if codec.is_matching_type(type(obj)):
                return codec.create_by_value(obj)

        raise NotFoundError(f"No matching codec found for object: {obj}")

    def get_codec_by_type(self, class_object: Type) -> Codec:
        """Create codec by Python type."""
        for codec in self._codecs:
            if codec.is_matching_type(class_object):
                return codec.create_for_type(class_object)

        raise NotFoundError(f"No matching codec found for type: {class_object}")

    def get_codec_by_content_type(self, content_type: str) -> Codec:
        """Create codec by content-type."""
        for codec in self._codecs:
            if codec.is_matching_content_type(content_type):
                return codec.create_by_content_type(content_type)

        raise NotFoundError(f"No matching codec found for content-type: {content_type}")


class Codec(abc.ABC, Generic[T]):
    CONTENT_TYPE = ""

    subclasses: list[Type[Codec]] = []
    _type_registry: TypeRegistry = TypeRegistry()

    def __init_subclass__(cls, **kwargs):
        Codec.subclasses.append(cls)
        cls._type_registry = TypeRegistry()

    @classmethod
    def register_type(cls, name: str, class_object: Type):
        """Register a class object.

        Codec can use registered class object to encode and decode this type of objects.

        For example, registering Enum, dataclass or namedtuple makes it possible to use these
        as arguments or return types.
        """
        # HTTP header names are not case sensitive.
        # See https://www.rfc-editor.org/rfc/rfc9110.html#name-field-names.
        #
        #   Field names are case-insensitive and ought to be registered within the "Hypertext
        #   Transfer Protocol (HTTP) Field Name Registry"; see Section 16.3.1.
        #
        cls._type_registry.put(name.lower(), class_object)

    @classmethod
    def get_registered_type(cls, name: str) -> Type:
        """Get registered type by name."""
        # HTTP header names are not case sensitive.
        # See https://www.rfc-editor.org/rfc/rfc9110.html#name-field-names.
        #
        #   Field names are case-insensitive and ought to be registered within the "Hypertext
        #   Transfer Protocol (HTTP) Field Name Registry"; see Section 16.3.1.
        #
        try:
            return cls._type_registry.get(name.lower())
        except KeyError:
            raise MissingTypeError(f"No type registered with name '{name}'.")

    @classmethod
    def create_by_value(cls, instance: T) -> Codec:
        """Create codec by Python object."""
        return cls.create_for_type(class_object=type(instance))

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        """Create codec by content type."""
        return cls()

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        """Create codec for a type."""
        return cls()

    @classmethod
    @abc.abstractmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        """Is codec matching with the given class object."""

    @classmethod
    def is_matching_content_type(cls, content_type: str) -> bool:
        """Is codec matching with content-type."""
        return cls.CONTENT_TYPE == content_type

    def get_encode_type(self) -> Type:
        """Get the type of the encoded object."""
        return self.get_decode_type()

    def get_decode_type(self) -> Type:
        """Get the class object (type) decoded from the received byte data."""
        return self.__orig_class__.__args__[0]

    @abc.abstractmethod
    def encode(self, obj: T) -> tuple[bytes, str]:
        """Encode object as bytes."""

    @abc.abstractmethod
    def decode(self, data: bytes, content_type: str) -> T:
        """Decode bytes as object."""

    @classmethod
    def check_content_type(cls, expected: str, tested: str):
        if expected != tested:
            raise ContentTypeError(
                f"Mismatching content-type. Expecting '{expected}' but got '{tested}'."
            )

    @classmethod
    def check_type(cls, expected: Type, tested: Type):
        if expected != tested:
            raise TypeError(
                f"Mismatching type. Expecting '{expected}' but got '{tested}'."
            )


# See https://stackoverflow.com/a/68283326.
NoneType = type(None)


class NoneCodec(Codec[NoneType]):
    CONTENT_TYPE = APPLICATION_NONE

    @classmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        return class_object == type(None) or class_object is None

    def get_decode_type(self) -> Type[T]:
        return NoneType

    @classmethod
    def is_matching_content_type(cls, content_type: str) -> bool:
        return content_type == cls.CONTENT_TYPE

    def encode(self, obj: T) -> tuple[bytes, str]:
        return "None".encode(), self.CONTENT_TYPE

    def decode(self, data: bytes, content_type: str) -> None:
        return None


class BytesCodec(Codec[bytes]):
    CONTENT_TYPE = APPLICATION_BYTES

    @classmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        return class_object == bytes

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        return BytesCodec()

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        return BytesCodec()

    def get_decode_type(self) -> Type:
        return bytes

    def encode(self, obj: T) -> tuple[bytes, str]:
        return obj, self.CONTENT_TYPE

    def decode(self, data: bytes, content_type: str) -> bytes:
        return data


class IntCodec(Codec[int]):
    CONTENT_TYPE = APPLICATION_INT

    @classmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        return class_object == int

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        return IntCodec()

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        return IntCodec()

    def get_decode_type(self) -> Type:
        return int

    def encode(self, obj: T) -> tuple[bytes, str]:
        return str(obj).encode(), self.CONTENT_TYPE

    def decode(self, data: bytes, content_type: str) -> int:
        return int(data)


class FloatCodec(Codec[float]):
    CONTENT_TYPE = APPLICATION_FLOAT

    @classmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        return class_object == float

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        cls.check_content_type(cls.CONTENT_TYPE, content_type)
        return FloatCodec()

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        return FloatCodec()

    def get_decode_type(self) -> Type:
        return float

    def encode(self, obj: T) -> tuple[bytes, str]:
        return str(obj).encode(), self.CONTENT_TYPE

    def decode(self, data: bytes, content_type: str) -> float:
        return float(data)


class BoolCodec(Codec[bool]):
    CONTENT_TYPE = APPLICATION_BOOL

    @classmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        return class_object == bool

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        return BoolCodec()

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        return BoolCodec()

    def get_decode_type(self) -> Type:
        return bool

    def encode(self, obj: T) -> tuple[bytes, str]:
        return str(obj).encode(), self.CONTENT_TYPE

    def decode(self, data: bytes, content_type: str) -> bool:
        str_value = data.decode()
        return str_value.lower() == "true"


class StrCodec(Codec[str]):
    CONTENT_TYPE = APPLICATION_STR

    @classmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        return class_object == str

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        return StrCodec()

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        return StrCodec()

    def get_decode_type(self) -> Type:
        return str

    def encode(self, obj: str) -> tuple[bytes, str]:
        return obj.encode(), self.CONTENT_TYPE

    def decode(self, data: bytes, content_type: str) -> str:
        return data.decode()


class DictCodec(Codec[dict]):
    CONTENT_TYPE = APPLICATION_DICT

    @classmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        return class_object == dict

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        return DictCodec()

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        return DictCodec()

    def get_decode_type(self) -> Type:
        return dict

    def encode(self, obj: dict) -> tuple[bytes, str]:
        return json.dumps(obj).encode(), self.CONTENT_TYPE

    def decode(self, data: bytes, content_type: str) -> dict:
        return json.loads(data.decode())


class ListCodec(Codec[list]):
    CONTENT_TYPE = APPLICATION_LIST

    @classmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        return class_object == list

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        return ListCodec()

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        return ListCodec()

    def get_decode_type(self) -> Type:
        return list

    def encode(self, obj: list) -> tuple[bytes, str]:
        return json.dumps(obj).encode(), self.CONTENT_TYPE

    def decode(self, data: bytes, content_type: str) -> list:
        return json.loads(data.decode())


class TupleCodec(Codec[tuple]):
    CONTENT_TYPE = APPLICATION_TUPLE

    @classmethod
    def is_matching_type(cls, class_object: Type[Any]) -> bool:
        return class_object == tuple

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        return TupleCodec()

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        return TupleCodec()

    def get_decode_type(self) -> Type:
        return tuple

    def encode(self, obj: tuple) -> tuple[bytes, str]:
        return json.dumps(obj).encode(), self.CONTENT_TYPE

    def decode(self, data: bytes, content_type: str) -> tuple:
        return tuple(json.loads(data.decode()))


class NamedTupleCodec(Codec[T]):
    CONTENT_TYPE = APPLICATION_TUPLE

    @classmethod
    def is_matching_type(cls, type_: Type[Any]) -> bool:
        return is_namedtuple(type_)

    @classmethod
    def is_matching_content_type(cls, content_type: str) -> bool:
        return content_type in (
            APPLICATION_DICT,
            APPLICATION_TUPLE,
        ) or content_type.startswith(APPLICATION_NAMEDTUPLE)

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        class_name = content_type.partition("-")[2]
        return cls.create_for_type(class_object=cls.get_registered_type(class_name))

    @classmethod
    def create_for_type(cls, class_object: Type[T]) -> Codec:
        """Create codec for type."""
        if cls.CONTENT_TYPE == APPLICATION_DICT:
            return NamedTupleCodec[class_object](dict)  # type: ignore[valid-type]
        if cls.CONTENT_TYPE == APPLICATION_TUPLE:
            return NamedTupleCodec[class_object](tuple)  # type: ignore[valid-type]
        if cls.CONTENT_TYPE == APPLICATION_NAMEDTUPLE:
            return NamedTupleCodec[class_object](class_object)  # type: ignore[valid-type]

        raise RuntimeError(f"Invalid content-type: {cls.CONTENT_TYPE}")

    def __init__(self, encode_type: Type):
        self._encode_type = encode_type

    def get_encode_type(self) -> Type:
        return self._encode_type

    def encode(self, obj: T) -> tuple[bytes, str]:
        content_type = self.CONTENT_TYPE

        if self.CONTENT_TYPE == APPLICATION_DICT:
            data_bytes = json.dumps(obj._asdict()).encode()  # type: ignore[attr-defined]
        elif self.CONTENT_TYPE == APPLICATION_TUPLE:
            data_bytes = json.dumps(obj).encode()
        elif self.CONTENT_TYPE == APPLICATION_NAMEDTUPLE:
            data_bytes = json.dumps(obj._asdict()).encode()  # type: ignore[attr-defined]
            content_type += "-" + obj.__class__.__name__
        else:
            raise RuntimeError(f"Invalid content-type: '{content_type}'")

        return data_bytes, content_type

    def decode(self, data: bytes, content_type: str) -> T:
        class_object = self.get_decode_type()

        if content_type == APPLICATION_TUPLE:
            return class_object(*json.loads(data.decode()))
        elif content_type == APPLICATION_DICT:
            return class_object(**json.loads(data.decode()))
        elif content_type.startswith(APPLICATION_NAMEDTUPLE):
            return class_object(**json.loads(data.decode()))

        raise RuntimeError(
            f"Invalid content-type: '{content_type}'. Expecting '{self.CONTENT_TYPE}'"
        )


class DataClassCodec(Codec[T]):
    CONTENT_TYPE = APPLICATION_DICT

    @classmethod
    def is_matching_type(cls, type_: Type[Any]) -> bool:
        # Matches any dataclass.
        return is_dataclass(type_)

    @classmethod
    def is_matching_content_type(cls, content_type: str) -> bool:
        return content_type in (
            APPLICATION_DICT,
            APPLICATION_TUPLE,
        ) or content_type.startswith(APPLICATION_DATACLASS)

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        class_name = content_type.partition("-")[2]
        return cls.create_for_type(class_object=cls.get_registered_type(class_name))

    @classmethod
    def create_for_type(cls, class_object: Type) -> Codec:
        """Create codec for type."""
        if cls.CONTENT_TYPE == APPLICATION_DICT:
            return DataClassCodec[class_object](dict)  # type: ignore[valid-type]
        elif cls.CONTENT_TYPE == APPLICATION_TUPLE:
            return DataClassCodec[class_object](tuple)  # type: ignore[valid-type]
        elif cls.CONTENT_TYPE == APPLICATION_DATACLASS:
            return DataClassCodec[class_object](class_object)  # type: ignore[valid-type]

        raise ValueError(f"Invalid content-type: {cls.CONTENT_TYPE}")

    def __init__(self, encode_type: Type):
        self._encode_type = encode_type

    def get_encode_type(self) -> Type:
        return self._encode_type

    def encode(self, obj: T) -> tuple[bytes, str]:
        # A data class object is first converted into a dictionary and then send over as bytes.
        # Client sees parameters annotated as dictionaries by default.
        content_type = self.CONTENT_TYPE

        if self.CONTENT_TYPE == APPLICATION_DICT:
            data_bytes = json.dumps(asdict(obj)).encode()  # type: ignore[call-overload]
        elif self.CONTENT_TYPE == APPLICATION_TUPLE:
            data_bytes = json.dumps(astuple(obj)).encode()  # type: ignore[call-overload]
        elif self.CONTENT_TYPE == APPLICATION_DATACLASS:
            data_bytes = json.dumps(asdict(obj)).encode()  # type: ignore[call-overload]
            content_type += "-" + obj.__class__.__name__
        else:
            raise RuntimeError(f"Invalid content-type: '{content_type}'")

        return data_bytes, content_type

    def decode(self, data: bytes, content_type: str) -> T:
        # Codec converts parameter values given as dictionaries (client side) back to original data
        # classes (server side).
        class_object = self.get_decode_type()

        if content_type == APPLICATION_DICT:
            return class_object(**json.loads(data.decode()))
        elif content_type == APPLICATION_TUPLE:
            return class_object(*json.loads(data.decode()))
        elif content_type.startswith(APPLICATION_DATACLASS):
            return class_object(**json.loads(data.decode()))

        raise RuntimeError(f"Invalid content-type: '{content_type}'")


class EnumCodec(Codec[T]):
    CONTENT_TYPE = APPLICATION_STR

    @classmethod
    def is_matching_type(cls, class_object: Type[T]) -> bool:
        try:
            return issubclass(class_object, Enum)
        except TypeError:
            # Raised by issubclass incase first argument is not class.
            return False

    @classmethod
    def is_matching_content_type(cls, content_type: str) -> bool:
        return content_type == APPLICATION_STR or content_type.startswith(
            APPLICATION_ENUM
        )

    @classmethod
    def create_by_content_type(cls, content_type: str) -> Codec:
        class_name = content_type.partition("-")[2]
        return cls.create_for_type(class_object=cls.get_registered_type(class_name))

    @classmethod
    def create_for_type(cls, class_object: Type[Any]) -> Codec:
        """Create codec for type."""
        if cls.CONTENT_TYPE == APPLICATION_STR:
            return EnumCodec[class_object](str)  # type: ignore[valid-type]

        if cls.CONTENT_TYPE == APPLICATION_ENUM:
            return EnumCodec[class_object](class_object)  # type: ignore[valid-type]

        raise RuntimeError(f"Invalid content-type: {cls.CONTENT_TYPE}")

    def __init__(self, encode_type: Type):
        self._encode_type = encode_type

    def get_encode_type(self) -> Type:
        return self._encode_type

    def encode(self, obj: T) -> tuple[bytes, str]:
        data_bytes = obj.name.encode("utf-8")  # type: ignore[attr-defined]

        if self.CONTENT_TYPE == APPLICATION_STR:
            content_type = self.CONTENT_TYPE
        elif self.CONTENT_TYPE == APPLICATION_ENUM:
            content_type = self.CONTENT_TYPE + "-" + obj.__class__.__name__
        else:
            raise RuntimeError(f"Invalid content-type: '{self.CONTENT_TYPE}'")

        return data_bytes, content_type

    def decode(self, data: bytes, content_type: str) -> T:
        class_object = self.get_decode_type()
        return class_object[data.decode("utf-8")]
