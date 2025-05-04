"""
This module provides functions for working with time.

Functions:
    time_now: Returns the current time in microseconds since the epoch in local time.
    time_now_utc: Returns the current time in microseconds since the epoch in UTC.
    utime2datestr: Converts a Unix timestamp to a date string.
    datestr2utime: Converts a date string to a Unix timestamp.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""
import datetime
from typing import List, Union

import numpy as np


def time_interval_indices(
    time: Union[List[float], np.ndarray],
    t0: Union[int, float],
    tn: Union[int, float],
) -> np.ndarray:
    """
    Given a set of timestamps, return the range of indices that is between t0 and tn.
    This function is useful for filtering timestamps within a specific time interval.

    Args:
        time (Union[List[float], np.ndarray]): Non-saturated values as a list of floats or as a numpy array.
        t0 (Union[int, float]): Lower boundary as a float or int.
        tn (Union[int, float]): Upper boundary as a float or int.

    Returns:
        idx_range (Union[List[float], np.ndarray]): Index range between t0 and tn.

    Raises:
        TypeError: If the input time is not a list or numpy array, or if t0 and tn are not int or float.
        ValueError: If the input time is not 1D, if it is empty, or if tn is not greater than t0.
    """
    # Convert to numpy array
    if isinstance(time, list):
        time = np.array(time)

    # Check input type
    if not isinstance(time, np.ndarray):
        raise TypeError("Input time must be a list or numpy array.")
    if not isinstance(t0, (int, float)):
        raise TypeError("t0 must be an int or float.")
    if not isinstance(tn, (int, float)):
        raise TypeError("tn must be an int or float.")

    # Check time array shape
    time = time.squeeze()
    if time.ndim != 1:
        raise ValueError("Input time must be a 1D array or list.")
    if time.shape[0] == 0:
        raise ValueError("Input time must not be empty.")

    # Check if tn is greater than t0
    if tn <= t0:
        raise ValueError("Upper boundary tn must be greater than lower boundary t0.")

    # Get index range
    idx_1 = np.searchsorted(time, np.max([t0, time[0]]), side="left")
    idx_2 = np.searchsorted(time, np.min([tn, time[-1]]), side="right")

    return np.arange(idx_1, idx_2)


def timestamps_make_uniform(timestamps: Union[List[float], np.ndarray]) -> np.ndarray:
    """
    Given a set of timestamps with non-uniform intervals or non-monotonic order,
    return a new set of timestamps with uniform intervals. This new set of timestamps
    will be evenly spaced between the minimum and maximum timestamps of the input.

    Args:
        timestamps (Union[List[float], np.ndarray]): Non-saturated values as a list of floats or as a numpy array.
    Returns:
        timestamps(np.ndarray): A new set of timestamps with uniform intervals.

    Raises:
        TypeError: If the input timestamps is not a list or numpy array.
        ValueError: If the input timestamps is not 1D or if it is empty.
    """
    # Convert to numpy array
    if isinstance(timestamps, list):
        timestamps = np.array(timestamps)

    # Check input type
    if not isinstance(timestamps, np.ndarray):
        raise TypeError("Input timestamps must be a list or numpy array.")

    # Check timestamps shape
    timestamps = timestamps.squeeze()
    if timestamps.ndim != 1:
        raise ValueError("Input timestamps must be a 1D array or list.")
    if timestamps.shape[0] == 0:
        raise ValueError("Input timestamps must not be empty.")

    # Correct timestamps
    timestamps = np.sort(timestamps)
    timestamps = np.linspace(
        np.min(timestamps), np.max(timestamps), num=timestamps.shape[0]
    )
    return timestamps


def time_now() -> float:
    """
    Returns the current time in microseconds since the epoch in local time.

    Returns:
        unix_ms (float): Current time in microseconds since the epoch.

    Examples:
        >>> time_now()
        1590678950000000.0
    """
    t = datetime.datetime.now()
    time_received = t.timestamp() * 1.00e6
    return time_received


def time_now_utc() -> float:
    """
    Returns the current time in microseconds since the epoch in UTC.

    Returns:
        unix_utc_ms (float): Current time in microseconds since the epoch.

    Examples:
        >>> time_now_utc()
        1590678950000000.0
    """
    t = datetime.datetime.now(datetime.timezone.utc)
    time_received = t.timestamp() * 1.00e6
    return time_received


def utime2datestr(
    utime: Union[List[float], np.ndarray, int, float, np.ndarray],
    datefmt: str = "%Y/%m/%d %H:%M:%S",
) -> Union[List[str], str]:
    """
    Converts unix timestamp in microseconds to a date string.

    Args:
        utime (Union[List[float], np.ndarray, int, float]): Unix timestamp in microseconds.
        datefmt (str, optional): Date format. Defaults to "%Y/%m/%d %H:%M:%S".

    Returns:
        data (Union[List[str], str]): Date string or list of date strings.

    Raises:
        TypeError: If the input utime is not a list, numpy array, int, or float.
        ValueError: If the input utime list is empty or if the date format is incorrect.

    Examples:
        >>> utime2datestr(1590678950000000.0)
        '2020/05/28 12:09:10'
    """
    # Convert to numpy array if it's a list
    if isinstance(utime, list):
        utime = np.array(utime)

    # Check input type
    if not isinstance(utime, (np.ndarray, int, float)):
        raise TypeError("Input utime must be a list, numpy array, int, or float.")

    # Check time array shape
    if isinstance(utime, np.ndarray):
        utime = utime.squeeze()
        if utime.ndim != 1:
            raise ValueError("Input utime must be a 1D array or list.")
        if utime.shape[0] == 0:
            raise ValueError("Input utime must not be empty.")
        if utime.shape[0] == 1:
            utime = utime[0]

    # Convert timestamps
    if isinstance(utime, (int, float)):
        t = datetime.datetime.fromtimestamp(utime / 1.00e6, tz=datetime.timezone.utc)
        return t.strftime(datefmt)
    else:
        t = []
        for i in range(utime.shape[0]):
            t.append(
                datetime.datetime.fromtimestamp(
                    utime[i] / 1.00e6, tz=datetime.timezone.utc
                )
            )
            t[i] = t[i].strftime(datefmt)
        return t


def datestr2utime(
    datestr: Union[str, List[str], np.ndarray],
    datefmt: str = "%Y/%m/%d %H:%M:%S",
) -> Union[float, List[float]]:
    """
    Converts date strings to a Unix timestamp in microseconds.

    Args:
        datestr (Union[str, List[str], np.ndarray]): Date string or list of date strings.
        datefmt (str, optional): Date format. Defaults to "%Y/%m/%d %H:%M:%S".

    Returns:
        unix_ms (Union[float, List[float]]): Unix timestamp in microseconds or list of timestamps.

    Raises:
        TypeError: If the input datestr is not a string, list of strings or numpy array.
        ValueError: If the input datestr list is empty or if the date format is incorrect.

    Examples:
        >>> datestr2utime("2020/05/28 12:09:10")
        1590678950000000.0
    """
    # Check input type
    if not isinstance(datestr, (str, list, np.ndarray)):
        raise TypeError(
            "Input datestr must be a string, list of strings or numpy array."
        )
    if isinstance(datestr, np.ndarray):
        datestr = datestr.tolist()

    # Check list length
    if isinstance(datestr, list):
        if len(datestr) == 0:
            raise ValueError("Input datestr list must not be empty.")
        if len(datestr) == 1:
            datestr = datestr[0]

    # Convert to datetime object
    if isinstance(datestr, str):
        t = datetime.datetime.strptime(datestr, datefmt)
        # Force the timezone to UTC
        t = t.replace(tzinfo=datetime.timezone.utc)
        return t.timestamp() * 1.00e6
    else:
        t = []
        for i in range(len(datestr)):
            t.append(datetime.datetime.strptime(datestr[i], datefmt))
            # Force the timezone to UTC
            t[i] = t[i].replace(tzinfo=datetime.timezone.utc)
            t[i] = t[i].timestamp() * 1.00e6
        return t
