#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shared time utilities to avoid circular imports.
"""

#----------------#
# Import modules #
#----------------#

# Standard modules #
import time
from datetime import datetime, timedelta

# Third-party modules #
import arrow
import numpy as np
import pandas as pd

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_type_str

#------------------#
# Define functions #
#------------------#

def get_datetime_object_unit(dt_obj):
    """
    Get the unit of a datetime object.
    
    Parameters
    ----------
    dt_obj : datetime.datetime, datetime.time, pandas.Timestamp, numpy.datetime64
        The datetime object to get the unit from.
    
    Returns
    -------
    str
        The unit of the datetime object.
        For datetime objects, returns 'us' (microseconds).
        For pandas objects, returns 'ns' (nanoseconds).
        For numpy objects, returns the unit from the dtype string.
    
    Raises
    ------
    TypeError
        If the input is not a supported datetime object type.
    """
    if isinstance(dt_obj, (datetime, time)):
        return "us"  # datetime objects use microsecond precision
    elif isinstance(dt_obj, pd.Timestamp):
        return "ns"  # pandas timestamps use nanosecond precision
    elif isinstance(dt_obj, np.datetime64):
        # Extract unit from dtype string (e.g., "datetime64[ns]" -> "ns")
        dtype_str = str(dt_obj.dtype)
        return dtype_str[dtype_str.find("[") + 1:dtype_str.find("]")]
    else:
        raise TypeError(f"Unsupported datetime object type: {type(dt_obj)}")

def get_nano_datetime(t=None, module="datetime"):
    """
    Get the current or specified time in nanoseconds, formatted as a datetime string.
    
    Parameters
    ----------
    t : int, float, or None, optional
        Time value in nanoseconds. If None, the current time is used.
    module : {"datetime", "time", "pandas", "numpy", "arrow"}, default "datetime"
        Module used to parse the floated time.

    Returns
    -------
    nano_dt_str : str
        The formatted datetime string with nanoseconds.
    """
    if t is not None and not isinstance(t, (float, int)):
        raise TypeError("Time value must either be integer or float.")
    
    # Use current time if none is provided
    if t is None:
        t = time.time_ns()  # Get current time in nanoseconds
    
    # Ensure we handle floating-point times by converting to int
    if isinstance(t, float):
        t = int(str(t).replace(".", ""))
        
    floated_nanotime_str = _nano_floated_time_str(t)
    nano_dt_str = _convert_floated_time_to_datetime(floated_nanotime_str, module)
    return nano_dt_str

def _convert_floated_time_to_datetime(floated_time, module):
    """
    Convert a floated time value to a datetime object with nanosecond precision.

    Parameters
    ----------
    floated_time : float or int
        The floated time value to be converted.
    module : str
        Module used to parse the floated time.

    Returns
    -------
    nano_dt_str : str
        The formatted datetime string with nanoseconds.
    """
    # Convert to float if input is a string
    if isinstance(floated_time, str):
        floated_time = np.float128(floated_time)
        
    # Split into seconds and nanoseconds
    seconds = int(floated_time)
    nanoseconds = int((floated_time - seconds) * 1_000_000_000)

    # Convert the seconds part into a datetime object
    dt = datetime.fromtimestamp(seconds)
    
    # Add the nanoseconds part and return the formatted string
    dt_with_nanos = dt + timedelta(microseconds=nanoseconds / 1_000)
    dt_with_nanos_str = datetime_obj_converter(dt_with_nanos, 
                                             convert_to="str",
                                             dt_fmt_str='%Y-%m-%dT%H:%M:%S')
    nano_dt_str = f"{dt_with_nanos_str}.{nanoseconds:09d}"
    return nano_dt_str

def _nano_floated_time_str(time_ns):
    """
    Convert a time value in nanoseconds to a formatted floating-point time string.

    Parameters
    ----------
    time_ns : int
        Time value in nanoseconds.

    Returns
    -------
    str
        The floating-point time string with nanosecond precision.
    """
    # Convert nanoseconds to seconds and nanoseconds parts
    seconds = time_ns // 1_000_000_000
    nanoseconds = time_ns % 1_000_000_000

    # Format the floating-point time with nanosecond precision
    return f"{seconds}.{nanoseconds:09d}"

def datetime_obj_converter(datetime_obj,
                         convert_to,
                         unit="s",
                         float_class="d", 
                         int_class="int",
                         dt_fmt_str=None):
    """
    Convert a date/time object to another, including float and string representation.
    If float, it represents seconds since the Unix epoch.
    
    Parameters
    ----------
    datetime_obj : object
        The date/time object to be converted.
        Accepted objects by library are:
        - datetime : `datetime.datetime`, 
        - time : `datetime.time`, 
        - numpy : `np.datetime64`, `np.ndarray`,
        - pandas : `pd.Timestamp`, `pd.DataFrame`, `pd.Series`
        - arrow : `arrow`, 
        - struct_time : `time.struct_time`
        
    convert_to : str
        The target type to convert `datetime_obj` to.
        Accepted values depend on the input type.
        For example, if `datetime_obj` is a `datetime`, `convert_to` could be
        `datetime64`, `Timestamp`, etc.
    unit : str
        The date unit for conversion, applicable to certain types.
        Default is `"s"` (seconds).
    float_class : str or numpy float class
        The float precision class. Default is `"d"` (double precision).
    int_class : str or numpy int class
        The integer precision class. Default is `"int"` (signed integer type).
    dt_fmt_str : str
        Format string to convert the date/time object to a string.

    Returns
    -------
    The converted date/time object in the format/type specified by `convert_to`.

    Raises
    ------
    ValueError
        If `convert_to` is not a valid target type for the given `datetime_obj`.
    RuntimeError
        If there is an error during the conversion process.
    """
    # Input validation
    if not convert_to:
        raise ValueError("Argument 'convert_to' not provided.")
    
    # Get the object type's name
    obj_type = get_type_str(datetime_obj, lowercase=True)
    
    # Convert to string if requested
    if convert_to == "str":
        if dt_fmt_str:
            return datetime_obj.strftime(dt_fmt_str)
        return str(datetime_obj)
    
    # Convert to datetime if requested
    if convert_to == "datetime":
        if isinstance(datetime_obj, datetime):
            return datetime_obj
        if isinstance(datetime_obj, pd.Timestamp):
            return datetime_obj.to_pydatetime()
        if isinstance(datetime_obj, np.datetime64):
            return pd.Timestamp(datetime_obj).to_pydatetime()
        if isinstance(datetime_obj, arrow.Arrow):
            return datetime_obj.datetime
        raise ValueError(f"Cannot convert {obj_type} to datetime")
    
    # Convert to pandas Timestamp if requested
    if convert_to == "timestamp":
        if isinstance(datetime_obj, pd.Timestamp):
            return datetime_obj
        if isinstance(datetime_obj, datetime):
            return pd.Timestamp(datetime_obj)
        if isinstance(datetime_obj, np.datetime64):
            return pd.Timestamp(datetime_obj)
        if isinstance(datetime_obj, arrow.Arrow):
            return pd.Timestamp(datetime_obj.datetime)
        raise ValueError(f"Cannot convert {obj_type} to Timestamp")
    
    # Convert to numpy datetime64 if requested
    if convert_to == "datetime64":
        if isinstance(datetime_obj, np.datetime64):
            return datetime_obj
        if isinstance(datetime_obj, (datetime, pd.Timestamp)):
            return np.datetime64(datetime_obj)
        if isinstance(datetime_obj, arrow.Arrow):
            return np.datetime64(datetime_obj.datetime)
        raise ValueError(f"Cannot convert {obj_type} to datetime64")
    
    # Convert to arrow if requested
    if convert_to == "arrow":
        if isinstance(datetime_obj, arrow.Arrow):
            return datetime_obj
        if isinstance(datetime_obj, datetime):
            return arrow.get(datetime_obj)
        if isinstance(datetime_obj, pd.Timestamp):
            return arrow.get(datetime_obj.to_pydatetime())
        if isinstance(datetime_obj, np.datetime64):
            return arrow.get(pd.Timestamp(datetime_obj).to_pydatetime())
        raise ValueError(f"Cannot convert {obj_type} to arrow")
    
    raise ValueError(f"Unsupported conversion target: {convert_to}") 