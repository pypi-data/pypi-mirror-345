"""
This module contains functions to calibrate AHRS.

Functions:
    cal_ahrs_so3: Calibration of the attitude extrinsics between two AHRS systems using the
        Special Orthogonal Group (SO(3)) optimization. The calibration is performed
        by minimizing the sum of squared residuals of the error of projecting the
        attitude of AHRS 2 to the attitude of AHRS 1.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

from typing import List, Union

import autograd.numpy as np_ag
import numpy as np

from navlib.math import (
    difference,
    filter_lowpass,
    median,
    resample,
    rph2rot,
    so3_optimization,
)


def cal_ahrs_so3(
    time_ahrs_1: Union[np.ndarray, List[float]],
    time_ahrs_2: Union[np.ndarray, List[float]],
    rph_ahrs_1: Union[np.ndarray, List[float]],
    rph_ahrs_2: Union[np.ndarray, List[float]],
    low_pass_filter: bool = True,
) -> np.ndarray:
    """
    Calibration of the attitude extrinsics between two AHRS systems using the
    Special Orthogonal Group (SO(3)) optimization. The calibration is performed
    by minimizing the sum of squared residuals of the error of projecting the
    attitude of AHRS 2 to the attitude of AHRS 1.

    Args:
        time_ahrs_1 (Union[np.ndarray, List[float]]): Time data of AHRS 1.
        time_ahrs_2 (Union[np.ndarray, List[float]]): Time data of AHRS 2.
        rph_ahrs_1 (Union[np.ndarray, List[float]]): Roll-Pitch-Heading data of AHRS 1.
        rph_ahrs_2 (Union[np.ndarray, List[float]]): Roll-Pitch-Heading data of AHRS 2.
        low_pass_filter (bool, optional): Apply low-pass filter to the input signals. Defaults to True.

    Returns:
        rot_1_2 (np.ndarray): Rotation matrix of AHRS 2 with respect to AHRS 1.

    Raises:
        TypeError: If the inputs are not of the correct type.
        ValueError: If the inputs are not of the correct dimensions.
        ValueError: If the data from AHRS 1 and AHRS 2 do not have the same number of measurements.
        ValueError: If the time_ahrs_1 is not in the time range of AHRS 2.
    """
    # Convert to numpy arrays
    if isinstance(time_ahrs_1, list):
        time_ahrs_1 = np.array(time_ahrs_1)
    if isinstance(time_ahrs_2, list):
        time_ahrs_2 = np.array(time_ahrs_2)
    if isinstance(rph_ahrs_1, list):
        rph_ahrs_1 = np.array(rph_ahrs_1)
    if isinstance(rph_ahrs_2, list):
        rph_ahrs_2 = np.array(rph_ahrs_2)

    # Check inputs
    if not isinstance(time_ahrs_1, np.ndarray):
        raise TypeError("time_ahrs_1 must be a numpy array or list")
    if not isinstance(time_ahrs_2, np.ndarray):
        raise TypeError("time_ahrs_2 must be a numpy array or list")
    if not isinstance(rph_ahrs_1, np.ndarray):
        raise TypeError("rph_ahrs_1 must be a numpy array or list")
    if not isinstance(rph_ahrs_2, np.ndarray):
        raise TypeError("rph_ahrs_2 must be a numpy array or list")
    if not isinstance(low_pass_filter, bool):
        raise TypeError("low_pass_filter must be a boolean")

    # Check dimensions
    time_ahrs_1 = time_ahrs_1.squeeze()
    if time_ahrs_1.ndim >= 2:
        raise ValueError(
            "The time_ahrs_1 must be a (n, ), (n, 1) or (1, n) numpy array."
        )
    time_ahrs_2 = time_ahrs_2.squeeze()
    if time_ahrs_2.ndim >= 2:
        raise ValueError(
            "The time_ahrs_2 must be a (n, ), (n, 1) or (1, n) numpy array."
        )
    if rph_ahrs_1.ndim != 2 or (rph_ahrs_1.shape[0] != 3 and rph_ahrs_1.shape[1] != 3):
        raise ValueError("rph_ahrs_1 must be a 3xN or Nx3 numpy array.")
    if rph_ahrs_2.ndim != 2 or (rph_ahrs_2.shape[0] != 3 and rph_ahrs_2.shape[1] != 3):
        raise ValueError("rph_ahrs_2 must be a 3xN or Nx3 numpy array.")

    # Force the roll, pitch, and heading to be Nx3
    if rph_ahrs_1.shape[0] == 3 and rph_ahrs_1.shape[1] != 3:
        rph_ahrs_1 = rph_ahrs_1.T
    if rph_ahrs_2.shape[0] == 3 and rph_ahrs_2.shape[1] != 3:
        rph_ahrs_2 = rph_ahrs_2.T

    # Check if the time arrays are the same length
    if time_ahrs_1.shape[0] != rph_ahrs_1.shape[0]:
        raise ValueError(
            "The time_ahrs_1 and rph_ahrs_1 must have the same number of measurements."
        )
    if time_ahrs_2.shape[0] != rph_ahrs_2.shape[0]:
        raise ValueError(
            "The time_ahrs_2 and rph_ahrs_2 must have the same number of measurements."
        )

    # Clip the measurements from AHRS 1 to the time range of AHRS 2
    time_ahrs_2_max = np.max(time_ahrs_2)
    time_ahrs_2_min = np.min(time_ahrs_2)
    filter_idx = (time_ahrs_1 >= time_ahrs_2_min) & (time_ahrs_1 <= time_ahrs_2_max)
    time_ahrs_1 = time_ahrs_1[filter_idx]
    rph_ahrs_1 = rph_ahrs_1[filter_idx]
    if time_ahrs_1.shape[0] == 0:
        raise ValueError(
            "The time_ahrs_1 must have at least one measurement in the time range of AHRS 2."
        )

    # Resample the data from AHRS 2 to the time of AHRS 1
    rph_ahrs_2 = resample(time_ahrs_1, time_ahrs_2, rph_ahrs_2)
    time_ahrs_2 = time_ahrs_1

    # Filter input signals with a low-pass filter set to a cutoff frequency of 1/10
    # of the sampling frequency
    if low_pass_filter:
        # Sampling frequency
        frequency = 1 / median(difference(time_ahrs_1))

        # Apply low-pass filter
        rph_ahrs_1 = filter_lowpass(rph_ahrs_1, frequency / 10)
        rph_ahrs_2 = filter_lowpass(rph_ahrs_2, frequency / 10)

    # Initialize variables for the optimization problem: LHS - RHS @ x = 0
    N = rph_ahrs_1.shape[0]
    RHS = np.zeros([N, 3, 3])
    LHS = np.zeros([N, 3, 3])

    # Populate the LHS and RHS matrices
    for ix in range(N):
        # Right hand side
        RHS[ix] = rph2rot(rph_ahrs_1[ix, :])

        # Left hand side
        LHS[ix] = rph2rot(rph_ahrs_2[ix, :])

    # SO(3) optimization
    rot_2_1 = so3_optimization(
        _objective_function_cal_ahrs_so3,
        LHS,
        RHS,
    )

    # Rotation of AHRS 2 with respect to AHRS 1
    rot_1_2 = rot_2_1.T

    return rot_1_2


def _objective_function_cal_ahrs_so3(
    x: np.ndarray, LHS: np.ndarray, RHS: np.ndarray
) -> np.ndarray:
    """
    Objective function to solve the calibration of two AHRS systems using the
    Special Orthogonal Group (SO(3)) optimization. The calibration is performed
    by minimizing the sum of squared residuals of the error of projecting the
    attitude of AHRS 2 to the attitude of AHRS 1.

    Args:
        x (np.ndarray): Optimization variables.
        LHS (np.ndarray): Left hand side corresponding to the AHRS 1 attitude.
        RHS (np.ndarray): Right hand side corresponding to the AHRS 2 attitude.

    Returns:
        np.ndarray: Sum of squared residuals.
    """
    cost = np_ag.sum(np_ag.linalg.norm(LHS - RHS @ np_ag.vstack(x), axis=1) ** 2)
    return cost
