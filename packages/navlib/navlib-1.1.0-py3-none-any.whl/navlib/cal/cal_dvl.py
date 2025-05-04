"""
This module contains functions to calibrate DVL systems.

Functions:
    cal_dvl_acc_so3: Doppler alignment code using AHRS, DVL and depth sensor data to estimate
        the attitude of the DVL with respect to the vehicle frame, given a previously
        known IMU extrinsic calibration and the lever arm between the DVL and the
        vehicle frame. The code is based on the work of [1].
    cal_dvl_correct_by_sound_velocity: Correct the DVL velocity by the sound velocity from CTD data.
    cal_dvl_jck_so3: Doppler alignment code using AHRS and DVL data to estimate the attitude of
        the DVL with respect to the vehicle frame given the position of an external
        aiding systems, such as LBL, given a previously known IMU extrinsic calibration
        and the lever arm between the DVL and the vehicle frame. The code is based on
        the work of [2].


Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org

References:
    [1] Troni, G. and Whitcomb, L.L. (2015), Advances in In Situ Alignment
        Calibration of Doppler and High/Low-end Attitude Sensors for Underwater
        Vehicle Navigation: Theory and Experimental Evaluation. J. Field
        Robotics, 32: 655-674.

    [2] Kinsey, J. C., & Whitcomb, L. L. (2002, May). Towards in-situ calibration
        of gyro and doppler navigation sensors for precision underwater vehicle
        navigation. In Proceedings 2002 IEEE International Conference on Robotics
        and Automation (Cat. No. 02CH37292) (Vol. 4, pp. 4016-4023). IEEE.
"""

from typing import List, Tuple, Union

import autograd.numpy as np_ag
import numpy as np
from scipy.integrate import cumulative_trapezoid

from navlib.environment import ctd2svel
from navlib.math import (
    derivative,
    difference,
    filter_lowpass,
    max,
    median,
    min,
    pose_diff,
    project_to_so3,
    remove_mean,
    remove_median,
    remove_offset,
    resample,
    rph2rot,
    so3_optimization,
    transpose,
    vec_to_so3,
    xyzrph2matrix,
)


def cal_dvl_acc_so3(
    time_dvl: Union[np.ndarray, List[float]],
    time_ahrs: Union[np.ndarray, List[float]],
    time_depth: Union[np.ndarray, List[float]],
    velocity_dvl: Union[np.ndarray, List[float]],
    acceleration_ahrs: Union[np.ndarray, List[float]],
    rph_ahrs: Union[np.ndarray, List[float]],
    angular_rate_ahrs: Union[np.ndarray, List[float]],
    depth: Union[np.ndarray, List[float]],
    low_pass_filter: bool = True,
    remove_gravity: bool = True,
    lever_arm: np.ndarray = [0, 0, 0],
    method: str = "ls",
    force_so3: bool = True,
) -> np.ndarray:
    """
    Doppler alignment code using AHRS, DVL and depth sensor data to estimate
    the attitude of the DVL with respect to the vehicle frame, given a previously
    known IMU extrinsic calibration and the lever arm between the DVL and the
    vehicle frame. The code is based on the work of [1].

    The solution can be estimated using least squares either with a regular
    least squares, or with SVD or with a nonlinear optimization using Pymanopt,
    which is the default as it computes the optimization considering the SO(3)
    constraints.

    [1] Troni, G. and Whitcomb, L.L. (2015), Advances in In Situ Alignment
    Calibration of Doppler and High/Low-end Attitude Sensors for Underwater
    Vehicle Navigation: Theory and Experimental Evaluation. J. Field Robotics,
    32: 655-674. https://doi.org/10.1002/rob.21551

    Args:
        time_dvl (np.ndarray): Time vector for DVL data.
        time_ahrs (np.ndarray): Time vector for AHRS data.
        time_depth (np.ndarray): Time vector for depth data.
        velocity_dvl (np.ndarray): DVL velocity data in the instrument frame.
        acceleration_ahrs (np.ndarray): AHRS acceleration data in the instrument frame.
        rph_ahrs (np.ndarray): AHRS roll, pitch, and heading data.
        angular_rate_ahrs (np.ndarray): AHRS angular rate data in the instrument frame.
        depth (np.ndarray): Depth data from the depth sensor.
        low_pass_filter (bool): Apply a low-pass filter to the input signals. The
            cutoff frequency is set to 1/10 of the sampling frequency.
        remove_gravity (bool): Remove gravity from the acceleration data.
        lever_arm (np.ndarray): Lever arm from the DVL with respect to the vehicle
            frame. Default is [0, 0, 0].
        method (str): Optimization method to use. Options are 'ls' for least
            squares and 'min' for SO(3) minimization and 'svd' for singular value
            decomposition.
        force_so3 (bool): Force the solution to be in SO(3).

    Returns:
        np.ndarray: Rotation matrix in SO(3).

    Raises:
        TypeError: If input types are not correct.
        ValueError: If input dimensions are not correct.
    """
    # Convert to numpy arrays
    if isinstance(time_dvl, list):
        time_dvl = np.array(time_dvl)
    if isinstance(time_ahrs, list):
        time_ahrs = np.array(time_ahrs)
    if isinstance(time_depth, list):
        time_depth = np.array(time_depth)
    if isinstance(velocity_dvl, list):
        velocity_dvl = np.array(velocity_dvl)
    if isinstance(acceleration_ahrs, list):
        acceleration_ahrs = np.array(acceleration_ahrs)
    if isinstance(rph_ahrs, list):
        rph_ahrs = np.array(rph_ahrs)
    if isinstance(angular_rate_ahrs, list):
        angular_rate_ahrs = np.array(angular_rate_ahrs)
    if isinstance(depth, list):
        depth = np.array(depth)
    if isinstance(lever_arm, list):
        lever_arm = np.array(lever_arm)

    # Check inputs
    if not isinstance(time_ahrs, np.ndarray):
        raise TypeError("time_ahrs must be a numpy array or list")
    if not isinstance(time_dvl, np.ndarray):
        raise TypeError("time_dvl must be a numpy array or list")
    if not isinstance(time_depth, np.ndarray):
        raise TypeError("time_depth must be a numpy array or list")
    if not isinstance(velocity_dvl, np.ndarray):
        raise TypeError("velocity_dvl must be a numpy array or list")
    if not isinstance(acceleration_ahrs, np.ndarray):
        raise TypeError("acceleration_ahrs must be a numpy array or list")
    if not isinstance(rph_ahrs, np.ndarray):
        raise TypeError("rph_ahrs must be a numpy array or list")
    if not isinstance(angular_rate_ahrs, np.ndarray):
        raise TypeError("angular_rate_ahrs must be a numpy array or list")
    if not isinstance(depth, np.ndarray):
        raise TypeError("depth must be a numpy array or list")
    if not isinstance(low_pass_filter, bool):
        raise TypeError("low_pass_filter must be a boolean")
    if not isinstance(remove_gravity, bool):
        raise TypeError("remove_gravity must be a boolean")
    if not isinstance(lever_arm, np.ndarray):
        raise TypeError("lever_arm must be a numpy array or list")
    if not isinstance(force_so3, bool):
        raise TypeError("force_so3 must be a boolean")
    if not isinstance(method, str):
        raise TypeError("method must be a string")

    # Check dimensions
    time_ahrs = time_ahrs.squeeze()
    if time_ahrs.ndim >= 2:
        raise ValueError("The time_ahrs must be a (n, ), (n, 1) or (1, n) numpy array.")
    time_dvl = time_dvl.squeeze()
    if time_dvl.ndim >= 2:
        raise ValueError("The time_dvl must be a (n, ), (n, 1) or (1, n) numpy array.")
    time_depth = time_depth.squeeze()
    if time_depth.ndim >= 2:
        raise ValueError(
            "The time_depth must be a (n, ), (n, 1) or (1, n) numpy array."
        )
    if velocity_dvl.ndim != 2 or (
        velocity_dvl.shape[0] != 3 and velocity_dvl.shape[1] != 3
    ):
        raise ValueError("velocity_dvl must be a 3xN or Nx3 numpy array.")
    if acceleration_ahrs.ndim != 2 or (
        acceleration_ahrs.shape[0] != 3 and acceleration_ahrs.shape[1] != 3
    ):
        raise ValueError("acceleration_ahrs must be a 3xN or Nx3 numpy array.")
    if rph_ahrs.ndim != 2 or (rph_ahrs.shape[0] != 3 and rph_ahrs.shape[1] != 3):
        raise ValueError("rph_ahrs must be a 3xN or Nx3 numpy array.")
    if angular_rate_ahrs.ndim != 2 or (
        angular_rate_ahrs.shape[0] != 3 and angular_rate_ahrs.shape[1] != 3
    ):
        raise ValueError("angular_rate_ahrs must be a 3xN or Nx3 numpy array.")
    depth = depth.squeeze()
    if depth.ndim >= 2:
        raise ValueError("The depth must be a (n, ), (n, 1) or (1, n) numpy array.")
    lever_arm = lever_arm.squeeze()
    if lever_arm.ndim >= 2 or lever_arm.shape[0] != 3:
        raise ValueError("The lever_arm must be a (3, ), (1, 3) or (3, 1) numpy array.")

    # Check the optional parameters
    if method.lower() not in ["ls", "min", "svd"]:
        raise ValueError("method must be 'ls', 'min', or 'svd'")

    # Force Nx3 shape for arrays
    if velocity_dvl.shape[0] == 3 and velocity_dvl.shape[1] != 3:
        velocity_dvl = velocity_dvl.T
    if acceleration_ahrs.shape[0] == 3 and acceleration_ahrs.shape[1] != 3:
        acceleration_ahrs = acceleration_ahrs.T
    if rph_ahrs.shape[0] == 3 and rph_ahrs.shape[1] != 3:
        rph_ahrs = rph_ahrs.T
    if angular_rate_ahrs.shape[0] == 3 and angular_rate_ahrs.shape[1] != 3:
        angular_rate_ahrs = angular_rate_ahrs.T

    # Check if the time arrays are the same length
    if time_ahrs.shape[0] != rph_ahrs.shape[0]:
        raise ValueError(
            "The time_ahrs and rph_ahrs must have the same number of measurements."
        )
    if time_ahrs.shape[0] != angular_rate_ahrs.shape[0]:
        raise ValueError(
            "The time_ahrs and angular_rate_ahrs must have the same number of measurements."
        )
    if time_ahrs.shape[0] != acceleration_ahrs.shape[0]:
        raise ValueError(
            "The time_ahrs and acceleration_ahrs must have the same number of measurements."
        )
    if time_dvl.shape[0] != velocity_dvl.shape[0]:
        raise ValueError(
            "The time_dvl and velocity_dvl must have the same number of measurements."
        )
    if time_depth.shape[0] != depth.shape[0]:
        raise ValueError(
            "The time_depth and depth must have the same number of measurements."
        )

    # Filter input signals with a low-pass filter set to a cutoff frequency of 1/10
    # of the sampling frequency
    if low_pass_filter:
        # Sampling frequency
        frequency_dvl = 1 / median(difference(time_dvl))
        frequency_ahrs = 1 / median(difference(time_ahrs))
        frequency_depth = 1 / median(difference(time_depth))

        # Apply low-pass filter
        velocity_dvl = filter_lowpass(velocity_dvl, frequency_dvl, 0.1 * frequency_dvl)
        acceleration_ahrs = filter_lowpass(
            acceleration_ahrs, frequency_ahrs, 0.1 * frequency_ahrs
        )
        angular_rate_ahrs = filter_lowpass(
            angular_rate_ahrs, frequency_ahrs, 0.1 * frequency_ahrs
        )
        rph_ahrs = filter_lowpass(rph_ahrs, frequency_ahrs, 0.1 * frequency_ahrs)
        depth = filter_lowpass(depth, frequency_depth, 0.1 * frequency_depth)

    # Clip the measurements from DVL to the AHRS and depth time range
    time_range_max = min([max(time_ahrs), max(time_depth)])
    time_range_min = max([min(time_ahrs), min(time_depth)])
    filter_idx = (time_dvl >= time_range_min) & (time_dvl <= time_range_max)
    time_dvl = time_dvl[filter_idx]
    velocity_dvl = velocity_dvl[filter_idx]
    if time_dvl.shape[0] == 0:
        raise ValueError(
            "The time_dvl must have at least one measurement in the time range of the AHRS and depth data."
        )

    # Resample the AHRS and depth data to the DVL time. Usually the AHRS data is
    # at a higher frequency than the DVL data.
    acceleration_dvl = resample(time_dvl, time_ahrs, acceleration_ahrs)
    rph_dvl = resample(time_dvl, time_ahrs, rph_ahrs)
    angular_rate_dvl = resample(time_dvl, time_ahrs, angular_rate_ahrs)
    depth_dvl = resample(time_dvl, time_depth, depth)

    # Remove gravity from the acceleration data. As the vehicle is moving slowly
    # the acceleration due to gravity can be removed using as offset the median
    # value of the acceleration data.
    if remove_gravity:
        acceleration_dvl = remove_median(acceleration_dvl)

    # Uses as reference the IMU, i.e., the IMU is aligned with the vehicle frame
    model = _model(dvl_position_xyz=lever_arm)

    # Initialize variables
    N = len(time_dvl)
    RHS = np.zeros([N, 3, 9])
    LHS = np.zeros([N, 3, 1])

    # First calculations
    # Rotation matrix from the AHRS to the vehicle frame
    rot_v_ahrs = model.ahrs.transformation_matrix()[:3, :3]
    # Lever arm from the attitude sensor to the DVL
    lever_arm = pose_diff(
        model.ahrs.transformation_matrix(), model.dvl.transformation_matrix()
    )[:3, [3]]
    # Compute the linear velocities and angular rates derivatives
    alfa_b = np.r_[np.zeros((1, 3)), derivative(angular_rate_dvl, time_dvl)]
    velocity_dvl_dot = np.r_[np.zeros((1, 3)), derivative(velocity_dvl, time_dvl)]

    # Equations related to accelerometer-based calibration, based on [1, Eq.13]
    for ix in range(N):
        # Right hand side
        term_1 = np.kron(velocity_dvl[ix, :], vec_to_so3(angular_rate_dvl[ix, :]))
        term_2 = np.kron(velocity_dvl_dot[ix, :], np.eye(3, dtype=np.float64))
        RHS[ix] = term_1 + term_2

        # Left hand side
        term_1 = rot_v_ahrs @ np.vstack(acceleration_dvl[ix, :])
        term_2 = (
            vec_to_so3(angular_rate_dvl[ix, :]) ** 2 + vec_to_so3(alfa_b[ix, :])
        ) @ lever_arm
        LHS[ix] = term_1 + term_2

    # Reshape the LHS and RHS matrices into 2D matrices
    LHS = LHS.reshape(-1, 1)
    RHS = RHS.reshape(-1, 9)

    # Equations related to the addition of the depth measurements to the accelerations-based
    # calibration, based on [1, Eq.17]
    RHSD = np.zeros([N, 1, 9])
    LHSD = np.zeros([N, 1, 1])
    e3 = np.vstack(np.array([0, 0, 1]))

    dt = median(difference(time_dvl))
    # NOTE: Low pass filter applied to the depth measurements set to a cutoff frequency of 1/10
    # of the sampling frequency
    depth_dvl_diff = np.r_[np.zeros(1), difference(depth_dvl)]

    for ix in range(N):
        # Right hand side
        rot_w_v = rph2rot(rph_dvl[ix, :])
        RHSD[ix] = np.kron(velocity_dvl[ix, :], (e3.T @ rot_w_v))

        # Left hand side
        LHSD[ix] = depth_dvl_diff[ix] / dt

    # Reshape the LHSD and RHSD matrices into 2D matrices
    LHSD = LHSD.reshape(-1, 1)
    RHSD = RHSD.reshape(-1, 9)

    # Compute gain beta, based on [1, Eq.20]
    beta_gain_numerator = np.sum(
        np.square(
            np.linalg.norm(rot_v_ahrs @ acceleration_dvl.reshape(-1, 3, 1), axis=1)
        )
    )
    beta_gain_denominator = np.sum(np.square(depth_dvl_diff))
    beta_gain = np.sqrt(beta_gain_numerator / beta_gain_denominator)

    # Row concatenate the LHS and RHS matrices
    LHS_tilde = np.r_[LHS.reshape(-1, 1), np.sqrt(beta_gain) * LHSD.reshape(-1, 1)]
    RHS_tilde = np.r_[RHS.reshape(-1, 9), np.sqrt(beta_gain) * RHSD.reshape(-1, 9)]

    # Solve the optimization problem (LHS_tilde = RHS_tilde @ X)
    # Least squares
    if method.lower() == "ls":
        x = np.linalg.lstsq(RHS_tilde, LHS_tilde, rcond=None)[0]

    # Singular value decomposition
    elif method.lower() == "svd":
        U, S, Vt = np.linalg.svd(RHS_tilde, full_matrices=False)
        x = Vt.T @ np.diag(1 / S) @ U.T @ LHS_tilde

    # Pymanopt
    elif method.lower() == "min":
        x = so3_optimization(
            _objective_function_cal_dvl_acc_so3, LHS, RHS, LHSD, RHSD, beta_gain
        )

    # Reshape the column-wise stacked solution into a 3x3 matrix
    rot_v_dvl = x.reshape(3, 3, order="F") if method != "min" else x

    # Force the solution to be in SO(3)
    if force_so3 and method != "min":
        rot_v_dvl = project_to_so3(rot_v_dvl)

    return rot_v_dvl


def _objective_function_cal_dvl_acc_so3(
    x: np.ndarray,
    LHS: np.ndarray,
    RHS: np.ndarray,
    LHSD: np.ndarray,
    RHSD: np.ndarray,
    beta: float,
) -> np.ndarray:
    """
    Objective function to minimize the sum of squared residuals.

    Args:
        X (np.ndarray): Optimization variables.
        LHS (np.ndarray): Left hand side of the acceleration-based calibration.
        RHS (np.ndarray): Right hand side of the acceleration-based calibration.
        LHSD (np.ndarray): Left hand side of the depth-based calibration.
        RHSD (np.ndarray): Right hand side of the depth-based calibration.
        beta (float): Gain to combine both equations.

    Returns:
        np.ndarray: Sum of squared residuals.
    """
    x = x.reshape(9, 1, order="F")
    residual_acceleration = np_ag.sum(
        np_ag.linalg.norm(LHS - RHS @ np_ag.vstack(x), axis=1) ** 2
    )
    residual_depth = np_ag.sum(
        np_ag.linalg.norm(LHSD - RHSD @ np_ag.vstack(x), axis=1) ** 2
    )
    cost = residual_acceleration + beta * residual_depth
    return cost


def cal_dvl_correct_by_sound_velocity(
    velocity_dvl: Union[np.ndarray, List[float]],
    conductivity: Union[np.ndarray, List[float]],
    temperature: Union[np.ndarray, List[float]],
    depth: Union[np.ndarray, List[float]],
    latitude: Union[float, np.ndarray, List[float]] = None,
    longitude: Union[float, np.ndarray, List[float]] = None,
    sound_velocity_ref: Union[int, float] = 1500,
) -> Tuple[np.ndarray, float]:
    """
    Correct the DVL velocity by the sound velocity from CTD data.
    The DVL velocity is corrected by the ratio of the sound velocity from CTD
    data to the reference sound velocity. The reference sound velocity is
    usually 1500 m/s.

    Args:
        velocity_dvl (np.ndarray): DVL velocity data in the instrument frame in m/s.
        conductivity (np.ndarray): Conductivity data from the CTD in S/m. It must be interpolated
            to the DVL time.
        temperature (np.ndarray): Temperature data from the CTD in degrees Celsius. It must be
            interpolated to the DVL time.
        depth (np.ndarray): Depth data from the CTD in meters. Upwards is positive.
            It must be interpolated to the DVL time.
        latitude (Union[float, np.ndarray, List[float]], optional): Latitude in degrees. It must
            be interpolated to the DVL time. Defaults to None.
        longitude (Union[float, np.ndarray, List[float]], optional): Longitude in degrees. It must
            be interpolated to the DVL time. Defaults to None.
        sound_velocity_ref (Union[int, float], optional): Reference sound velocity in m/s. Defaults to 1500.

    Returns:
        Tuple[np.ndarray, float]:
            - np.ndarray: Corrected DVL velocity in the instrument frame in m/s.
            - float: Median sound velocity ratio.
    """
    # Convert to numpy arrays
    if isinstance(velocity_dvl, list):
        velocity_dvl = np.array(velocity_dvl)
    if isinstance(conductivity, list):
        conductivity = np.array(conductivity)
    if isinstance(temperature, list):
        temperature = np.array(temperature)
    if isinstance(depth, list):
        depth = np.array(depth)
    if isinstance(latitude, list):
        latitude = np.array(latitude)
    if isinstance(longitude, list):
        longitude = np.array(longitude)

    # Check inputs type
    if not isinstance(velocity_dvl, (np.ndarray)):
        raise TypeError("Velocity DVL must be a list or a numpy array.")
    if not isinstance(conductivity, (np.ndarray)):
        raise TypeError("Conductivity must be a list or a numpy array.")
    if not isinstance(temperature, (np.ndarray)):
        raise TypeError("Temperature must be a list or a numpy array.")
    if not isinstance(depth, (np.ndarray)):
        raise TypeError("Depth must be a list or a numpy array.")
    if latitude is not None and not isinstance(latitude, (np.ndarray, float)):
        raise TypeError("Latitude must be a float or an array.")
    if longitude is not None and not isinstance(longitude, (np.ndarray, float)):
        raise TypeError("Longitude must be a float or an array.")
    if not isinstance(sound_velocity_ref, (int, float)):
        raise TypeError("Sound velocity reference must be a float or an int.")

    # Check shape of inputs if they are numpy arrays
    if velocity_dvl.ndim != 2 or (
        velocity_dvl.shape[0] != 3 and velocity_dvl.shape[1] != 3
    ):
        raise ValueError("velocity_dvl must be a 3xN or Nx3 numpy array.")
    conductivity = conductivity.squeeze()
    if conductivity.ndim > 1:
        raise ValueError("Conductivity must be a 1D array.")
    temperature = temperature.squeeze()
    if temperature.ndim > 1:
        raise ValueError("Temperature must be a 1D array.")
    depth = depth.squeeze()
    if depth.ndim > 1:
        raise ValueError("Depth must be a 1D array.")
    if latitude is not None and isinstance(latitude, np.ndarray):
        latitude = latitude.squeeze()
        if latitude.ndim > 1:
            raise ValueError("Latitude must be a 1D array.")
    if longitude is not None and isinstance(longitude, np.ndarray):
        longitude = longitude.squeeze()
        if longitude.ndim > 1:
            raise ValueError("Longitude must be a 1D array.")

    # If latitude is not provided, set it to 0
    if latitude is None:
        latitude = 0 if isinstance(depth, float) else np.zeros_like(depth)
    elif isinstance(latitude, float) and isinstance(depth, np.ndarray):
        latitude = np.full_like(depth, latitude)

    # If longitude is not provided, set it to 0
    if longitude is None:
        longitude = 0 if isinstance(depth, float) else np.zeros_like(depth)
    elif isinstance(longitude, float) and isinstance(depth, np.ndarray):
        longitude = np.full_like(depth, longitude)

    # Force Nx3 shape for arrays
    if velocity_dvl.shape[0] == 3 and velocity_dvl.shape[1] != 3:
        velocity_dvl = velocity_dvl.T

    # Check that the inputs are of the same shape
    if (
        conductivity.shape[0] != temperature.shape[0]
        or conductivity.shape[0] != depth.shape[0]
        or conductivity.shape[0] != latitude.shape[0]
        or conductivity.shape[0] != longitude.shape[0]
        or conductivity.shape[0] != velocity_dvl.shape[0]
    ):
        raise ValueError(
            "DVL velocity, conductivity, temperature, depth, latitude, and longitude must have the same shape."
        )

    # Check that the depth is negative
    if isinstance(depth, np.ndarray):
        if np.any(depth > 0):
            raise ValueError("Depth must be negative.")
    else:
        if depth > 0:
            raise ValueError("Depth must be negative.")

    # Check that the latitude is between -90 and 90
    if isinstance(latitude, np.ndarray):
        if np.any(latitude < -90) or np.any(latitude > 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
    else:
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")

    # Check that the longitude is between -360 and 360
    if isinstance(longitude, np.ndarray):
        if np.any(longitude < -360) or np.any(longitude > 360):
            raise ValueError("Longitude must be between -360 and 360 degrees.")
    else:
        if longitude < -360 or longitude > 360:
            raise ValueError("Longitude must be between -360 and 360 degrees.")

    # Calculate Sound velocity from CTD data
    sound_velocity_ctd = ctd2svel(conductivity, temperature, depth, latitude, longitude)
    sound_velocity_ratio = sound_velocity_ctd / sound_velocity_ref
    corrected_velocity_dvl = velocity_dvl * np.vstack(sound_velocity_ratio)
    median_sound_velocity_ratio = np.median(sound_velocity_ratio, axis=0)
    return corrected_velocity_dvl, median_sound_velocity_ratio


def cal_dvl_jck_so3(
    time_dvl: Union[np.ndarray, List[float]],
    time_ahrs: Union[np.ndarray, List[float]],
    time_position: Union[np.ndarray, List[float]],
    velocity_dvl: Union[np.ndarray, List[float]],
    rph_ahrs: Union[np.ndarray, List[float]],
    angular_rate_ahrs: Union[np.ndarray, List[float]],
    position: Union[np.ndarray, List[float]],
    low_pass_filter: bool = True,
    lever_arm: np.ndarray = [0, 0, 0],
    method: str = "min",
    force_so3: bool = True,
    zero_mean_sensor: bool = False,
    zero_mean_equation: bool = False,
):
    """
    Doppler alignment code using AHRS and DVL data to estimate the attitude of
    the DVL with respect to the vehicle frame give the position of an external
    aiding systems, such as LBL, given a previously known IMU extrinsic calibration
    and the lever arm between the DVL and the vehicle frame. The code is based on
    the work of [1].

    The solution can be estimated using least squares either with a regular
    least squares, or with SVD or with a nonlinear optimization using Pymanopt,
    which is the default as it computes the optimization considering the SO(3)
    constraints.

    [1] Kinsey, J. C., & Whitcomb, L. L. (2002, May). Towards in-situ calibration
        of gyro and doppler navigation sensors for precision underwater vehicle
        navigation. In Proceedings 2002 IEEE International Conference on Robotics
        and Automation (Cat. No. 02CH37292) (Vol. 4, pp. 4016-4023). IEEE.

    Args:
        time_dvl (np.ndarray): Time vector for DVL data.
        time_ahrs (np.ndarray): Time vector for AHRS data.
        time_position (np.ndarray): Time vector for depth data.
        velocity_dvl (np.ndarray): DVL velocity data in the instrument frame.
        rph_ahrs (np.ndarray): AHRS roll, pitch, and heading data.
        angular_rate_ahrs (np.ndarray): AHRS angular rate data in the instrument frame.
        position (np.ndarray): Position data from the external aiding system.
        low_pass_filter (bool): Apply a low-pass filter to the input signals. The
            cutoff frequency is set to 1/10 of the sampling frequency.
        lever_arm (np.ndarray): Lever arm from the DVL with respect to the vehicle
            frame. Default is [0, 0, 0].
        method (str): Optimization method to use. Options are 'ls' for least
            squares and 'min' for SO(3) minimization and 'svd' for singular value
            decomposition.
        force_so3 (bool): Force the solution to be in SO(3).

    Returns:
        rot_v_dvl (np.ndarray): Rotation matrix in SO(3) from the DVL to the vehicle
            frame.

    Raises:
        TypeError: If input types are not correct.
        ValueError: If input dimensions are not correct.
    """
    # Convert to numpy arrays
    if isinstance(time_dvl, list):
        time_dvl = np.array(time_dvl)
    if isinstance(time_ahrs, list):
        time_ahrs = np.array(time_ahrs)
    if isinstance(time_position, list):
        time_position = np.array(time_position)
    if isinstance(velocity_dvl, list):
        velocity_dvl = np.array(velocity_dvl)
    if isinstance(rph_ahrs, list):
        rph_ahrs = np.array(rph_ahrs)
    if isinstance(angular_rate_ahrs, list):
        angular_rate_ahrs = np.array(angular_rate_ahrs)
    if isinstance(position, list):
        position = np.array(position)
    if isinstance(lever_arm, list):
        lever_arm = np.array(lever_arm)

    # Check inputs
    if not isinstance(time_ahrs, np.ndarray):
        raise TypeError("time_ahrs must be a numpy array or list")
    if not isinstance(time_dvl, np.ndarray):
        raise TypeError("time_dvl must be a numpy array or list")
    if not isinstance(time_position, np.ndarray):
        raise TypeError("time_position must be a numpy array or list")
    if not isinstance(velocity_dvl, np.ndarray):
        raise TypeError("velocity_dvl must be a numpy array or list")
    if not isinstance(rph_ahrs, np.ndarray):
        raise TypeError("rph_ahrs must be a numpy array or list")
    if not isinstance(angular_rate_ahrs, np.ndarray):
        raise TypeError("angular_rate_ahrs must be a numpy array or list")
    if not isinstance(position, np.ndarray):
        raise TypeError("position must be a numpy array or list")
    if not isinstance(low_pass_filter, bool):
        raise TypeError("low_pass_filter must be a boolean")
    if not isinstance(lever_arm, np.ndarray):
        raise TypeError("lever_arm must be a numpy array or list")
    if not isinstance(force_so3, bool):
        raise TypeError("force_so3 must be a boolean")
    if not isinstance(method, str):
        raise TypeError("method must be a string")
    if not isinstance(zero_mean_sensor, bool):
        raise TypeError("zero_mean_sensor must be a boolean")
    if not isinstance(zero_mean_equation, bool):
        raise TypeError("zero_mean_equation must be a boolean")

    # Check dimensions
    time_ahrs = time_ahrs.squeeze()
    if time_ahrs.ndim >= 2:
        raise ValueError("The time_ahrs must be a (n, ), (n, 1) or (1, n) numpy array.")
    time_dvl = time_dvl.squeeze()
    if time_dvl.ndim >= 2:
        raise ValueError("The time_dvl must be a (n, ), (n, 1) or (1, n) numpy array.")
    time_position = time_position.squeeze()
    if time_position.ndim >= 2:
        raise ValueError(
            "The time_position must be a (n, ), (n, 1) or (1, n) numpy array."
        )
    if velocity_dvl.ndim != 2 or (
        velocity_dvl.shape[0] != 3 and velocity_dvl.shape[1] != 3
    ):
        raise ValueError("velocity_dvl must be a 3xN or Nx3 numpy array.")
    if rph_ahrs.ndim != 2 or (rph_ahrs.shape[0] != 3 and rph_ahrs.shape[1] != 3):
        raise ValueError("rph_ahrs must be a 3xN or Nx3 numpy array.")
    if angular_rate_ahrs.ndim != 2 or (
        angular_rate_ahrs.shape[0] != 3 and angular_rate_ahrs.shape[1] != 3
    ):
        raise ValueError("angular_rate_ahrs must be a 3xN or Nx3 numpy array.")
    if position.ndim != 2 or (position.shape[0] != 3 and position.shape[1] != 3):
        raise ValueError("position must be a 3xN or Nx3 numpy array.")
    lever_arm = lever_arm.squeeze()
    if lever_arm.ndim >= 2 or lever_arm.shape[0] != 3:
        raise ValueError("The lever_arm must be a (3, ), (1, 3) or (3, 1) numpy array.")

    # Check the optional parameters
    if method.lower() not in ["ls", "min", "svd"]:
        raise ValueError("method must be 'ls', 'min', or 'svd'")

    # Force Nx3 shape for arrays
    if velocity_dvl.shape[0] == 3 and velocity_dvl.shape[1] != 3:
        velocity_dvl = velocity_dvl.T
    if rph_ahrs.shape[0] == 3 and rph_ahrs.shape[1] != 3:
        rph_ahrs = rph_ahrs.T
    if angular_rate_ahrs.shape[0] == 3 and angular_rate_ahrs.shape[1] != 3:
        angular_rate_ahrs = angular_rate_ahrs.T
    if position.shape[0] == 3 and position.shape[1] != 3:
        position = position.T

    # Check if the time arrays are the same length
    if time_ahrs.shape[0] != rph_ahrs.shape[0]:
        raise ValueError(
            "The time_ahrs and rph_ahrs must have the same number of measurements."
        )
    if time_ahrs.shape[0] != angular_rate_ahrs.shape[0]:
        raise ValueError(
            "The time_ahrs and angular_rate_ahrs must have the same number of measurements."
        )
    if time_dvl.shape[0] != velocity_dvl.shape[0]:
        raise ValueError(
            "The time_dvl and velocity_dvl must have the same number of measurements."
        )
    if time_position.shape[0] != position.shape[0]:
        raise ValueError(
            "The time_position and position must have the same number of measurements."
        )

    # Filter input signals with a low-pass filter set to a cutoff frequency of 1/10
    # of the sampling frequency
    if low_pass_filter:
        # Sampling frequency
        frequency_dvl = 1 / median(difference(time_dvl))
        frequency_ahrs = 1 / median(difference(time_ahrs))
        frequency_position = 1 / median(difference(time_position))

        # Apply low-pass filter
        velocity_dvl = filter_lowpass(velocity_dvl, frequency_dvl, 0.1 * frequency_dvl)
        angular_rate_ahrs = filter_lowpass(
            angular_rate_ahrs, frequency_ahrs, 0.1 * frequency_ahrs
        )
        rph_ahrs = filter_lowpass(rph_ahrs, frequency_ahrs, 0.1 * frequency_ahrs)
        position = filter_lowpass(
            position, frequency_position, 0.1 * frequency_position
        )

    # Clip the measurements from DVL to the AHRS and depth time range
    time_range_max = min([max(time_ahrs), max(time_dvl)])
    time_range_min = max([min(time_ahrs), min(time_dvl)])
    filter_idx = (time_position >= time_range_min) & (time_position <= time_range_max)
    time_position = time_position[filter_idx]
    position = position[filter_idx]
    if position.shape[0] == 0:
        raise ValueError(
            "The time_position must have at least one measurement in the time range of the AHRS and DVL data."
        )

    # Resample the AHRS and depth data to the DVL time. Usually the AHRS data is
    # at a higher frequency than the DVL data.
    velocity_pos = resample(time_position, time_dvl, velocity_dvl)
    rph_pos = resample(time_position, time_ahrs, rph_ahrs)
    angular_rate_pos = resample(time_position, time_ahrs, angular_rate_ahrs)

    # Remove mean from the external aiding position data
    if zero_mean_sensor:
        position = remove_mean(position)

    # Uses as reference the IMU, i.e., the IMU is aligned with the vehicle frame
    model = _model(dvl_position_xyz=lever_arm)

    # Left side (alpha(t) from Eq. 10)
    # The original formulation doesn't consider the lever arm between the DVL
    # and the AHRS. Therefore, we add a modification to include it:
    # (Rw'*pw - Integral[Rw_dot' * pw] + Integral[Rw' * Rw_dot * T] )
    r_w = np.apply_along_axis(rph2rot, 1, rph_pos)
    r_w_dot = r_w * np.apply_along_axis(vec_to_so3, 1, angular_rate_pos)

    # Compute each term for the left-hand side
    # 1. Rw' * pw
    lhs_1a = np.squeeze(transpose(r_w) @ position[:, :, np.newaxis], axis=-1)
    # Remove offset induced by the initial position
    lhs_1 = remove_offset(lhs_1a, lhs_1a[0])
    # 2a. Rw_dot' * pw
    lhs_2a = np.squeeze(transpose(r_w_dot) @ position[:, :, np.newaxis], axis=-1)
    # 2b. Integral[Rw_dot' * pw], using trapezoidal numerical integration
    lhs_2 = -cumulative_trapezoid(lhs_2a, x=time_position, axis=0, initial=0)
    # 3. Rw' * Rw_dot * T
    lhs_3a = np.squeeze(
        transpose(r_w)
        @ r_w_dot
        @ np.tile(np.vstack(model.dvl.position_xyz), (time_position.shape[0], 1, 1)),
        axis=-1,
    )
    # 3b. Integral[Rw' * Rw_dot * T], using trapezoidal numerical integration
    lhs_3 = cumulative_trapezoid(lhs_3a, x=time_position, axis=0, initial=0)

    # Combine all terms
    LHS = lhs_1 + lhs_2 + lhs_3

    # Right side (beta(t) from Eq. 10)
    RHS = cumulative_trapezoid(velocity_pos, x=time_position, axis=0, initial=0)

    # Remove mean from the equations
    if zero_mean_equation:
        LHS = remove_mean(LHS)
        RHS = remove_mean(RHS)

    # Compute the solution
    # Solve the optimization problem (LHS = X @ RHS)
    # Least squares
    if method.lower() == "ls":
        N = LHS.shape[0]
        A = np.zeros((3 * N, 9))

        # Use kronecker product to write R as a vector
        for i in range(N):
            A[3 * i : 3 * i + 3, :] = np.kron(RHS[i, :].T, np.eye(3, dtype=np.float64))

        # Flatten the LHS matrix
        b = LHS.reshape(3 * N, 1)

        # Solve the least squares problem
        x = np.linalg.lstsq(A, b, rcond=None)[0]

    # Singular value decomposition
    elif method.lower() == "svd":
        # Cross covariance matrix
        A = LHS.T @ RHS
        U, _, Vt = np.linalg.svd(A)
        x = U @ Vt

    # Pymanopt
    elif method.lower() == "min":
        x = so3_optimization(_objective_function_cal_dvl_jck, LHS, RHS)

    # Reshape the column-wise stacked solution into a 3x3 matrix
    rot_v_dvl = x.reshape(3, 3, order="F") if method == "ls" else x

    # Force the solution to be in SO(3)
    if force_so3 and method != "min":
        rot_v_dvl = project_to_so3(rot_v_dvl)

    return rot_v_dvl


def _objective_function_cal_dvl_jck(
    x: np.ndarray,
    LHS: np.ndarray,
    RHS: np.ndarray,
) -> float:
    """
    Objective function to minimize the sum of squared residuals.

    Args:
        X (np.ndarray): Optimization variables.
        LHS (np.ndarray): Left hand side of the position-based calibration.
        RHS (np.ndarray): Right hand side of the position-based calibration.

    Returns:
        float: Sum of squared residuals.
    """
    x_3d = np_ag.tile(x, (LHS.shape[0], 1, 1))
    cost = np_ag.squeeze(
        LHS[:, :, np_ag.newaxis] - x_3d @ RHS[:, :, np_ag.newaxis], axis=-1
    )
    cost = np_ag.sum(np_ag.linalg.norm(cost, axis=1) ** 2)
    return cost


class _pose:
    def __init__(
        self,
        orientation_rph: Union[List, np.ndarray] = None,
        position_xyz: Union[List, np.ndarray] = None,
    ) -> None:
        if orientation_rph is None:
            self.orientation_rph = np.array([0, 0, 0])
        else:
            self.orientation_rph = np.array(orientation_rph)
        if position_xyz is None:
            self.position_xyz = np.array([0, 0, 0])
        else:
            self.position_xyz = np.array(position_xyz)

    def transformation_matrix(self) -> np.ndarray:
        """
        Compute the transformation matrix from the pose.

        Returns:
            np.ndarray: Transformation matrix.
        """
        return xyzrph2matrix(
            np.concatenate((self.position_xyz, self.orientation_rph), axis=0)
        )


class _model:
    """
    Model class to store the DVL and AHRS extrinsics.
    """

    def __init__(
        self,
        dvl_orientation_rph: Union[List, np.ndarray] = None,
        dvl_position_xyz: Union[List, np.ndarray] = None,
        ahrs_orientation_rph: Union[List, np.ndarray] = None,
        ahrs_position_xyz: Union[List, np.ndarray] = None,
    ) -> None:
        self.dvl = _pose(dvl_orientation_rph, dvl_position_xyz)
        self.ahrs = _pose(ahrs_orientation_rph, ahrs_position_xyz)
