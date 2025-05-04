"""
This module provides functions for filtering data.

Functions:
    filter_median: Median filter for multi-dimensional data.
    filter_savgol: Savitsky-Golay filter for multi-dimensional data.
    filter_lowpass: Lowpass filter for multi-dimensional data.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

from typing import List, Union

import numpy as np
from scipy.signal import butter, filtfilt, lfilter, lfiltic, medfilt, savgol_filter

from navlib.math.vmath import max, resample, std


def filter_median(
    data: Union[np.ndarray, List[float]],
    time: Union[np.ndarray, List[float]] = None,
    window: int = 13,
    threshold: Union[float, int] = None,
    patch: bool = False,
    remove_outliers: bool = False,
):
    """
    Median filter for multi-dimensional data. Removes data points that are above
    a threshold, replacing them with nan or interpolated data. The filter is
    applied to each column of the data.

    Args:
        data (Union[np.ndarray, List[float]]): Data to be filtered.
        time (Union[np.ndarray, List[float]]): Time vector.
        window (int, optional): Median filter length. By default 13.
        threshold (Union[float, int], optional): Threshold size defined to remove data. If the
            threashold is not defined STD of the data error is used. By default
            None.
        patch (bool, optional): Patch data. Replace removed data with linear
            interpolation of the points. By default False.
        remove_outliers (bool, optional): Remove outliers. By default False.

    Returns:
        data_filtered (np.ndarray): Filtered data.
        time_filtered (np.ndarray): Filtered time.

    Raises:
        TypeError: If any parameter has an invalid type.
        ValueError: If numeric parameters are non-positive, time is not 1D, or if
            data and time lengths mismatch.

    Examples:
        >>> data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> filtered_data, filtered_time = filter_median(data, window=3)
    """
    # Convert data to numpy array if list
    if isinstance(data, list):
        data = np.array(data)
    if time is not None and isinstance(time, list):
        time = np.array(time)

    # Check the data type
    if not isinstance(data, np.ndarray):
        raise TypeError("Data must be a numpy array or list")
    if time is not None and not isinstance(time, np.ndarray):
        raise TypeError("Time must be a numpy array or list")
    if not isinstance(window, int):
        raise TypeError("Window must be an integer")
    if threshold is not None:
        if not isinstance(threshold, (int, float)):
            raise TypeError("Threshold must be a float or an integer")
        threshold = float(threshold)
    if not isinstance(patch, bool):
        raise TypeError("Patch must be a boolean")
    if not isinstance(remove_outliers, bool):
        raise TypeError("Remove outliers must be a boolean")

    # Make sure data is a 2D array
    if data.ndim == 1:
        data = data[:, np.newaxis]
    # Make sure the time is a 1D array
    if time is not None:
        time = np.squeeze(time)

    # Check values
    if window <= 0:
        raise ValueError("Window must be greater than zero")
    if threshold is not None and threshold <= 0:
        raise ValueError("Threshold must be greater than zero")
    if time is not None:
        if time.ndim != 1:
            raise ValueError("Time must be a 1D array")
        if time.size != data.shape[0]:
            raise ValueError(
                "Time and data must have the same length if single"
                "column or same number of rows if multiple columns"
            )
    else:
        time = np.arange(data.shape[0])

    # Compute the median filter of the data
    data_filtered = np.zeros(data.shape)
    for ix in range(data.shape[1]):
        data_filtered[:, ix] = medfilt(data[:, ix], window)

    # Initialize threshold with default option if not defined
    if threshold is None:
        threshold = 3 * max(std(data - data_filtered, keepdims=True))

    # Find good data points
    good_flags = np.abs(data - data_filtered) < threshold
    good_flags_time = good_flags.all(axis=1)

    # For multi columns remove bad data in all columns
    if good_flags.ndim > 1:
        good_flags = good_flags.all(axis=1)

    # Select good data
    if remove_outliers:
        data_filtered_good = np.zeros((np.sum(good_flags_time), data.shape[1]))
        for ix in range(data.shape[1]):
            data_filtered_good[:, ix] = data[good_flags, ix]
        time_filtered_good = time[good_flags_time]
    else:
        data_filtered_good = np.zeros(data.shape)
        for ix in range(data.shape[1]):
            data_filtered_good[~good_flags, ix] = np.nan
        time_filtered_good = time

    # Patch data
    if patch:
        data_filtered = resample(time, time_filtered_good, data_filtered_good)
        time_filtered = time
    else:
        data_filtered = data_filtered_good
        time_filtered = time_filtered_good

    return data_filtered.squeeze(), time_filtered.squeeze()


def filter_savgol(
    data: Union[np.ndarray, List[float]],
    time: Union[np.ndarray, List[float]] = None,
    window: int = 13,
    polynomial: int = 2,
    threshold: Union[float, int] = None,
    patch: bool = False,
    remove_outliers: bool = False,
):
    """
    Savitsky-Golay filter for multi-dimensional data. Removes data points that
    are above a threshold, replacing them with nan or interpolated data. The
    filter is applied to each column of the data.

    Args:
        data (Union[np.ndarray, List[float]]): Data to be filtered.
        time (Union[np.ndarray, List[float]]): Time vector.
        window (int, optional): Median filter length. By default 25.
        polynomial (int, optional): Polynomial order. By default 2.
        threshold (Union[float, int], optional): Threshold size defined to remove data. If the
            threashold is not defined STD of the data error is used. By default
            None.
        patch (bool, optional): Patch data. Replace removed data with linear
            interpolation of the points. By default False.
        remove_outliers (bool, optional): Remove outliers. By default False.

    Returns:
        data_filtered (np.ndarray): Filtered data.
        time_filtered (np.ndarray): Filtered time.

    Raises:
        TypeError: If any parameter has an invalid type.
        ValueError: If numeric parameters are non-positive, time is not 1D, or if
            data and time lengths mismatch.

    Examples:
        >>> data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> filtered_data, filtered_time = filter_savgol(data, window=3)
    """
    # Convert data to numpy array if list
    if isinstance(data, list):
        data = np.array(data)
    if time is not None and isinstance(time, list):
        time = np.array(time)

    # Check the data type
    if not isinstance(data, np.ndarray):
        raise TypeError("Data must be a numpy array or list")
    if time is not None and not isinstance(time, np.ndarray):
        raise TypeError("Time must be a numpy array or list")
    if not isinstance(window, int):
        raise TypeError("Window must be an integer")
    if not isinstance(polynomial, int):
        raise TypeError("Polynomial must be an integer")
    if threshold is not None:
        if not isinstance(threshold, (int, float)):
            raise TypeError("Threshold must be a float or an integer")
        threshold = float(threshold)
    if not isinstance(patch, bool):
        raise TypeError("Patch must be a boolean")
    if not isinstance(remove_outliers, bool):
        raise TypeError("Remove outliers must be a boolean")

    # Make sure data is a 2D array
    if data.ndim == 1:
        data = data[:, np.newaxis]
    # Make sure the time is a 1D array
    if time is not None:
        time = np.squeeze(time)

    # Check values
    if window <= 0:
        raise ValueError("Window must be greater than zero")
    if polynomial <= 0:
        raise ValueError("Polynomial must be greater than zero")
    if threshold is not None and threshold <= 0:
        raise ValueError("Threshold must be greater than zero")
    if time is not None:
        if time.ndim != 1:
            raise ValueError("Time must be a 1D array")
        if time.size != data.shape[0]:
            raise ValueError(
                "Time and data must have the same length if single"
                "column or same number of rows if multiple columns"
            )
    else:
        time = np.arange(data.shape[0])

    # Compute the savgol filter of the data
    data_filtered = savgol_filter(data, window, polynomial, axis=0)

    # Initialize threshold with default option if not defined
    if threshold is None:
        threshold = 3 * max(std(data - data_filtered, keepdims=True))

    # Find good data points
    good_flags = np.abs(data - data_filtered) < threshold
    good_flags_time = good_flags.all(axis=1)

    # For multi columns remove bad data in all columns
    if good_flags.ndim > 1:
        good_flags = good_flags.all(axis=1)

    # Select good data
    if remove_outliers:
        data_filtered_good = np.zeros((np.sum(good_flags_time), data.shape[1]))
        for ix in range(data.shape[1]):
            data_filtered_good[:, ix] = data[good_flags, ix]
        time_filtered_good = time[good_flags_time]
    else:
        data_filtered_good = np.zeros(data.shape)
        for ix in range(data.shape[1]):
            data_filtered_good[~good_flags, ix] = np.nan
        time_filtered_good = time

    # Patch data
    if patch:
        data_filtered = resample(time, time_filtered_good, data_filtered_good)
        time_filtered = time
    else:
        data_filtered = data_filtered_good
        time_filtered = time_filtered_good

    return data_filtered.squeeze(), time_filtered.squeeze()


def filter_lowpass(
    data: Union[np.ndarray, List[float]],
    sample_freq_hz: Union[int, float] = 1.0,
    cutoff_freq_hz: Union[int, float] = 0.1,
    filter_order: int = 5,
    causality: str = "noncausal",
):
    """
    Lowpass filter for multi-dimensional data for a signal with a given sample
    frequency and cutoff frequency. The filter is applied to each column of the
    data.

    Args:
        data (Union[np.ndarray, List[float]]): Data to be filtered.
        sample_freq_hz (Union[int, float], optional): Sample frequency in Hz. By default 1.0.
        cutoff_freq_hz (Union[int, float], optional): Cutoff frequency in Hz. By default 0.5.
        filter_order (int, optional): Filter order. By default 5.
        causality (str, optional): Causality of the filter. By default "noncausal".

    Returns:
        data_filtered (np.ndarray): Filtered data.

    Raises:
        TypeError: If any parameter has an invalid type.
        ValueError: If numeric parameters are non-positive or if causality is
            invalid.
    Examples:
        >>> data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> filtered_data = filter_lowpass(data)
    """
    # Convert data to numpy array if list
    if isinstance(data, list):
        data = np.array(data)

    # Check the data type
    if not isinstance(data, np.ndarray):
        raise TypeError("Data must be a numpy array or list")
    if not isinstance(sample_freq_hz, (int, float)):
        raise TypeError("Sample frequency must be a float")
    if not isinstance(cutoff_freq_hz, (int, float)):
        raise TypeError("Cutoff frequency must be a float")
    if not isinstance(filter_order, int):
        raise TypeError("Filter order must be an integer")
    if not isinstance(causality, str):
        raise TypeError("Causality must be a string")

    # Make causality lowercase
    causality = causality.lower()

    # Make sure data is a 2D array
    if data.ndim == 1:
        data = data[:, np.newaxis]

    # Check values
    if sample_freq_hz <= 0:
        raise ValueError("Sample frequency must be greater than zero")
    if cutoff_freq_hz <= 0:
        raise ValueError("Cutoff frequency must be greater than zero")
    if filter_order <= 0:
        raise ValueError("Filter order must be greater than zero")
    if causality not in {"causal", "noncausal", "non-causal", "no causal", "acausal"}:
        raise ValueError(
            "Causality must be 'causal', 'noncausal', 'non-causal', 'no causal', or 'acausal'"
        )

    # Filter Design
    causal = True if causality == "causal" else False
    wn = cutoff_freq_hz / (0.5 * sample_freq_hz)

    if wn >= 1 or wn <= 0:
        raise ValueError("The cutoff frequency cannot exceed 1/2 the sample frequency.")

    # Create nth order butterworth filter
    b_matrix, a_matrix = butter(filter_order, wn, btype="low", analog=False)

    # Apply filter to each column of the data
    if causal:
        # Causal filtering. Initialize the filter state using the initial
        # conditions of the filter.
        zi = lfiltic(b_matrix, a_matrix, data[0, :])
        data_filtered, _ = lfilter(
            b_matrix, a_matrix, data, zi=zi[:, np.newaxis], axis=0
        )
    else:
        # Non-causal filtering. Apply the filter forward and backward in time
        # to remove phase shift.
        data_filtered = filtfilt(b_matrix, a_matrix, data, axis=0)

    return data_filtered.squeeze()
