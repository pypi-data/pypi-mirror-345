import json
from datetime import datetime
from uuid import UUID
from typing import Any, Union



SERIALIZED_TYPE_MAP = {
    "datetime": datetime,
    "uuid": UUID,
    "tuple": tuple,
    "bool": bool,
    "int": int,
    "float": float,
    "str": str,
    "list": list,
    "dict": dict,
    "none": None
}
"""Mapping of string type identifiers to corresponding Python types for supported serializations."""


def serialize(value: Any, with_type: bool = False, with_type_str: bool = False) -> Union[bytes, tuple[Any, bytes]]:
    """
    Serialize a supported Python value into a JSON-encoded byte string, 
    embedding its type information for accurate deserialization.

    Supported types: datetime, UUID, tuple, bool, int, float, str, list, dict.

    Args:
        value (Any): The value to serialize. Must be one of the supported types.
        with_type (bool, optional): If True, returns a tuple of (type, serialized_bytes).
        with_type_str (bool, optional): If True and with_type is True, returns the type as a string
            instead of a Python type.

    Returns:
        bytes: The serialized representation of the value.
        tuple[the_type, bytes]: If with_type is True, returns the resolved type (type or str) and the serialized bytes.

    Raises:
        TypeError: If the value is not of a supported type.
    """
    if isinstance(value, datetime):
        data = {"__type__": "datetime", "value": value.isoformat()}
    elif isinstance(value, UUID):
        data = {"__type__": "uuid", "value": str(value)}
    elif isinstance(value, tuple):
        data = {"__type__": "tuple", "value": list(value)}
    elif isinstance(value, bool):
        data = {"__type__": "bool", "value": value}
    elif isinstance(value, (int, float, str)):
        data = {"__type__": type(value).__name__, "value": value}
    elif isinstance(value, (dict, list)):
        data = {"__type__": type(value).__name__, "value": value}
    elif value is None:
        data = {"__type__": 'none', 'value': 'None'}
    else:
        raise TypeError(f"Unsupported value type: {type(value)}")
    
    result = json.dumps(data).encode()
    if with_type:
        if with_type_str:
            the_type = data['__type__']
        else:
            the_type = SERIALIZED_TYPE_MAP[data['__type__']]
        return the_type, result
    else:
        return result


def deserialize(raw: Union[bytes, str], with_type: bool = False, with_type_str: bool = False) -> Union[Any, tuple[Any, Any]]:
    """
    Deserialize a JSON-encoded byte string or string containing type metadata into a Python value.

    The serialized input must include a "__type__" field indicating the original type.

    Args:
        raw (Union[bytes, str]): The raw serialized data as bytes or JSON string.
        with_type (bool, optional): If True, returns a tuple of (type, deserialized_value).
        with_type_str (bool, optional): If True and with_type is True, returns the type as a string
            instead of a Python type.

    Returns:
        value: The deserialized Python value.
        tuple[the_type, value]: If with_type is True, returns the resolved type (type or str) and the deserialized value.

    Raises:
        ValueError: If the serialized data is not properly formatted or missing the "__type__" field.
        TypeError: If the embedded type is not supported for deserialization.
    """
    if isinstance(raw, bytes):
        raw = raw.decode()

    data = json.loads(raw)

    if not isinstance(data, dict) or "__type__" not in data:
        raise ValueError("Missing __type__ metadata in serialized data")

    value_type = data["__type__"]
    value = data["value"]

    if value_type == "datetime":
        result = datetime.fromisoformat(value)
    elif value_type == "uuid":
        result = UUID(value)
    elif value_type == "tuple":
        result = tuple(value)
    elif value_type == "bool":
        result = bool(value)
    elif value_type == "int":
        result = int(value)
    elif value_type == "float":
        result = float(value)
    elif value_type == "str":
        result = str(value)
    elif value_type == "list":
        result = list(value)
    elif value_type == "dict":
        result = dict(value)
    elif value_type == 'none':
        result = None
    else:
        raise TypeError(f"Unsupported deserialization type: {value_type}")
    
    if with_type:
        if with_type_str:
            the_type = value_type
        else:
            the_type = SERIALIZED_TYPE_MAP[value_type]
        return the_type, result
    else:
        return result
