"""NumPy codec to be used with remotecall library.

Usage:
    from remotecall.extracodecs.imagecodec import NumPyCodec
"""
from __future__ import annotations

import typing
from typing import Type

import numpy as np
from numpy.typing import NDArray, DTypeLike

from remotecall import Codec
from remotecall.codecs import T


class NumPyCodec(Codec[NDArray]):
    """NumPy codec.

    Example NumPy codec.
    """

    @classmethod
    def is_matching_content_type(cls, content_type: str) -> bool:
        return content_type.startswith("application/numpy")

    @classmethod
    def is_matching_type(cls, type_: typing.Type) -> bool:
        return type_ == np.ndarray

    @classmethod
    def _get_shape_and_data_type(cls, content_type: str) -> tuple[list, DTypeLike]:
        """Extract shape and dtype from content-type.

        Content-type string is expected to be like "numpy-uint8-1080x1920x3".
        """
        fields = content_type.split("-")
        return (
            [int(dimension) for dimension in fields[2].split("x")],
            np.dtype(fields[1])
        )

    def get_encode_type(self) -> Type:
        return NDArray

    def encode(self, array: T) -> tuple[bytes, str]:
        return array.tobytes(), self._get_content_type(array)

    def decode(self, data: bytes, content_type: str) -> T:
        shape, data_type = self._get_shape_and_data_type(content_type)
        return np.ndarray(shape=shape, dtype=data_type, buffer=data)

    @classmethod
    def _get_content_type(cls, array: NDArray) -> str:
        # Example output: "numpy-uint8-1080x1920x3"
        dtype_name = str(array.dtype)
        shape_name = "x".join(map(str, array.shape))
        return f"application/numpy-{dtype_name}-{shape_name}"
