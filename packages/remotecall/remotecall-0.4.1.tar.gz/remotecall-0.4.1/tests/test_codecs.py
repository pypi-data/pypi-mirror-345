import pytest
import enum
from collections import namedtuple
from dataclasses import dataclass

from remotecall import codecs


def test_none_codec():
    codec = codecs.NoneCodec()
    assert codec.get_decode_type() == type(None)
    assert codec.is_matching_type(type(None))
    assert codec.decode(*codec.encode(None)) is None


def test_bytes_codec():
    b = b'a'
    codec = codecs.BytesCodec()
    assert codec.get_decode_type() == bytes
    assert codec.is_matching_type(bytes)
    assert codec.decode(*codec.encode(b)) == b


def test_int_codec():
    codec = codecs.IntCodec()
    assert codec.get_decode_type() == int
    assert codec.is_matching_type(int)
    assert codec.decode(*codec.encode(1)) == 1


def test_float_codec():
    codec = codecs.FloatCodec()
    assert codec.get_decode_type() == float
    assert codec.is_matching_type(float)
    assert codec.decode(*codec.encode(1.1)) == 1.1


def test_bool_codec():
    codec = codecs.BoolCodec()
    assert codec.get_decode_type() == bool
    assert codec.is_matching_type(bool)
    assert codec.decode(*codec.encode(True)) is True
    assert codec.decode(*codec.encode(False)) is False


def test_str_codec():
    codec = codecs.StrCodec()
    assert codec.get_decode_type() == str
    assert codec.is_matching_type(str)
    assert codec.decode(*codec.encode("Hello")) == "Hello"


def test_dict_codec():
    d = {"a": 1}
    codec = codecs.DictCodec()
    assert codec.get_decode_type() == dict
    assert codec.is_matching_type(dict)
    assert codec.decode(*codec.encode(d)) == d


def test_list_codec():
    l = [1, 2, 3]
    codec = codecs.ListCodec()
    assert codec.get_decode_type() == list
    assert codec.is_matching_type(list)
    assert codec.decode(*codec.encode(l)) == l


def test_tuple_codec():
    t = ("a", 1)
    codec = codecs.TupleCodec()
    assert codec.get_decode_type() == tuple
    assert codec.is_matching_type(tuple)
    assert codec.decode(*codec.encode(t)) == t


def test_namedtuple_codec():
    Foo = namedtuple("Foo", "name value")
    codec = codecs.NamedTupleCodec[Foo](str)
    assert codec.get_decode_type() == Foo
    assert codec.is_matching_type(Foo)
    assert codec.decode(*codec.encode(Foo("A", 42))) == Foo("A", 42)


def test_dataclass_codec():
    @dataclass
    class Foo:
        name: str
        value: int

    codec = codecs.DataClassCodec[Foo](str)
    assert codec.is_matching_type(Foo)
    assert codec.decode(*codec.encode(Foo("A", 42))) == Foo("A", 42)


def test_enum_codec():
    class Foo(enum.Enum):
        A = enum.auto()

    codec = codecs.EnumCodec[Foo](str)
    assert codec.get_decode_type() == Foo
    assert codec.is_matching_type(Foo)
    assert codec.decode(*codec.encode(Foo.A)) == Foo.A


def test_get_codec_by_value():
    codecs_obj = codecs.Codecs(codecs.Codec.subclasses)
    codec = codecs_obj.get_codec_by_value(1)
    assert isinstance(codec, codecs.IntCodec)

    with pytest.raises(codecs.NotFoundError):
        codecs_obj.get_codec_by_value(object())


def test_get_codec_by_type():
    codecs_obj = codecs.Codecs(codecs.Codec.subclasses)
    codec = codecs_obj.get_codec_by_type(int)
    assert isinstance(codec, codecs.IntCodec)

    with pytest.raises(codecs.NotFoundError):
        codecs_obj.get_codec_by_type(object)


def test_get_codec_by_content_type():
    from remotecall.codecs import APPLICATION_NONE
    from remotecall.codecs import APPLICATION_BYTES
    from remotecall.codecs import APPLICATION_STR
    from remotecall.codecs import APPLICATION_INT
    from remotecall.codecs import APPLICATION_FLOAT
    from remotecall.codecs import APPLICATION_BOOL
    from remotecall.codecs import APPLICATION_DICT
    from remotecall.codecs import APPLICATION_LIST
    from remotecall.codecs import APPLICATION_TUPLE
    from remotecall.codecs import APPLICATION_DATACLASS
    from remotecall.codecs import APPLICATION_NAMEDTUPLE

    codecs_obj = codecs.Codecs(codecs.Codec.subclasses)
    codec = codecs_obj.get_codec_by_content_type(APPLICATION_INT)
    assert isinstance(codec, codecs.IntCodec)

    assert isinstance(codecs_obj.get_codec_by_content_type(APPLICATION_NONE), codecs.NoneCodec)
    assert isinstance(codecs_obj.get_codec_by_content_type(APPLICATION_BYTES), codecs.BytesCodec)
    assert isinstance(codecs_obj.get_codec_by_content_type(APPLICATION_STR), codecs.StrCodec)
    assert isinstance(codecs_obj.get_codec_by_content_type(APPLICATION_BOOL), codecs.BoolCodec)
    assert isinstance(codecs_obj.get_codec_by_content_type(APPLICATION_INT), codecs.IntCodec)
    assert isinstance(codecs_obj.get_codec_by_content_type(APPLICATION_FLOAT), codecs.FloatCodec)
    assert isinstance(codecs_obj.get_codec_by_content_type(APPLICATION_DICT), codecs.DictCodec)
    assert isinstance(codecs_obj.get_codec_by_content_type(APPLICATION_LIST), codecs.ListCodec)
    assert isinstance(codecs_obj.get_codec_by_content_type(APPLICATION_TUPLE), codecs.TupleCodec)

    with pytest.raises(codecs.MissingTypeError):
        content_type = APPLICATION_DATACLASS + "-FooDataclass"
        assert isinstance(codecs_obj.get_codec_by_content_type(content_type), codecs.DataClassCodec)

        content_type = APPLICATION_DATACLASS + "-"
        assert isinstance(codecs_obj.get_codec_by_content_type(content_type), codecs.DataClassCodec)

        content_type = APPLICATION_DATACLASS
        assert isinstance(codecs_obj.get_codec_by_content_type(content_type), codecs.DataClassCodec)

        content_type = ""
        assert isinstance(codecs_obj.get_codec_by_content_type(content_type), codecs.DataClassCodec)

    with pytest.raises(codecs.MissingTypeError):
        content_type = APPLICATION_NAMEDTUPLE + "-FooNamedtuple"
        assert isinstance(codecs_obj.get_codec_by_content_type(content_type),
                          codecs.NamedTupleCodec)

    with pytest.raises(codecs.NotFoundError):
        codecs_obj.get_codec_by_content_type("")
