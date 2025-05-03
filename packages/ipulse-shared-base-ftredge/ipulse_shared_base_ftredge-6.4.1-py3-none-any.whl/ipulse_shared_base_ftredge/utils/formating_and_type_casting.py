# Created Date: 2024.???.??
# Version: 2025.01.03

import datetime
from typing import  Any, Union, Optional
import json
import traceback
from pprint import pformat


def list_as_strings(*enums):
    """Converts a list of Enum members to their string values."""
    return [str(enum) for enum in enums]

def list_as_lower_strings(*enums):
    """Converts a list of Enum members to their string values."""
    return [str(enum).lower() for enum in enums]

def val_as_str(value):
    """
    Converts various data types to a string representation.
    """
    if isinstance(value, str):
        return value
    elif value is None:
        return ""  # Return an empty string for NoneType
    elif isinstance(value, bool):
        return str(value)  # Return 'True' or 'False' (without quotes)
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, datetime.datetime):
        return value.isoformat()  # Example: '2024-08-16T14:30:00'
    elif isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d')  # Date-only format
    elif isinstance(value, datetime.time):
        return value.strftime('%H:%M:%S')  # Time-only format
    return str(value)  # Fallback to basic string conversion


def any_as_str_or_none(value):
    """
    Converts various data types to a string representation.
    """
    if isinstance(value, str):
        return value
    elif value is None:
        return None  # Return an empty string for NoneType
    elif isinstance(value, bool):
        return str(value)  # Return 'True' or 'False' (without quotes)
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, datetime.datetime):
        return value.isoformat()  # Example: '2024-08-16T14:30:00'
    elif isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d')  # Date-only format
    elif isinstance(value, datetime.time):
        return value.strftime('%H:%M:%S')  # Time-only format
    try:
        # Handle collections and complex objects
        return json.dumps(value, default=str, ensure_ascii=False)
    except Exception as e:
        print(f"Error serializing value {value} of type {type(value)}: {e}")
        return str(value)  # Fallback to basic string conversion in case of failure


def stringify_multiline_msg(msg: Union[str, dict, set, Any]) -> str:
    """
    Format multiline messages for better readability in logs.
    Handles dictionaries, sets, and other serializable types.
    """
    try:
        # Use json.dumps for structured types
        if isinstance(msg, (dict, set, list, tuple)):
            return json.dumps(msg if not isinstance(msg, set) else list(msg), indent=2, default=str)
        return str(msg)
    except (TypeError, ValueError):
        # Fallback to pprint for non-serializable objects
        return pformat(msg, indent=2, width=80)


def format_exception(e: Exception, operation_name: Optional[str]="Not Provided") -> dict:
    """
    Format detailed error message as a dictionary.
    """
    return {
        "Exception operation": operation_name,
        "Type": type(e).__name__,
        "Message": str(e),
        "Caused_by": str(e.__cause__ or ""),
        "Stack Trace": traceback.format_tb(e.__traceback__)  # List of stack trace lines
    }

def to_enum(value: Any, enum_class: type, required: bool = False, default: Any = None, raise_if_unknown:bool=False) -> Optional[Any]:
    """Convert value to enum, handling None and string inputs"""

    if isinstance(value, enum_class):
        return value
    
    if value is None:
        if required:
            if default:
                return default
            raise ValueError(f"Value is required but was None. Enum class: {enum_class}")
        return None

    if isinstance(value, str):
        try:
            return enum_class[value.upper()]
        except Exception:
            pass
    if isinstance(value, (int, str, float)):
        try:
            return enum_class(value)
        except Exception:
            pass
    if raise_if_unknown:
        raise ValueError(f"Unknown value {value} for enum {enum_class} provided")
    return default

def make_json_serializable(data: Any) -> Any:
    """
    Recursively convert data to JSON serializable format.
    Handles:
    - Enums (converts to name)
    - Datetime objects (converts to ISO format)
    - Sets (converts to lists)
    - Custom objects with to_dict() method
    - Nested dicts and lists
    """
    if hasattr(data, 'name'):  # Enum-like objects
        return str(data)
    if isinstance(data, (datetime.datetime, datetime.date, datetime.time)):
        return data.isoformat()
    if isinstance(data, (set, frozenset)):
        return list(data)
    if hasattr(data, 'to_dict'):  # Custom objects with to_dict method
        return make_json_serializable(data.to_dict())
    if isinstance(data, dict):
        return {key: make_json_serializable(value) for key, value in data.items()}
    if isinstance(data, (list, tuple)):
        return [make_json_serializable(item) for item in data]
    if isinstance(data, (int, float, str, bool, type(None))):
        return data
    return str(data)  # Fallback to string representation


