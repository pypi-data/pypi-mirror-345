"""
This module contains functions to estimate the state of a vehicle using multiple inputs.

Functions:
    navdvl_dead_reckoning: Estimate the position of a vehicle using DVL data based on a dead reckoning approach.
    navdvl_kf: Estimate the position of a vehicle using DVL data based on a Kalman filter approach.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

from typing import List, Tuple, Union

import numpy as np

from navlib.math import difference, remove_offset, rph2rot

from .kalman_filter import kf_lti_discretize, kf_predict, kf_update


def navdvl_dead_reckoning(
    velocity: Union[np.ndarray, List[float]],
    rph: Union[np.ndarray, List[float]],
    time: Union[np.ndarray, List[float]] = None,
    dt: Union[float, int] = None,
    initial_state: Union[np.ndarray, List[float]] = None,
    velocity_frame: str = "body",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Position estimation using DVL data based on a dead reckoning approach. The
    function integrates the velocity data to estimate the position of the
    vehicle, where the integration can be over a fixed time step or based on
    the time vector. Additionally, the velocity can be either provided in the
    body frame or the world frame.

    Args:
        velocity (np.ndarray, list): Velocity data in the body or world frame.
        rph (np.ndarray, list): Roll, pitch, and heading data.
        time (np.ndarray, list): Time vector.
        dt (float, int): Time step.
        initial_state (np.ndarray, list): Initial position.
        velocity_frame (str): Velocity frame.

    Returns:
        position (np.ndarray): Estimated position.
        rph (np.ndarray): Roll, pitch, and heading data.

    Raises:
        TypeError: If the input is not a numpy array.
        ValueError: If the input is not correct.
    """
    # Convert to numpy arrays
    if isinstance(velocity, list):
        velocity = np.array(velocity)
    if isinstance(rph, list):
        rph = np.array(rph)
    if isinstance(time, list):
        time = np.array(time)
    if initial_state is not None and isinstance(initial_state, list):
        initial_state = np.array(initial_state)

    # Check if the input is correct
    if not isinstance(velocity, np.ndarray):
        raise TypeError("Velocity must be a numpy array")
    if not isinstance(rph, np.ndarray):
        raise TypeError("RPH must be a numpy array")
    if time is not None and not isinstance(time, np.ndarray):
        raise TypeError("Time must be a numpy array")
    if initial_state is not None and not isinstance(initial_state, np.ndarray):
        raise TypeError("Initial state must be a numpy array")
    if dt is not None and not isinstance(dt, (float, int)):
        raise TypeError("dt must be a float or an integer")
    if dt is not None and time is not None:
        raise ValueError("dt and time cannot be used together")
    if dt is not None and dt <= 0:
        raise ValueError("dt must be greater than zero")
    if velocity_frame and not isinstance(velocity_frame, str):
        raise TypeError("velocity_frame must be a string")
    if velocity_frame not in ["body", "world"]:
        raise ValueError("velocity_frame must be either 'body' or 'world'")

    # For matrices to be n x 3
    if velocity.ndim != 2 or (velocity.shape[1] != 3 and velocity.shape[0] != 3):
        raise ValueError("Velocity must be a matrix with 3 columns")
    if velocity.shape[0] == 3 and velocity.shape[1] != 3:
        velocity = velocity.T
    if rph.ndim != 2 or (rph.shape[1] != 3 and rph.shape[0] != 3):
        raise ValueError("RPH must be a matrix with 3 columns")
    if rph.shape[0] == 3 and rph.shape[1] != 3:
        rph = rph.T
    if time is not None:
        time = time.squeeze()
        if time.ndim != 1:
            raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")
    if initial_state is not None:
        initial_state = initial_state.squeeze()
        if initial_state.ndim != 1:
            raise ValueError(
                "The initial state must be a (3, ), (3, 1) or (1, 3) numpy array."
            )
        if initial_state.size != 3:
            raise ValueError("The initial state must have 3 elements.")

    # Initial state
    x0 = initial_state if initial_state is not None else np.zeros(3)

    # Delta time vector
    if time is not None:
        dt_vec = difference(time).reshape(-1, 1)
    else:
        dt_vec = np.ones((velocity.shape[0] - 1, 1)) * dt

    if velocity_frame == "body":
        # Initialize velocity in the world frame vector and convert body frame velocities to world frame
        velocity_world = np.zeros(velocity.shape)

        for ix in range(velocity.shape[0]):
            velocity_world[ix, :] = (
                rph2rot(rph[ix, :]) @ velocity[ix, :].reshape(-1, 1)
            ).squeeze()
    else:
        velocity_world = velocity

    # Integrate velocity
    xyz = remove_offset(np.cumsum(velocity_world[:-1] * dt_vec, axis=0), -x0)
    return xyz, rph[1:]


def navdvl_kf(
    velocity: Union[np.ndarray, List[float]],
    rph: Union[np.ndarray, List[float]],
    time: Union[np.ndarray, List[float]] = None,
    dt: Union[float, int] = None,
    initial_state: Union[np.ndarray, List[float]] = None,
    velocity_frame: str = "body",
    k1: float = 1.0,
    k2: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Position estimation using DVL data based on a Kalman filter approach. The
    function integrates the velocity data to estimate the position of the
    vehicle, where the integration can be over a fixed time step or based on
    the time vector. Additionally, the velocity can be either provided in the
    body frame or the world frame.

    Args:
        velocity (np.ndarray, list): Velocity data in the body or world frame.
        rph (np.ndarray, list): Roll, pitch, and heading data.
        time (np.ndarray, list): Time vector.
        dt (float, int): Time step.
        initial_state (np.ndarray, list): Initial position.
        velocity_frame (str): Velocity frame.
        k1 (float): Process noise covariance.
        k2 (float): Measurement noise covariance.

    Returns:
        position (np.ndarray): Estimated position.
        rph (np.ndarray): Roll, pitch, and heading data.

    Raises:
        TypeError: If the input is not a numpy array.
        ValueError: If the input is not correct.
    """
    # Convert to numpy arrays
    if isinstance(velocity, list):
        velocity = np.array(velocity)
    if isinstance(rph, list):
        rph = np.array(rph)
    if isinstance(time, list):
        time = np.array(time)
    if initial_state is not None and isinstance(initial_state, list):
        initial_state = np.array(initial_state)

    # Check if the input is correct
    if not isinstance(velocity, np.ndarray):
        raise TypeError("Velocity must be a numpy array")
    if not isinstance(rph, np.ndarray):
        raise TypeError("RPH must be a numpy array")
    if time is not None and not isinstance(time, np.ndarray):
        raise TypeError("Time must be a numpy array")
    if initial_state is not None and not isinstance(initial_state, np.ndarray):
        raise TypeError("Initial state must be a numpy array")
    if dt is not None and not isinstance(dt, (float, int)):
        raise TypeError("dt must be a float or an integer")
    if dt is not None and time is not None:
        raise ValueError("dt and time cannot be used together")
    if dt is not None and dt <= 0:
        raise ValueError("dt must be greater than zero")
    if velocity_frame and not isinstance(velocity_frame, str):
        raise TypeError("velocity_frame must be a string")
    if velocity_frame not in ["body", "world"]:
        raise ValueError("velocity_frame must be either 'body' or 'world'")
    if not isinstance(k1, (int, float)):
        raise TypeError("k1 must be an integer or a float")
    k1 = float(k1)
    if not isinstance(k2, (int, float)):
        raise TypeError("k2 must be an integer or a float")
    k2 = float(k2)

    # For matrices to be n x 3
    if velocity.ndim != 2 or (velocity.shape[1] != 3 and velocity.shape[0] != 3):
        raise ValueError("Velocity must be a matrix with 3 columns")
    if velocity.shape[0] == 3 and velocity.shape[1] != 3:
        velocity = velocity.T
    if rph.ndim != 2 or (rph.shape[1] != 3 and rph.shape[0] != 3):
        raise ValueError("RPH must be a matrix with 3 columns")
    if rph.shape[0] == 3 and rph.shape[1] != 3:
        rph = rph.T
    if time is not None:
        time = time.squeeze()
        if time.ndim != 1:
            raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")
    if initial_state is not None:
        initial_state = initial_state.squeeze()
        if initial_state.ndim != 1:
            raise ValueError(
                "The initial state must be a (3, ), (3, 1) or (1, 3) numpy array."
            )
        if initial_state.size != 3:
            raise ValueError("The initial state must have 3 elements.")

    # Initial state
    x0 = initial_state if initial_state is not None else np.zeros(3)

    # Delta time vector
    if time is not None:
        dt_vec = difference(time)
    else:
        dt_vec = np.ones((velocity.shape[0] - 1,)) * dt

    # Kalman Model
    f1_matrix = np.vstack(
        [np.hstack([np.zeros((3, 3)), np.eye(3)]), np.zeros((3, 6))]
    )  # State transition matrix
    bc_matrix = np.zeros((6, 1))  # No inputs
    qc_matrix = np.eye(6, dtype=np.float64) * k1  # Process Noise Covariance
    r_matrix = np.eye(3, dtype=np.float64) * k2  # Measurement Noise Covariance

    # Kalman Filter
    h1_matrix = _navdvl_kf_measurement_model([0.0, 0.0, 0.0])
    n, m = f1_matrix.shape

    # Matrices definitions
    mm_matrix = np.zeros([n, velocity.shape[0]])  # States mean matrix
    pp_matrix = np.zeros([n, m, velocity.shape[0]])  # State covariance matrix
    aa_matrix = np.zeros([n, m, velocity.shape[0]])  # State transition matrix
    qq_matrix = np.zeros([n, m, velocity.shape[0]])  # Process noise covariance
    kk_matrix = np.zeros([n, h1_matrix.shape[0], velocity.shape[0]])  # Kalman gains

    # Initial guesses for the state mean and covariance.
    x = np.hstack([x0, np.zeros((3,))])
    p_matrix = np.eye(6, dtype=np.float64) * 0.1

    # Filtering steps.
    for ix in range(velocity.shape[0] - 1):
        # Discretization of the continous-time system (dtk)
        dtk = float(dt_vec[ix])

        ak_matrix, _, qk_matrix = kf_lti_discretize(
            f1_matrix, bc_matrix, qc_matrix, dtk
        )
        aa_matrix[:, :, ix + 1] = ak_matrix
        qq_matrix[:, :, ix + 1] = qk_matrix
        x, p_matrix = kf_predict(x, p_matrix, ak_matrix, qk_matrix)
        if velocity_frame == "body":
            hk_matrix = _navdvl_kf_measurement_model(rph[ix])
        else:
            hk_matrix = _navdvl_kf_measurement_model([0.0, 0.0, 0.0])
        x, p_matrix, kk, _, _ = kf_update(
            x, p_matrix, velocity[ix], hk_matrix, r_matrix
        )

        mm_matrix[:, ix + 1] = x
        pp_matrix[:, :, ix + 1] = p_matrix
        kk_matrix[:, :, ix + 1] = kk

    # Filtered position
    position_filtered = mm_matrix[:3, :].T

    # Filtered velocity
    velocity_filtered = mm_matrix[3:, :].T

    return position_filtered, velocity_filtered


def _navdvl_kf_measurement_model(rph: np.ndarray) -> np.ndarray:
    """
    Measurement model for the Kalman filter.

    Args:
        rph (np.ndarray): Roll, pitch, and heading data.

    Returns:
        np.ndarray: Measurement model.
    """
    return np.hstack([np.zeros((3, 3)), rph2rot(rph).T])
