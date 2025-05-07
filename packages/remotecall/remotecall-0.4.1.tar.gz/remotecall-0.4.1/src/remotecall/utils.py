from typing import Type


def is_namedtuple(class_object: Type) -> bool:
    """Is class object a named tuple."""
    try:
        return (
            issubclass(class_object, tuple)
            and hasattr(class_object, "_asdict")
            and hasattr(class_object, "_fields")
        )
    except TypeError:
        # Raised by issubclass incase first argument is not class.
        return False
