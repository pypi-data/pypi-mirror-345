"""
This module provides a set of functions to perform operations in arrays as vectors
or matrices and as lists.

Functions:
    norm: Returns the norm of a vector or matrix.
    normalize: Returns the normalized vector or matrix.
    mean: Returns the mean of a vector or matrix.
    median: Returns the median of a vector or matrix.
    std: Returns the standard deviation of a vector or matrix.
    min: Returns the minimum value of a vector or matrix.
    max: Returns the maximum value of a vector or matrix.
    print_stats: Prints the statistics of a vector or matrix.
    remove_offset: Removes a constant offset from a vector or matrix.
    remove_mean: Removes the mean from a vector or matrix.
    remove_median: Removes the median from a vector or matrix.
    difference: Returns the difference of a vector or matrix.
    derivative: Returns the derivative of a vector or matrix.
    resample: Resamples a signal to a new time vector.
    distance_traveled: Returns the distance traveled by a vector or matrix.
    saturate: Saturates a vector or matrix.
    wrap360: Wraps an input of angles between 0 and 360 degrees.
    wrap180: Wraps an input of angles between -180 and 180 degrees.
    wrap2pi: Wraps an input of angles between 0 and 2pi radians.
    wrap1pi: Wraps an input of angles between -pi and pi radians.
    unwrap2pi: Unwraps an input of angles wrapped between 0 and 2pi radians.
    unwrap1pi: Unwraps an input of angles wrapped between -pi and pi radians.
    unwrap360: Unwraps an input of angles wrapped between 0 and 360 degrees.
    unwrap180: Unwraps an input of angles wrapped between -180 and 180 degrees.
    wrapunwrap: Wraps and unwraps an input of angles between 0 and 2pi radians.
    wrapunwrap360: Wraps and unwraps an input of angles between 0 and 360 degrees.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

from typing import Iterable, List, Union
from warnings import warn

import numpy as np

from navlib.time import time_interval_indices


def norm(
    mat: Union[np.ndarray, List[float]], keepdims: bool = False
) -> Union[float, np.ndarray]:
    """
    Returns the norm of a vector or matrix. If the input is a matrix, the norm
    is calculated for each row.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        keepdims (bool): If True, the output is the same shape as the input. If
            False, the output is a row vector.

    Returns:
        Union[float, np.ndarray]: Norm of the vector or matrix. If the input is
            a vector, a float is returned. If the input is a matrix, the norm of
            each column is returned as a row vector

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> norm = np.array([1, 2, 3])
        >>> print(norm)
        3.7416573867739413
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    # Squeeze the matrix if it has only one row or column
    mat = np.squeeze(mat)

    if mat.ndim == 1:
        return np.linalg.norm(mat)
    else:
        return np.linalg.norm(mat, axis=1, keepdims=keepdims)


def normalize(mat: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Returns the normalized vector or matrix.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.

    Returns:
        np.ndarray: Normalized vector or matrix.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print(normalize(vec))
        [0.26726124 0.53452248 0.80178373]
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    if mat.ndim == 1:
        return mat / norm(mat)
    else:
        return mat / norm(mat, keepdims=True)


def mean(mat: Union[np.ndarray, List[float]], keepdims: bool = False) -> np.ndarray:
    """
    Returns the mean of a vector or matrix. If the input is a matrix, the mean
    is calculated for each column.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        keepdims (bool): If True, the output is the same shape as the input. If
            False, the output is a row vector.

    Returns:
        np.ndarray: Mean of the vector or matrix. If the input is a vector, a
            float is returned. If the input is a matrix, the mean of each column
            is returned as a row vector.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print(mean(vec))
        2.0
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    # Squeeze the matrix if it has only one row or column
    mat = np.squeeze(mat)

    return np.mean(mat, axis=0, keepdims=keepdims)


# TODO: Add test and header documentation
def transpose(mat: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Returns the transpose of a vector or matrix. The input can be either 2D or
    3D.
    For 3D arrays einsum is used for better performance

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.

    Returns:
        np.ndarray: Transpose of the vector or matrix

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([[1, 2], [3, 4]])
        >>> print(transpose(vec))
        [[1  3] [2  4]]

        >>> mat = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
        >>> print(transpose(mat))
        [[[1  3] [5  7]] [[2  4] [6  8]]]
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")
    mat = np.array(mat) if isinstance(mat, list) else mat
    if mat.ndim > 3:
        raise ValueError("The dimension of the array must be up to 3D")

    # Squeeze the matrix if it has only one row or column
    if mat.ndim in [1, 2]:
        return mat.T
    else:
        return np.einsum("ijk->ikj", mat)


def median(mat: Union[np.ndarray, List[float]], keepdims: bool = False) -> np.ndarray:
    """
    Returns the median of a vector or matrix. If the input is a matrix, the
    median is calculated for each column.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        keepdims (bool): If True, the output is the same shape as the input. If
            False, the output is a row vector.

    Returns:
        np.ndarray: Median of the vector or matrix. If the input is a vector, a
            float is returned. If the input is a matrix, the median of each column
            is returned as a row vector.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print(median(vec))
        2.0
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    # Squeeze the matrix if it has only one row or column
    mat = np.squeeze(mat)

    return np.median(mat, axis=0, keepdims=keepdims)


def std(mat: Union[np.ndarray, List[float]], keepdims: bool = False) -> np.ndarray:
    """
    Returns the standard deviation of a vector or matrix. If the input is a
    matrix, the standard deviation is calculated for each column.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        keepdims (bool): If True, the output is the same shape as the input. If
            False, the output is a row vector.

    Returns:
        np.ndarray: Standard deviation of the vector or matrix. If the input is
            a vector, a float is returned. If the input is a matrix, the standard
            deviation of each column is returned as a row vector.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print(std(vec))
        0.816496580927726
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    # Squeeze the matrix if it has only one row or column
    mat = np.squeeze(mat)

    return np.std(mat, axis=0, keepdims=keepdims)


def min(mat: Union[np.ndarray, List[float]], keepdims: bool = False) -> np.ndarray:
    """
    Returns the minimum value of a vector or matrix. If the input is a matrix,
    the minimum value is calculated for each column.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        keepdims (bool): If True, the output is the same shape as the input. If
            False, the output is a row vector.

    Returns:
        np.ndarray: Minimum value of the vector or matrix. If the input is a
            vector, a float is returned. If the input is a matrix, the minimum
            value of each column is returned as a row vector.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print(min(vec))
        1
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    # Squeeze the matrix if it has only one row or column
    mat = np.squeeze(mat)

    return np.min(mat, axis=0, keepdims=keepdims)


def max(mat: Union[np.ndarray, List[float]], keepdims: bool = False) -> np.ndarray:
    """
    Returns the maximum value of a vector or matrix. If the input is a matrix,
    the maximum value is calculated for each column.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        keepdims (bool): If True, the output is the same shape as the input. If
            False, the output is a row vector.

    Returns:
        np.ndarray: Maximum value of the vector or matrix. If the input is a
        vector, a float is returned. If the input is a matrix, the maximum value
        of each column is returned as a row vector.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print(max(vec))
        3
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    # Squeeze the matrix if it has only one row or column
    mat = np.squeeze(mat)

    return np.max(mat, axis=0, keepdims=keepdims)


def print_stats(mat: Union[np.ndarray, List[float]]) -> None:
    """
    Prints the statistics of a vector or matrix.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print_stats(vec)
        Mean: 2.00
        Median: 2.00
        Standard deviation: 0.82
        Min: 1.00
        Max: 3.00
        Norm: 3.74
        MinMax: 2.00
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    if isinstance(mat, list):
        mat = np.array(mat)

    if mat.ndim > 1:
        print("Mean:   " + ", ".join("%.2f" % f for f in mean(mat)))
        print("Median: " + ", ".join("%.2f" % f for f in median(mat)))
        print("Standard deviation: " + ", ".join("%.2f" % f for f in std(mat)))
        print("Min: " + ", ".join("%.2f" % f for f in min(mat)))
        print("Max: " + ", ".join("%.2f" % f for f in max(mat)))
        print("Norm: " + ", ".join("%.2f" % f for f in norm(mat)))
        print("MinMax: " + ", ".join("%.2f" % f for f in (max(mat) - min(mat))))
    else:
        print("Mean:   %.2f" % mean(mat))
        print("Median: %.2f" % median(mat))
        print("Standard deviation: %.2f" % std(mat))
        print("Min: %.2f" % min(mat))
        print("Max: %.2f" % max(mat))
        print("Norm: %.2f" % norm(mat))
        print("MinMax: %.2f" % (max(mat) - min(mat)))


def remove_offset(
    mat: Union[np.ndarray, List[float]],
    offset: Union[float, int, np.ndarray, List[float]],
) -> np.ndarray:
    """
    Removes a constant offset from a vector or matrix.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        offset (Union[float, int, np.ndarray, List[float]]): Offset to remove.

    Returns:
        np.ndarray: Vector or matrix with the offset removed.

    Raises:
        TypeError: If the input is not a numpy array or a list.
        TypeError: If the offset is not a number or an array.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> offset = 2
        >>> print(remove_offset(vec, offset))
        [-1  0  1]
    """
    if isinstance(mat, list):
        mat = np.array(mat)
    if not isinstance(mat, np.ndarray):
        raise TypeError("Input must be a numpy array or a list.")
    if isinstance(offset, list):
        offset = np.array(offset)
    if not isinstance(offset, (int, float, np.ndarray)):
        raise TypeError("Offset must be a number or an array.")
    if mat.ndim == 1 and isinstance(offset, np.ndarray) and offset.ndim > 1:
        raise TypeError("Offset must be a number or a 1D array for 1D input.")
    if mat.ndim == 2 and isinstance(offset, np.ndarray):
        offset = offset.squeeze()
        if offset.ndim > 1:
            raise TypeError("Offset must be a number or a 1D array for 2D arrays.")
    return mat - offset


def remove_mean(mat: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Removes the mean from a vector or matrix. If the array is 2D, the mean
    is calculated for each column.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.

    Returns:
        np.ndarray: Vector or matrix with the mean removed.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print(remove_mean(vec))
        [-1.  0.  1.]
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    return mat - mean(mat, keepdims=True)


def remove_median(mat: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Removes the median from a vector or matrix. If the array is 2D, the median
    is calculated for each column.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.

    Returns:
        np.ndarray: Vector or matrix with the median removed.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print(remove_median(vec))
        [-1.  0.  1.]
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    return mat - median(mat, keepdims=True)


def difference(mat: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Returns the difference of a vector or matrix. If the input is a matrix, the
    difference is calculated within each column.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.

    Returns:
        Union[np.ndarray, List[float]]: Difference of the vector or matrix.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> print(difference(vec))
        [1 1]
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    return np.diff(mat, axis=0, n=1)


def derivative(
    mat: Union[np.ndarray, List[float]], time: Union[np.ndarray, List[float]]
) -> np.ndarray:
    """
    Returns the derivative of a vector or matrix.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        time (Union[np.ndarray, List[float]]): Time vector.

    Returns:
        Union[np.ndarray, List[float]]: Derivative of the vector or matrix.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> time = np.array([1, 2, 3])
        >>> print(derivative(vec, time))
        [1. 1.]
    """
    # Convert to lists
    if isinstance(mat, list):
        mat = np.array(mat)
    if isinstance(time, list):
        time = np.array(time)

    # Check for data type
    if not isinstance(mat, np.ndarray):
        raise TypeError("Input must be a numpy array or a list.")

    if not isinstance(time, np.ndarray):
        raise TypeError("Input must be a numpy array or a list.")

    # Shape check
    mat = np.squeeze(mat)
    if mat.ndim > 2:
        raise ValueError("The dimension of the mat array must be up to 2D")
    time = time.squeeze()
    if time.ndim != 1:
        raise ValueError("The time array must be exactly 1D")
    if time.shape[0] != mat.shape[0]:
        raise ValueError(
            "The time vector must have the same number of rows as the input matrix."
        )

    time_diff = difference(time)
    mat_diff = difference(mat)

    if mat.ndim == 1:
        return mat_diff / time_diff
    else:
        # If the input is a matrix, compute the derivative for each column
        return np.array([mat_diff[:, i] / time_diff for i in range(mat.shape[1])]).T


def resample(
    x: Union[np.ndarray, List[float]],
    xp: Union[np.ndarray, List[float]],
    fp: Union[np.ndarray, List[float]],
) -> np.ndarray:
    """
    Resamples a signal to a new time vector. If the new time vector is not within
    the range of the old time vector, the new time vector is truncated to the range of
    the old time vector.

    Args:
        x (Union[np.ndarray, List[float]]): New time vector, as a 1-D sequence of
            k floats.
        xp (Union[np.ndarray, List[float]]): Old time vector, as a 1-D sequence
            of n floats.
        fp (Union[np.ndarray, List[float]]): Signal to resample, as a 1-D sequence
            of n floats or as a nxm array, where n is the number of time steps and m
            is the number of signals.

    Returns:
        np.ndarray: Resampled signal, as a 1-D sequence of k floats or as a kxm
        array, where k is the number of time steps and m is the number of signals.

    Raises:
        TypeError: If the input x, xp or fp is not a numpy array or a list.
        ValueError: If the input xp or x is not a 1-D sequence of n floats.
        ValueError: If the number of samples in the old time vector and the signal do not match.
        ValueError: If the new time vector is not within the range of the old time vector.
        ValueError: Time series must be monotonically increasing.

    Examples:
        >>> x = np.arange(0, 10, 0.1)
        >>> xp = np.arange(0, 10, 1)
        >>> fp = np.sin(xp)
        >>> print(resample(x, xp, fp))
    """
    # Check for data type
    if not isinstance(x, (np.ndarray, list)):
        raise TypeError("Input x must be a numpy array or a list.")
    if not isinstance(xp, (np.ndarray, list)):
        raise TypeError("Input xp must be a numpy array or a list.")
    if not isinstance(fp, (np.ndarray, list)):
        raise TypeError("Input fp must be a numpy array or a list.")

    # Convert to numpy arrays
    if isinstance(x, list):
        x = np.array(x)
    if isinstance(xp, list):
        xp = np.array(xp)
    if isinstance(fp, list):
        fp = np.array(fp)

    # Squueze the arrays
    x = np.squeeze(x)
    xp = np.squeeze(xp)
    fp = np.squeeze(fp)

    # Check for data shape
    if xp.ndim != 1:
        raise ValueError("Input xp must be a 1-D sequence of n floats.")
    if x.ndim != 1:
        raise ValueError("Input x must be a 1-D sequence of k floats.")

    # Check that the number of samples in the old time vector and the signal match
    if xp.shape[0] != fp.shape[0]:
        raise ValueError(
            "The number of samples in the old time vector and the signal must match."
        )

    # Check for data integrity
    if x[0] < xp[0] or x[-1] > xp[-1]:
        # Truncate data
        idx = time_interval_indices(x, xp[0], xp[-1])
        x = x[idx]
        if x.size == 0:
            raise ValueError(
                "The new time vector is empty after truncation. Ensure the new time vector overlaps with the old time vector."
            )
        warn(
            "The new time vector is not within the range of the old time vector. Data has been truncated."
        )

    if not np.all(difference(xp) > 0):
        raise ValueError("Time series must be monotonically increasing.")

    # Resample the signal
    if fp.ndim == 1:
        return np.interp(x, xp, fp)
    else:
        f = np.empty((x.shape[0], fp.shape[1]))
        for i in range(fp.shape[1]):
            f[:, i] = np.interp(x, xp, fp[:, i])
        return f


def distance_traveled(
    mat: Union[np.ndarray, List[float]],
    dimensions: str = "2d",
    linear: bool = False,
    full: bool = False,
) -> Union[float, np.ndarray]:
    """
    Returns the distance traveled by a vector or matrix. If the input is a matrix,
    the distance traveled is calculated for column the first two or three columns,
    depending on the dimensions parameter.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        dimensions (str, default): Number of dimensions to compute the distance.
            Options are '2d' or '3d'. Default is '2d'. If the input is a matrix,
            with more than two columns, the distance will be computed by default
            with the first two columns if '2d' is selected, or with the first
            three columns if '3d' is selected.
        linear (bool): If True, the euclidean distance is computed for each
            measurement between the point and the origin; otherwise, computes
            the euclidean norm between points as a cumulative distance.
        full (bool): If True, the distance traveled computed for each point is
            returned; otherwise, the total distance traveled is returned.

    Returns:
        Union[float, np.ndarray]: The distance traveled given the matrix of points.

    Raises:
        ValueError: If the dimensions options is different than '2d' and '3d'.
        ValueError: If the dimensions is set to '2d' and the matrix has less than
            2 columns.
        ValueError: If the dimensions is set to '3d' and the matrix has less than
            3 columns.

    Examples:
        >>> mat = np.array([[0, 0], [1, 1], [2, 2]])
        >>> print(distance_traveled(mat, '2d', True, False))
    """
    # Check dimensions
    if dimensions not in ["2d", "3d"]:
        raise ValueError("Dimensions must be either 2d or 3d.")

    if dimensions == "2d":
        if mat.shape[1] < 2:
            raise ValueError("The input matrix must have at least two columns.")
        mat = mat[:, :2]
    else:
        if mat.shape[1] < 3:
            raise ValueError("The input matrix must have at least three columns.")
        mat = mat[:, :3]

    # Compute distance traveled
    # If linear, for each measurement compute the distance between the point and the origin. If full, return the
    # distance for each point; otherwise, just between the last point and the origin.
    if linear:
        if full:
            return norm(remove_offset(mat, mat[0]))
        else:
            return norm(remove_offset(mat, mat[0]))[-1]

    # Otherwise, for each measurement compute the distance between the current and the previous point and then compute
    # the cumulative distance. If full, return the cumulative sum for each measurement, otherwise, return the total
    # cumulative sum.
    else:
        if full:
            return np.r_[0.0, np.cumsum(norm(difference(mat)))]
        else:
            return np.sum(norm(difference(mat)))


def saturate(
    mat: Union[np.ndarray, List[float]], min_val: float, max_val: float
) -> np.ndarray:
    """
    Saturates a vector or matrix.

    Args:
        mat (Union[np.ndarray, List[float]]): Vector or matrix.
        min_val (float): Minimum value.
        max_val (float): Maximum value.

    Returns:
        np.ndarray: Saturated vector or matrix.

    Raises:
        TypeError: If the input is not a numpy array or a list.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> min_val = 0
        >>> max_val = 2
        >>> print(saturate(vec, min_val, max_val))
        [1 2 2]
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise TypeError("Input must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat
    return np.clip(mat, min_val, max_val)


def wrap360(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Wraps an input of angles between 0 and 360 degrees. If the input is a matrix,
    the wrap is applied to each column.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in degrees as a numpy array or a list.

    Returns:
        np.ndarray: The wrapped angles in degrees between 0 and 360 as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list.

    Examples:
        >>> angles = np.array([-30, 0, 90, 400])
        >>> wrapped_angles = wrap360(angles)
        >>> print(wrapped_angles)
        [330.   0.  90.  40.]

        >>> angles_matrix = np.array([[-30, 0, 90, 400], [720, -450, 180, 270]])
        >>> wrapped_angles_matrix = wrap360(angles_matrix)
        >>> print(wrapped_angles_matrix)
        [[330.   0.  90.  40.]
         [  0. 270. 180. 270.]]
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    return np.mod(angles, 360.0)


def wrap180(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Wraps an input of angles between -180 and 180 degrees.  If the input is a matrix,
    the wrap is applied to each column.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in degrees as a numpy array or a list.

    Returns:
        np.ndarray: The wrapped angles in degrees between -180 and 180 as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list.

    Examples:
        >>> angles = np.array([[-360, -270, -180, -90, 0, 90, 180, 270, 360])
        >>> wrapped_angles = wrap180(angles)
        >>> print(wrapped_angles)
        [  0. 90. -180. -90.   0.  90. -180. -90.   0.]

        >>> angles_matrix = np.array([[-360, -270, -180, -90, 0, 90, 180, 270, 360],
                                      [720, -450, 180, 270, -540, 630, -720, 810, -900]])
        >>> wrapped_angles_matrix = wrap180(angles_matrix)
        >>> print(wrapped_angles_matrix)
        [[   0.   90. -180.  -90.    0.   90. -180.  -90.    0.]
         [   0.  -90. -180.  -90.    0.  270.    0.  450.    0.]]
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    return np.mod(angles + 180.0, 360.0) - 180.0


def wrap2pi(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Wraps an input of angles between 0 and 2pi radians. If the input is a matrix,
    the wrap is applied to each column.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in radians as a numpy array or a list.

    Returns:
        np.ndarray: The wrapped angles in radians between 0 and 2pi as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list

    Examples:
        >>> angles = np.array([-np.pi/6, 0, np.pi/2, 5*np.pi])
        >>> wrapped_angles = wrap2pi(angles)
        >>> print(wrapped_angles)
        [5.7595865 0.         1.57079633 3.1415927]

        >>> angles_matrix = np.array([[-np.pi/6, 0, np.pi/2, 5*np.pi],
                                      [7*np.pi, -4*np.pi, 3*np.pi, 8*np.pi]])
        >>> wrapped_angles_matrix = wrap2pi(angles_matrix)
        >>> print(wrapped_angles_matrix)
        [[5.75958653 0.         1.57079633 3.14159265]
         [3.14159265 0.         3.14159265 0.        ]]
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    return np.mod(angles, 2 * np.pi)


def wrap1pi(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Wraps an input of angles between -pi and pi radians. If the input is a matrix,
    the wrap is applied to each element.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in radians as a numpy array or a list.

    Returns:
        np.ndarray: The wrapped angles in radians between -pi and pi as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list.

    Examples:
        >>> angles = np.array([-2*np.pi, -3*np.pi/2, -np.pi, 0, np.pi, 3*np.pi/2, 2*np.pi])
        >>> wrapped_angles = wrap1pi(angles)
        >>> print(wrapped_angles)
        [  0.          1.57079633 3.14159265  0.         -3.14159265 -1.57079633  0.          ]

        >>> angles_matrix = np.array([[-2*np.pi, -3*np.pi/2, -np.pi, 0, np.pi, 3*np.pi/2, 2*np.pi],
                                      [4*np.pi, -5*np.pi/2, 6*np.pi, -7*np.pi/2, 8*np.pi, -9*np.pi/2, 10*np.pi]])
        >>> wrapped_angles_matrix = wrap1pi(angles_matrix)
        >>> print(wrapped_angles_matrix)
        [[ 0.          1.57079633 -3.14159265  0.         -3.14159265 -1.57079633  0.        ]
         [ 0.         -1.57079633  0.          1.57079633  0.         -1.57079633  0.        ]]
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    return np.mod(angles + np.pi, 2 * np.pi) - np.pi


def unwrap2pi(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Unwraps an input of angles wrapped between 0 and 2pi radians. If the input is a matrix,
    the wrap is applied to each element.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in radians as a numpy array or a list.

    Returns:
        np.ndarray: The unwrapped angles in radians as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list.

    Examples:
        >>> angles = np.array([np.pi/2, np.pi, 3*np.pi/2, 2*np.pi, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
        >>> unwrapped_angles = unwrap2pi(angles)
        >>> print(unwrapped_angles)
        [1.57079633 3.14159265 4.71238898 6.28318531 7.85398163 9.42477796 10.99557429 12.56637061]

        >>> angles = np.array([[np.pi/2, np.pi, 3*np.pi/2, 2*np.pi, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                               [np.pi/2, np.pi, 3*np.pi/2, 2*np.pi, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]])
        >>> unwrapped_angles = unwrap2pi(angles.T)
        >>> print(unwrapped_angles.T)
        [[1.57079633 3.14159265 4.71238898 6.28318531 7.85398163 9.42477796 10.99557429 12.56637061],
         [1.57079633 3.14159265 4.71238898 6.28318531 7.85398163 9.42477796 10.99557429 12.56637061]]

    Notes:
        The unwrapping is done using the numpy unwrap function.
        By default, if the discontinuity between angles is greater than pi radians, no unwrapping is done.
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    # Unwrap each column in the array
    unwrapped = np.unwrap(angles, axis=0) if angles.ndim > 1 else np.unwrap(angles)

    return unwrapped


def unwrap1pi(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Unwraps an input of angles wrapped between -pi and pi radians. If the input is a matrix,
    the wrap is applied to each element.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in radians as a numpy array or a list.

    Returns:
        np.ndarray: The unwrapped angles in radians as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list.

    Examples:
        >>> angles = np.array([-3*np.pi/2, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
        >>> unwrapped_angles = unwrap1pi(angles)
        >>> print(unwrapped_angles)
        [-4.71238898 -3.14159265 -1.57079633  0.          1.57079633  3.14159265  4.71238898  6.28318531]

        >>> angles = np.array([[-3*np.pi/2, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                               [-3*np.pi/2, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]])
        >>> unwrapped_angles = unwrap1pi(angles.T)
        >>> print(unwrapped_angles.T)
        [[-4.71238898 -3.14159265 -1.57079633  0.          1.57079633  3.14159265  4.71238898  6.28318531],
         [-4.71238898 -3.14159265 -1.57079633  0.          1.57079633  3.14159265  4.71238898  6.28318531]]

    Notes:
        The unwrapping is done using the numpy unwrap function.
        By default, if the discontinuity between angles is greater than pi/2 radians, no unwrapping is done.
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    # Unwrap each column in the array
    unwrapped = (
        np.unwrap(angles, axis=0, period=np.pi)
        if angles.ndim > 1
        else np.unwrap(angles, period=np.pi)
    )

    return unwrapped


def unwrap360(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Unwraps an input of angles wrapped between 0 and 360 degrees. If the input is a matrix,
    the wrap is applied to each element.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in degrees as a numpy array or a list.

    Returns:
        np.ndarray: The unwrapped angles in degrees as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list.

    Examples:
        >>> angles = np.array([30, 90, 180, 270, 360, 30, 90, 180, 270, 360])
        >>> unwrapped_angles = unwrap360(angles)
        >>> print(unwrapped_angles)
        [ 30.  90. 180. 270. 360. 390. 450. 540. 630. 720.]

        >>> angles = np.array([[30, 90, 180, 270, 360, 30, 90, 180, 270, 360],
                               [30, 90, 180, 270, 360, 30, 90, 180, 270, 360]])
        >>> unwrapped_angles = unwrap360(angles.T)
        >>> print(unwrapped_angles.T)
        [[ 30.  90. 180. 270. 360. 390. 450. 540. 630. 720.],
         [ 30.  90. 180. 270. 360. 390. 450. 540. 630. 720.]]

    Notes:
        The unwrapping is done using the numpy unwrap function.
        By default, if the discontinuity between angles is greater than 180 degrees, no unwrapping is done.
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    # Unwrap each column in the array
    unwrapped = (
        np.unwrap(angles, axis=0, period=360.0)
        if angles.ndim > 1
        else np.unwrap(angles, period=360.0)
    )

    return unwrapped


def unwrap180(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Unwraps an input of angles wrapped between -180 and 180 degrees. If the input is a matrix,
    the wrap is applied to each element.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in degrees as a numpy array or a list.

    Returns:
        np.ndarray: The unwrapped angles in degrees as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list.

    Examples:
        >>> angles = np.array([45, 90, 135, 180, 45, 90, 135, 180])
        >>> unwrapped_angles = unwrap180(angles)
        >>> print(unwrapped_angles)
        [ 45.  90. 135. 180. 225. 270. 315. 360.]

        >>> angles = np.array([[45, 90, 135, 180, 45, 90, 135, 180],
                               [45, 90, 135, 180, 45, 90, 135, 180]])
        >>> unwrapped_angles = unwrap180(angles.T)
        >>> print(unwrapped_angles.T)
        [[ 45.  90. 135. 180. 225. 270. 315. 360.],
         [ 45.  90. 135. 180. 225. 270. 315. 360.]]

    Notes:
        The unwrapping is done using the numpy unwrap function.
        By default, if the discontinuity between angles is greater than 90 degrees, no unwrapping is done.
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    # Unwrap each column in the array
    unwrapped = (
        np.unwrap(angles, axis=0, period=180.0)
        if angles.ndim > 1
        else np.unwrap(angles, period=180.0)
    )

    return unwrapped


def wrapunwrap(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Wraps an input of angle between -pi and pi radians and then unwraps it. If the input is a matrix,
    the wrap is applied to each element.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in radians as a numpy array or a list.

    Returns:
        np.ndarray: The wrapped and unwrapped angles in radians as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list.

    Examples:
        >>> angles = np.array([-3*np.pi/2, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
        >>> wrapped_unwrapped_angles = wrapunwrap(angles)
        >>> print(wrapped_unwrapped_angles)
        [-4.71238898 -3.14159265 -1.57079633  0.          1.57079633  3.14159265  4.71238898  6.28318531]

        >>> angles = np.array([[-3*np.pi/2, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                               [-3*np.pi/2, -np.pi, -np.pi/2, 0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi]])
        >>> wrapped_unwrapped_angles = wrapunwrap(angles.T)
        >>> print(wrapped_unwrapped_angles.T)
        [[-4.71238898 -3.14159265 -1.57079633  0.          1.57079633  3.14159265  4.71238898  6.28318531],
         [-4.71238898 -3.14159265 -1.57079633  0.          1.57079633  3.14159265  4.71238898  6.28318531]]
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    return unwrap1pi(wrap1pi(angles))


def wrapunwrap360(angles: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Wraps an input of angle between 0 and 360 degrees and then unwraps it. If the input is a matrix,
    the wrap is applied to each element.

    Args:
        angles (Union[Iterable[float], np.ndarray]): The angles in degrees as a numpy array or a list.

    Returns:
        np.ndarray: The wrapped and unwrapped angles in degrees as a numpy array.

    Raises:
        ValueError: If the input angles are not a numpy array or a list.

    Examples:
        >>> angles = np.array([30, 90, 180, 270, 360, 390, 450, 540, 630, 720])
        >>> wrapped_unwrapped_angles = wrapunwrap360(angles)
        >>> print(wrapped_unwrapped_angles)
        [ 30.  90. 180. 270. 360. 390. 450. 540. 630. 720.]

        >>> angles = np.array([[30, 90, 180, 270, 360, 390, 450, 540, 630, 720],
                               [30, 90, 180, 270, 360, 390, 450, 540, 630, 720]])
        >>> wrapped_unwrapped_angles = wrapunwrap360(angles.T)
        >>> print(wrapped_unwrapped_angles.T)
        [[ 30.  90. 180. 270. 360. 390. 450. 540. 630. 720.],
         [ 30.  90. 180. 270. 360. 390. 450. 540. 630. 720.]]
    """
    if not isinstance(angles, np.ndarray) and not isinstance(angles, list):
        raise ValueError("Type Error: The angles must be a numpy array or a list.")

    angles = np.array(angles) if isinstance(angles, list) else angles

    return unwrap360(wrap360(angles))
