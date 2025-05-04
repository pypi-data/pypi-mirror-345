"""
This module provides functions to work with Kalman filters.

Functions:
    kf_lti_discretize: Discretize a Linear Time-Invariant (LTI) system using the matrix fraction decomposition.
    kf_predict: Prediction step of the Kalman filter.
    kf_update: Update step of the Kalman filter.

Classes:
    UUV_EKF: Extended Kalman Filter (EKF) class for uncrewed underwater vehicles.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

from collections import deque
from typing import List, Tuple, Union
from warnings import warn

import numpy as np
from scipy.linalg import expm
from scipy.stats import chi2

from navlib.math import (
    axis_ang3,
    left_quat_product_matrix,
    norm,
    quat2rot,
    right_quat_product_matrix,
)


def kf_lti_discretize(
    Ac: np.ndarray,
    Bc: np.ndarray = None,
    Qc: np.ndarray = None,
    dt: float = 1,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Discretize a Linear Time-Invariant (LTI) system using the matrix fraction decomposition
    for use in a discrete-time Kalman filter.

    Args:
        Ac (np.ndarray): Continuos state transition matrix.
        Bc (np.ndarray): Continuos input matrix, by default None.
        Qc (np.ndarray): Continuos covariance matrix, by default None.
        dt (float): Time step, by default 1.

    Returns:
        transition_mat (np.ndarray): Discrete state transition matrix.
        inpu_mat (np.ndarray): Discrete input matrix.
        covariance_mat (np.ndarray): Discrete covariance matrix.

    Raises:
        TypeError: If Ac, Bc or Qc are not numpy arrays.
        ValueError: If Ac is not a 2D matrix, if Ac and Bc do not have the same number of rows,
            if Qc is not a square matrix, if Qc does not have the same number of rows as Ac.
    """
    # Convert to numpy array
    if isinstance(Ac, list):
        Ac = np.array(Ac)
    if isinstance(Bc, list):
        Bc = np.array(Bc)
    if isinstance(Qc, list):
        Qc = np.array(Qc)

    # Check inputs type
    if not isinstance(Ac, np.ndarray):
        raise TypeError("Ac must be a numpy array")
    if Bc is not None and not isinstance(Bc, np.ndarray):
        raise TypeError("Bc must be a numpy array")
    if Qc is not None and not isinstance(Qc, np.ndarray):
        raise TypeError("Qc must be a numpy array")
    if not isinstance(dt, (int, float)):
        raise TypeError("dt must be a number")

    # Force the input matrix to be a column vector
    if Bc is not None and Bc.ndim == 1:
        Bc = Bc[:, np.newaxis] if Bc.ndim == 1 else np.vstack(Bc)

    # Check that the shape of the matrices is correct
    if Ac.ndim != 2:
        raise ValueError("Ac must be a 2D matrix")
    if Bc is not None and Bc.shape[0] != Ac.shape[0]:
        raise ValueError("Ac and Bc must have the same number of rows")
    if Qc is not None and Qc.shape[0] != Qc.shape[1]:
        raise ValueError("Qc must be a square matrix")
    if Qc is not None and Qc.shape[0] != Ac.shape[0]:
        raise ValueError("Qc must have the same number of rows as Ac")

    # Check the number of states
    n = Ac.shape[0]

    # Default to zero non provided matrices
    if Bc is None:
        Bc = np.zeros([n, 1])

    if Qc is None:
        Qc = np.zeros([n, n])

    # Discretize state transition and input matrix (close form)
    # Ad = expm(Ac*dt)
    M = np.vstack([np.hstack([Ac, Bc]), np.zeros([1, n + 1])])
    ME = expm(M * dt)

    # Discretize state transition and input matrix
    Ad = ME[:n, :n]
    Bd = ME[:n, n:]

    # Discretize Covariance: by (Van Loan, 1978)
    F = np.vstack([np.hstack([-Ac, Qc]), np.hstack([np.zeros([n, n]), Ac.T])])
    G = expm(F * dt)
    Qd = np.dot(G[n:, n:].T, G[:n, n:])

    # # Discretize Covariance: by matrix fraction decomposition
    # Phi = vstack([hstack([Ac,            Qc]),
    #               hstack([np.zeros([n,n]),-Ac.T])])
    # AB  = np.dot (scipy.linalg.expm(Phi*dt), vstack([np.zeros([n,n]),np.eye(n)]))
    # Qd  = np.linalg.solve(AB[:n,:].T, AB[n:2*n,:].T).T

    return Ad, Bd, Qd


def kf_predict(
    x: np.ndarray,
    P: np.ndarray,
    A: np.ndarray = None,
    Q: np.ndarray = None,
    B: np.ndarray = None,
    u: np.ndarray = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prediction step of the Kalman filter.

    Args:
        x (np.ndarray): State mean.
        P (np.ndarray): State covariance.
        A (np.ndarray): State transition matrix, by default None.
        Q (np.ndarray): Process noise covariance, by default None.
        B (np.ndarray): Input matrix, by default None.
        u (np.ndarray): Input vector, by default None.

    Returns:
        updated_state_mean (np.ndarray): Updated state mean.
        updated_state_cov (np.ndarray): Updated state covariance.

    Raises:
        TypeError: If A, Q, B, u, x or P are not numpy arrays.
        ValueError: If A is not a 2D matrix, if x and A do not have the same number of rows,
            if B is not a 2D matrix, if the number of columns in B is not equal to the number of rows in u,
            if B does not have the same number of rows as x, if P is not a square matrix,
            if P is not a square matrix, if Q is not a square matrix, if Q does not have the same number of rows as A.
    """
    # Convert to numpy array
    if isinstance(A, list):
        A = np.array(A)
    if isinstance(Q, list):
        Q = np.array(Q)
    if isinstance(B, list):
        B = np.array(B)
    if isinstance(u, list):
        u = np.array(u)
    if isinstance(x, list):
        x = np.array(x)
    if isinstance(P, list):
        P = np.array(P)

    # Check inputs type
    if A is not None and not isinstance(A, np.ndarray):
        raise TypeError("A must be a numpy array")
    if Q is not None and not isinstance(Q, np.ndarray):
        raise TypeError("Q must be a numpy array")
    if B is not None and not isinstance(B, np.ndarray):
        raise TypeError("B must be a numpy array")
    if u is not None and not isinstance(u, np.ndarray):
        raise TypeError("u must be a numpy array")
    if not isinstance(x, np.ndarray):
        raise TypeError("x must be a numpy array")
    if not isinstance(P, np.ndarray):
        raise TypeError("P must be a numpy array")

    # Force the state, input and control matrices to be column vectors
    x = x[:, np.newaxis] if x.ndim == 1 else x
    if u is not None:
        u = u[:, np.newaxis] if u.ndim == 1 else u

    # Check that the shape of the matrices is correct
    if A is not None and A.ndim != 2:
        raise ValueError("A must be a 2D matrix")
    if A is not None and x.shape[0] != A.shape[0]:
        raise ValueError("x and A must have the same number of rows")
    if B is not None and B.ndim != 2:
        raise ValueError("B must be a 2D matrix")
    if u is not None and B is not None and u.shape[0] != B.shape[1]:
        raise ValueError(
            "The number of columns in B must be equal to the number of rows in u"
        )
    if B is not None and B.shape[0] != x.shape[0]:
        raise ValueError("B must have the same number of rows as x")
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be a square matrix")
    if A is not None and P.shape[0] != A.shape[0]:
        raise ValueError("P must have the same number of rows as A")
    if Q is not None and (Q.ndim != 2 or Q.shape[0] != Q.shape[1]):
        raise ValueError("Q must be a square matrix")
    if Q is not None and A is not None and Q.shape[0] != A.shape[0]:
        raise ValueError("Q must have the same number of rows as A")

    # Check Arguments
    n = A.shape[0] if A is not None else x.shape[0]

    # Default state transition matrix to the identity matrix if not provided
    if A is None:
        A = np.eye(n)

    # Default process noise covariance to zero matrix if not provided
    if Q is None:
        Q = np.zeros((n, n))

    # Default input matrix to the identity matrix if not provided
    if B is None and u is not None:
        B = np.eye(n, u.shape[0])

    # Prediction step
    # State
    if u is None:
        x = A @ x
    else:
        x = A @ x + B @ u

    # Covariance
    P = A @ P @ A.T + Q

    return x.squeeze(), P.squeeze()


def kf_update(
    x: np.ndarray,
    P: np.ndarray,
    y: np.ndarray,
    H: np.ndarray,
    R: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Update step of the Kalman filter.

    Args:
        x (np.ndarray): State mean.
        P (np.ndarray): State covariance.
        y (np.ndarray): Measurement.
        H (np.ndarray): Measurement matrix.
        R (np.ndarray): Measurement noise covariance.

    Returns:
        x (np.ndarray): Updated state mean.
        P (np.ndarray): Updated state covariance.
        K (np.ndarray): Kalman Gain.
        dy (np.ndarray): Measurement residual.
        S (np.ndarray): Covariance residual.

    Raises:
        TypeError: If x, P, y, H or R are not numpy arrays.
        ValueError: If x is not a numpy array, if P is not a numpy array, if y is not a numpy array,
            if H is not a 2D matrix, if R is not a square matrix, if P is not a square matrix,
            if P does not have the same number of rows as x, if H does not have the same number of columns as rows in x,
            if x and y do not have the same number of rows, if R does not have the same number of rows as y.
    """
    # Convert to numpy array
    if isinstance(x, list):
        x = np.array(x)
    if isinstance(P, list):
        P = np.array(P)
    if isinstance(y, list):
        y = np.array(y)
    if isinstance(H, list):
        H = np.array(H)
    if isinstance(R, list):
        R = np.array(R)

    # Check inputs type
    if not isinstance(x, np.ndarray):
        raise TypeError("x must be a numpy array")
    if not isinstance(P, np.ndarray):
        raise TypeError("P must be a numpy array")
    if not isinstance(y, np.ndarray):
        raise TypeError("y must be a numpy array")
    if not isinstance(H, np.ndarray):
        raise TypeError("H must be a numpy array")
    if not isinstance(R, np.ndarray):
        raise TypeError("R must be a numpy array")

    # Force the state and measurements to be column vectors
    x = x[:, np.newaxis] if x.ndim == 1 else x
    y = y[:, np.newaxis] if y.ndim == 1 else y

    # Check dimensions
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be a square matrix")
    if P.shape[0] != x.shape[0]:
        raise ValueError("P must have the same number of rows as x")
    if H.ndim != 2:
        raise ValueError("H must be a 2D matrix")
    if x.shape[0] != H.shape[1]:
        raise ValueError("H must have the same number of columns as rows in x")
    if R.ndim != 2 or R.shape[0] != R.shape[1]:
        raise ValueError("R must be a square matrix")
    if R.shape[0] != y.shape[0]:
        raise ValueError("R must have the same number of rows as y")

    # Compute measurement residual
    dy = y - H @ x
    # Compute covariance residual
    S = R + H @ P @ H.T
    # Compute Kalman Gain
    K = P @ H.T @ np.linalg.inv(S)

    # Update state estimate
    x = x + K @ dy
    P = P - K @ H @ P

    return x.squeeze(), P.squeeze(), K.squeeze(), dy.squeeze(), S.squeeze()


class UUV_EKF:
    """
    Extended Kalman Filter (EKF) class for uncrewed underwater vehicles.
    This class implements the Extended Kalman Filter (EKF) algorithm for state estimation
    of an uncrewed underwater vehicle using AHRS, DVL, Depth sensors and USBL asynchronous measurements.
    """

    def __init__(
        self,
        bottom_height: bool = False,
        covariance_dvl_velocity: Union[float, np.ndarray, List[float]] = 0.01,
        covariance_dvl_bottom_height: float = 0.01,
        covariance_ahrs_quaternion: Union[float, np.ndarray, List[float]] = 0.1,
        covariance_ahrs_angular_rate: Union[float, np.ndarray, List[float]] = 0.1,
        covariance_depth: float = 0.001,
        covariance_position: Union[float, np.ndarray, List[float]] = 10.0,
    ) -> None:
        """
        Extended Kalman Filter (EKF) class.

        This class implements the Extended Kalman Filter (EKF) algorithm for state estimation
        of an uncrewed underwater vehicle using AHRS, DVL and Depth sensor asynchronous measurements.

        Args:
            bottom_height (bool): If True, the EKF will estimate the bottom height.
                If False, the EKF will not estimate the bottom height.
            covariance_dvl_velocity (Union[float, np.ndarray, List[float]]): Covariance for DVL velocity measurements.
                It must be a float or a (3, ) array.
            covariance_dvl_bottom_height (float): Covariance for DVL bottom height measurements.
            covariance_ahrs_quaternion (float): Covariance for AHRS quaternion measurements. It must be a (3, ) array.
                It uses the small angle approximation, where the covariance for qx, qy, qz is approximated with the
                covariance for roll, pitch and yaw angles.
            covariance_ahrs_angular_rate (Union[float, np.ndarray, List[float]]): Covariance for AHRS angular rate measurements.
                It must be a float or a (3, ) array.
            covariance_depth (float): Covariance for depth measurements.
            covariance_position (Union[float, np.ndarray, List[float]]): Covariance for position measurements.
                It must be a float or a (2, ) array.
        """
        # Convert to a numpy arrays if they are lists
        if isinstance(covariance_dvl_velocity, list):
            covariance_dvl_velocity = np.array(covariance_dvl_velocity)
        if isinstance(covariance_ahrs_quaternion, list):
            covariance_ahrs_quaternion = np.array(covariance_ahrs_quaternion)
        if isinstance(covariance_ahrs_angular_rate, list):
            covariance_ahrs_angular_rate = np.array(covariance_ahrs_angular_rate)
        if isinstance(covariance_position, list):
            covariance_position = np.array(covariance_position)

        # Types checking
        if not isinstance(bottom_height, bool):
            raise TypeError("bottom_height must be a boolean")
        if not isinstance(covariance_dvl_velocity, (float, np.ndarray, list)):
            raise TypeError("covariance_dvl_velocity must be a float or a (3, ) array")
        if not isinstance(covariance_dvl_velocity, float):
            covariance_dvl_velocity = covariance_dvl_velocity.squeeze()
            if covariance_dvl_velocity.ndim != 1:
                raise ValueError("covariance_dvl_velocity must be a (3, ) array")
            if covariance_dvl_velocity.shape[0] != 3:
                raise ValueError("covariance_dvl_velocity must be a (3, ) array")
        if not isinstance(covariance_dvl_bottom_height, float):
            raise TypeError("covariance_dvl_bottom_height must be a float")
        if not isinstance(covariance_ahrs_quaternion, (float, np.ndarray)):
            raise TypeError(
                "covariance_ahrs_quaternion must be a float or a (3, ) array"
            )
        if not isinstance(covariance_ahrs_angular_rate, (float, np.ndarray)):
            raise TypeError(
                "covariance_ahrs_angular_rate must be a float or a (3, ) array"
            )
        if not isinstance(covariance_ahrs_angular_rate, float):
            covariance_ahrs_angular_rate = covariance_ahrs_angular_rate.squeeze()
            if covariance_ahrs_angular_rate.ndim != 1:
                raise ValueError("covariance_ahrs_angular_rate must be a (3, ) array")
            if covariance_ahrs_angular_rate.shape[0] != 3:
                raise ValueError("covariance_ahrs_angular_rate must be a (3, ) array")
        if not isinstance(covariance_ahrs_quaternion, float):
            covariance_ahrs_quaternion = covariance_ahrs_quaternion.squeeze()
            if covariance_ahrs_quaternion.ndim != 1:
                raise ValueError("covariance_ahrs_quaternion must be a (3, ) array")
            if covariance_ahrs_quaternion.shape[0] != 3:
                raise ValueError("covariance_ahrs_quaternion must be a (3, ) array")
        if not isinstance(covariance_depth, float):
            raise TypeError("covariance_depth must be a float")
        if not isinstance(covariance_position, (float, np.ndarray)):
            raise TypeError("covariance_position must be a float or a (2, ) array")
        if not isinstance(covariance_position, float):
            covariance_position = covariance_position.squeeze()
            if covariance_position.ndim != 1:
                raise ValueError("covariance_position must be a (2, ) array")
            if covariance_position.shape[0] != 2:
                raise ValueError("covariance_position must be a (2, ) array")

        # State Vector: [x, y, z, qx, qy, qz, qw, vx, vy, vz, wx, wy, wz, bh (optional)]
        self._current_state = np.r_[np.zeros(6), np.ones(1), np.zeros(6)]
        if bottom_height:
            self._current_state = np.r_[self._current_state, np.zeros(1)]
        self._state_dim = self._current_state.shape[0]

        # Process noise covariance
        self._q0_velocity = 1e-3 * np.eye(3, dtype=np.float64)

        # Sensor dt history
        self._imu_dt = deque([np.nan] * 5, maxlen=5)
        self._imu_last_timestamp = 0.0
        self._dvl_dt = deque([np.nan] * 5, maxlen=5)
        self._dvl_last_timestamp = 0.0
        self._depth_dt = deque([np.nan] * 5, maxlen=5)
        self._depth_last_timestamp = 0.0
        self._position_dt = deque([np.nan] * 5, maxlen=5)
        self._position_last_timestamp = 0.0

        # Measurements
        # XY position - Measurement model matrix
        H_position = np.zeros((2, self.state_dim))
        H_position[:, :2] = np.eye(2, dtype=np.float64)
        self._H_position = H_position
        # XY position - Measurement noise covariance
        if isinstance(covariance_position, float):
            self._R_position = np.eye(2, dtype=np.float64) * covariance_position
        else:
            self._R_position = np.diag(covariance_position)
        # Depth - Measurement model matrix
        H_depth = np.zeros((1, self.state_dim))
        H_depth[0, 2] = 1
        self._H_depth = H_depth
        # Depth - Measurement noise covariance
        self._R_depth = np.eye(1, dtype=np.float64) * covariance_depth
        # AHRS - Measurement model matrix
        H_ahrs = np.zeros((7, self.state_dim))
        H_ahrs[:4, 3:7] = np.eye(4, dtype=np.float64)
        H_ahrs[4:7, 10:13] = np.eye(3, dtype=np.float64)
        self._H_ahrs = H_ahrs
        # AHRS - Measurement noise covariance
        self._R_ahrs = np.zeros((7, 7), dtype=np.float64)
        # Quaternion covariance: we will use the small angle approximation;
        # therefore, we will use the covariance of roll, pitch and yaw angles
        # and leave the scalar component as 0.0.
        if isinstance(covariance_ahrs_quaternion, float):
            self._R_ahrs[:3, :3] = (
                np.eye(3, dtype=np.float64) * covariance_ahrs_quaternion
            )
        else:
            self._R_ahrs[:3, :3] = np.diag(covariance_ahrs_quaternion)
        if isinstance(covariance_ahrs_angular_rate, float):
            self._R_ahrs[4:7, 4:7] = (
                np.eye(3, dtype=np.float64) * covariance_ahrs_angular_rate
            )
        else:
            self._R_ahrs[4:7, 4:7] = np.diag(covariance_ahrs_angular_rate)
        # Linear velocity - Measurement model matrix
        H_vel = np.zeros((3, self.state_dim))
        H_vel[:, 7:10] = np.eye(3, dtype=np.float64)
        self._H_vel = H_vel
        # Linear velocity - Measurement noise covariance
        if isinstance(covariance_dvl_velocity, float):
            self._R_vel = np.eye(3, dtype=np.float64) * covariance_dvl_velocity
        else:
            self._R_vel = np.diag(covariance_dvl_velocity)
        # Bottom height - Measurement model matrix
        H_bottom_height = np.zeros((1, self.state_dim))
        H_bottom_height[0, -1] = 1
        self._H_bottom_height = H_bottom_height
        # Bottom height - Measurement noise covariance
        self._R_bottom_height = (
            np.eye(1, dtype=np.float64) * covariance_dvl_bottom_height
        )

        # Velocity Filtering
        self._velocity_d_squared_acummulted = 0.0
        self._velocity_d_squared_count = 0
        self._velocity_q_tuner = _QTuner()

        # Process noise covariance
        initial_dt = 0.01
        self._current_covariance = self._process_noise_covariance(initial_dt)

    @property
    def current_state(self) -> np.ndarray:
        """
        Get the current state ($x_t$) of the EKF.

        Returns:
            current_state (np.ndarray): Current state vector.
        """
        return self._current_state

    @current_state.setter
    def current_state(self, state: np.ndarray):
        """
        Set the current state ($x_t$) of the EKF.

        Args:
            state (np.ndarray): State vector to set.
        """
        if not isinstance(state, np.ndarray):
            raise TypeError("State must be a numpy array")
        if state.ndim != 1:
            raise ValueError("State must be a 1D array")
        if state.shape[0] != self._current_state.shape[0]:
            raise ValueError(
                f"State must have the same number of elements as the current state ({self._current_state.shape[0]})"
            )
        self._current_state = state

    @property
    def current_covariance(self) -> np.ndarray:
        """
        Get the current covariance ($P_t$) of the EKF.

        Returns:
            current_covariance (np.ndarray): Current covariance matrix.
        """
        return self._current_covariance

    @current_covariance.setter
    def current_covariance(self, covariance: np.ndarray):
        """
        Set the current covariance ($P_t$) of the EKF.

        Args:
            covariance (np.ndarray): Covariance matrix to set.
        """
        if not isinstance(covariance, np.ndarray):
            raise TypeError("Covariance must be a numpy array")
        if covariance.ndim != 2:
            raise ValueError("Covariance must be a 2D matrix")
        if covariance.shape[0] != self._current_state.shape[0]:
            raise ValueError(
                f"Covariance must have the same number of rows as the current state ({self._current_state.shape[0]})"
            )
        self._current_covariance = covariance

    @property
    def state_dim(self) -> int:
        """
        Get the dimension of the state vector.

        Returns:
            state_dim (int): Dimension of the state vector.
        """
        return self._state_dim

    @property
    def H_position(self) -> np.ndarray:
        """
        Get the measurement model matrix for cartesian position.

        Returns:
            H_position (np.ndarray): Measurement model matrix for cartesian position.
        """
        return self._H_position

    @property
    def R_position(self) -> np.ndarray:
        """
        Get the measurement noise covariance for cartesian position.

        Returns:
            R_position (np.ndarray): Measurement noise covariance for cartesian position.
        """
        return self._R_position

    @property
    def H_depth(self) -> np.ndarray:
        """
        Get the measurement model matrix for depth.

        Returns:
            H_depth (np.ndarray): Measurement model matrix for depth.
        """
        return self._H_depth

    @property
    def R_depth(self) -> np.ndarray:
        """
        Get the measurement noise covariance for depth.

        Returns:
            R_depth (np.ndarray): Measurement noise covariance for depth.
        """
        return self._R_depth

    @property
    def H_ahrs(self) -> np.ndarray:
        """
        Get the measurement model matrix for AHRS.

        Returns:
            H_ahrs (np.ndarray): Measurement model matrix for AHRS.
        """
        return self._H_ahrs

    @property
    def R_ahrs(self) -> np.ndarray:
        """
        Get the measurement noise covariance for AHRS.

        Returns:
            R_ahrs (np.ndarray): Measurement noise covariance for AHRS.
        """
        return self._R_ahrs

    @property
    def H_vel(self) -> np.ndarray:
        """
        Get the measurement model matrix for linear velocity.

        Returns:
            H_vel (np.ndarray): Measurement model matrix for linear velocity.
        """
        return self._H_vel

    @property
    def R_vel(self) -> np.ndarray:
        """
        Get the measurement noise covariance for linear velocity.

        Returns:
            R_vel (np.ndarray): Measurement noise covariance for linear velocity.
        """
        return self._R_vel

    @property
    def H_bottom_height(self) -> np.ndarray:
        """
        Get the measurement model matrix for bottom height.

        Returns:
            H_bottom_height (np.ndarray): Measurement model matrix for bottom height.
        """
        return self._H_bottom_height

    @property
    def R_bottom_height(self) -> np.ndarray:
        """
        Get the measurement noise covariance for bottom height.

        Returns:
            R_bottom_height (np.ndarray): Measurement noise covariance for bottom height.
        """
        return self._R_bottom_height

    def initialize_state(
        self,
        position: Union[List[Union[int, float]], np.ndarray],
        quaternion: Union[List[Union[int, float]], np.ndarray],
        velocity: Union[List[Union[int, float]], np.ndarray],
        angular_velocity: Union[List[Union[int, float]], np.ndarray],
        bottom_height: Union[float, int] = 0.0,
    ) -> None:
        """
        Initialize the state of the EKF.

        Args:
            position (Union[List[Union[int, float]], np.ndarray]): Initial position of the vehicle.
            quaternion (Union[List[Union[int, float]], np.ndarray]): Initial quaternion of the vehicle. Order: (x, y, z, w).
            velocity (Union[List[Union[int, float]], np.ndarray]): Initial velocity of the vehicle.
            angular_velocity (Union[List[Union[int, float]], np.ndarray]): Initial angular velocity of the vehicle.
            bottom_height (Union[float, int]): Initial bottom height of the vehicle. Default is 0.0.
        """
        # Convert to numpy array
        if isinstance(position, list):
            position = np.array(position)
        if isinstance(quaternion, list):
            quaternion = np.array(quaternion)
        if isinstance(velocity, list):
            velocity = np.array(velocity)
        if isinstance(angular_velocity, list):
            angular_velocity = np.array(angular_velocity)

        # Check inputs type
        if not isinstance(position, np.ndarray):
            raise TypeError("Position must be a numpy array")
        position = position.squeeze()
        if position.ndim != 1:
            raise ValueError("Position must be a 1D array")
        if position.shape[0] != 3:
            raise ValueError("Position must have 3 elements")
        if not isinstance(quaternion, np.ndarray):
            raise TypeError("Quaternion must be a numpy array")
        quaternion = quaternion.squeeze()
        if quaternion.ndim != 1:
            raise ValueError("Quaternion must be a 1D array")
        if quaternion.shape[0] != 4:
            raise ValueError("Quaternion must have 4 elements")
        if np.abs(norm(quaternion) - 1.0) > 1e-6:
            raise ValueError("Quaternion must be a unit quaternion")
        if not isinstance(velocity, np.ndarray):
            raise TypeError("Velocity must be a numpy array")
        velocity = velocity.squeeze()
        if velocity.ndim != 1:
            raise ValueError("Velocity must be a 1D array")
        if velocity.shape[0] != 3:
            raise ValueError("Velocity must have 3 elements")
        if not isinstance(angular_velocity, np.ndarray):
            raise TypeError("Angular velocity must be a numpy array")
        angular_velocity = angular_velocity.squeeze()
        if angular_velocity.ndim != 1:
            raise ValueError("Angular velocity must be a 1D array")
        if angular_velocity.shape[0] != 3:
            raise ValueError("Angular velocity must have 3 elements")
        if not isinstance(bottom_height, (int, float)):
            raise TypeError("Bottom height must be a float or an int")

        current_state = np.concatenate(
            [position, quaternion, velocity, angular_velocity]
        )
        if self._state_dim == 14:
            current_state = np.concatenate([current_state, np.array([bottom_height])])
        self._current_state = current_state

    def predict(self, dt: float, omega_body: np.ndarray) -> None:
        """
        Predict the next state of the EKF.

        Args:
            dt (float): Time step.
            omega_body (np.ndarray): Angular velocity in body frame.
        """
        # State transition
        current_state = np.empty(self._state_dim)

        # Position (p <- p + v * dt)
        current_state[:3] = self._current_state[:3] + self._current_state[7:10] * dt

        # Quaternion (q <- q * q{omega_body*dt})
        axis, theta = axis_ang3(omega_body)
        q_delta = np.array(
            [
                np.sin(dt * theta / 2) * axis[0],
                np.sin(dt * theta / 2) * axis[1],
                np.sin(dt * theta / 2) * axis[2],
                np.cos(dt * theta / 2),
            ]
        )
        current_state[3:7] = (
            left_quat_product_matrix(self._current_state[3:7]) @ q_delta
        )
        current_state[3:7] /= norm(current_state[3:7])
        if current_state[6] < 0:
            current_state[3:7] *= -1

        # Linear velocity (v <- v)
        current_state[7:10] = self._current_state[7:10]
        # Angular rates (w <- omega_body)
        current_state[10:13] = omega_body
        # Bottom height (bh <- bh)
        if self._state_dim == 14:
            current_state[13] = self._current_state[13]

        # Update state
        self._current_state = current_state

        # Process noise covariance and state transition jacobian
        Q = self._process_noise_covariance(dt)
        J = self._state_transition_jacobian(dt, omega_body)

        # Predict covariance
        self._current_covariance = J @ self._current_covariance @ J.T + Q

    def correction_position(
        self,
        timestamp: float,
        x: Union[float, int],
        y: Union[float, int],
        scaling_strength: Union[float, int] = 1.0,
        threshold: float = 0.99,
    ) -> Tuple[float, bool]:
        """
        Correct the state of the EKF using position measurements.

        Args:
            timestamp (float): Timestamp of the measurement in seconds.
            x (Union[float, int]): X position measurement.
            y (Union[float, int]): Y position measurement.
            scaling_strength (Union[float, int]): Scaling strength for the adaptive measurement noise covariance.
                scale_factor =  np.exp(scaling_strength * (d_squared / threshold - 1.0))
            threshold (float): Threshold for the adaptive measurement noise covariance indicating the confidence level.
                The default value is 0.99, which corresponds to a 99% confidence level. This ensures that measurements
                falling within the 99% confidence region are trusted, while outliers are adaptively scaled.

        Returns:
            d_squared (float): Mahalanobis distance squared.
            success (bool): True if the correction was used, False if the correction was scaled.

        Raises:
            TypeError: If timestamp, x, y, scaling_strength or threshold are not of the expected type.
            ValueError: If threshold is not between 0.0 and 1.0.
        """
        # Check typing
        if not isinstance(timestamp, float):
            raise TypeError("Timestamp must be a float")
        if not isinstance(x, (float, int)):
            raise TypeError("X position must be a float or an int")
        if not isinstance(y, (float, int)):
            raise TypeError("Y position must be a float or an int")
        if not isinstance(scaling_strength, (float, int)):
            raise TypeError("Scaling strength must be a float or an int")
        if not isinstance(threshold, (float, int)):
            raise TypeError("Threshold must be a float or an int")
        if threshold <= 0.0 or threshold >= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")

        # Delta time computation update
        if self._position_last_timestamp == 0.0:
            self._position_last_timestamp = timestamp
        else:
            dt = timestamp - self._position_last_timestamp
            self._position_dt.append(dt)
            self._position_last_timestamp = timestamp

        # Measurement (z, shape=(2, 1))
        z = np.array([[x], [y]])

        # H matrix
        H = self._H_position

        # Innovation or residual (y, shape=(2, 1))
        y = z - H @ np.vstack(self._current_state)
        if norm(y) > 100.0:
            warn("Position correction: large innovation (> 100 m), skipping correction")
            return np.nan, True

        # Innovation covariance
        R = self._R_position
        S = H @ self._current_covariance @ H.T + R
        S_inv = np.linalg.inv(S)

        # Mahalanobis distance
        d_squared = (y.T @ S_inv @ y).item()

        # Adaptive R scaling
        threshold_chi2 = chi2.ppf(threshold, df=2)
        scaled = False

        if d_squared > threshold_chi2:
            exponent = scaling_strength * ((d_squared / threshold_chi2) - 1.0)
            exponent = np.clip(exponent, -20, 20)
            scale_factor = np.exp(exponent)
            R_scaled = R * scale_factor
            S = H @ self._current_covariance @ H.T + R_scaled
            S_inv = np.linalg.inv(S)
            scaled = True

        # Kalman gain (K, shape=(n, 2))
        K = self._current_covariance @ H.T @ S_inv

        # Update state estimate (x, shape=(n, 2))
        self._current_state = np.squeeze(np.vstack(self._current_state) + K @ y)

        # Update covariance estimate (P, shape=(n, n))
        self._current_covariance = (
            np.eye(self._state_dim, dtype=np.float64) - K @ H
        ) @ self._current_covariance

        # Normalize quaternion and force it to have positive scalar part
        self._current_state[3:7] /= norm(self._current_state[3:7])
        if self._current_state[6] < 0:
            self._current_state[3:7] *= -1

        return d_squared, scaled

    def correction_depth(
        self,
        timestamp: float,
        z: Union[float, int],
        scaling_strength: Union[float, int] = 1.0,
        threshold: float = 0.99,
    ) -> Tuple[float, bool]:
        """
        Correct the state of the EKF using depth measurements.

        Args:
            timestamp (float): Timestamp of the measurement in seconds.
            z (Union[float, int]): Depth measurement.
            scaling_strength (Union[float, int]): Scaling strength for the adaptive measurement noise covariance.
                scale_factor (Union[float, int]) = np.exp(scaling_strength * (d_squared / threshold - 1.0))
            threshold (float): Threshold for the adaptive measurement noise covariance indicating the confidence level.
                The default value is 0.99, which corresponds to a 99% confidence level.

        Returns:
            d_squared (float): Mahalanobis distance squared.
            success (bool): True if the correction was used, False if the correction was scaled.

        Raises:
            TypeError: If timestamp, z, scaling_strength or threshold are not of the expected type.
            ValueError: If threshold is not between 0.0 and 1.0.
        """
        # Delta time computation update
        if self._depth_last_timestamp == 0.0:
            self._depth_last_timestamp = timestamp
        else:
            dt = timestamp - self._depth_last_timestamp
            self._depth_dt.append(dt)
            self._depth_last_timestamp = timestamp

        # Measurement (z, shape=(1, 1))
        z = np.array([[z]])

        # H matrix
        H = self._H_depth

        # Innovation or residual (y, shape=(1, 1))
        y = z - H @ np.vstack(self._current_state)

        # Innovation covariance
        S = H @ self._current_covariance @ H.T + self._R_depth
        S_inv = np.linalg.inv(S)

        # Mahalanobis distance
        d_squared = (y.T @ S_inv @ y).item()

        # Adaptive R scaling
        threshold_chi2 = chi2.ppf(threshold, df=1)
        scaled = False

        if d_squared > threshold_chi2:
            exponent = scaling_strength * ((d_squared / threshold_chi2) - 1.0)
            exponent = np.clip(exponent, -20, 20)
            scale_factor = np.exp(exponent)
            R_scaled = self._R_depth.copy() * scale_factor
            S = H @ self._current_covariance @ H.T + R_scaled
            S_inv = np.linalg.inv(S)
            scaled = True

        # Kalman gain (K, shape=(n, 1))
        K = self._current_covariance @ H.T @ S_inv

        # Update state estimate (x, shape=(n, 1))
        self._current_state = np.squeeze(np.vstack(self._current_state) + K @ y)

        # Update covariance estimate (P, shape=(n, n))
        self._current_covariance = (
            np.eye(self._state_dim, dtype=np.float64) - K @ H
        ) @ self._current_covariance

        # Normalize quaternion and force it to have positive scalar part
        self._current_state[3:7] /= norm(self._current_state[3:7])
        if self._current_state[6] < 0:
            self._current_state[3:7] *= -1

        return d_squared, scaled

    def correction_ahrs(
        self,
        timestamp: float,
        quaternion: Union[List[Union[int, float]], np.ndarray],
        angular_velocity: Union[List[Union[int, float]], np.ndarray],
    ) -> None:
        """
        Correct the state of the EKF using orientation and angular velocity measurements.

        Args:
            timestamp (float): Timestamp of the measurement in seconds.
            quaternion (Union[List[Union[int, float]], np.ndarray]): Quaternion measurement. Order: (x, y, z, w).
            angular_velocity (Union[List[Union[int, float]], np.ndarray]): Angular velocity measurement.
        """
        # Convert to numpy array
        if isinstance(quaternion, list):
            quaternion = np.array(quaternion)
        if isinstance(angular_velocity, list):
            angular_velocity = np.array(angular_velocity)

        # Check inputs type
        if not isinstance(timestamp, float):
            raise TypeError("Timestamp must be a float")
        if not isinstance(quaternion, np.ndarray):
            raise TypeError("Quaternion must be a numpy array")
        quaternion = quaternion.squeeze()
        if quaternion.ndim != 1:
            raise ValueError("Quaternion must be a 1D array")
        if quaternion.shape[0] != 4:
            raise ValueError("Quaternion must have 4 elements")
        if np.abs(norm(quaternion) - 1.0) > 1e-6:
            raise ValueError("Quaternion must be a unit quaternion")
        if not isinstance(angular_velocity, np.ndarray):
            raise TypeError("Angular velocity must be a numpy array")
        angular_velocity = angular_velocity.squeeze()
        if angular_velocity.ndim != 1:
            raise ValueError("Angular velocity must be a 1D array")
        if angular_velocity.shape[0] != 3:
            raise ValueError("Angular velocity must have 3 elements")

        # Delta time computation update
        if self._imu_last_timestamp == 0.0:
            self._imu_last_timestamp = timestamp
        else:
            dt = timestamp - self._imu_last_timestamp
            self._imu_dt.append(dt)
            self._imu_last_timestamp = timestamp

        # Measurement (z, shape=(4, 1))
        z = np.vstack(np.concatenate([quaternion, angular_velocity]))

        # Innovation or residual (y, shape=(7, 1))
        y = z - self._H_ahrs @ np.vstack(self._current_state)

        # Measurement noise covariance (R, shape=(7, 7))
        R = self._R_ahrs

        # Measurement prediction covariance (S, shape=(7, 7))
        S = self._H_ahrs @ self._current_covariance @ self._H_ahrs.T + R

        # Kalman gain (K, shape=(n, 7))
        # We will use np.linalg solve instead of np.linalg.inv, as it is faster and more stable
        K = np.linalg.solve(S, (self._current_covariance @ self._H_ahrs.T).T).T

        # Update state estimate (x, shape=(n, 1))
        self._current_state = np.squeeze(np.vstack(self._current_state) + K @ y)

        # Normalize quaternion and force it to have positive scalar part
        self._current_state[3:7] /= norm(self._current_state[3:7])
        if self._current_state[6] < 0:
            self._current_state[3:7] *= -1

        # Update covariance estimate (P, shape=(n, n))
        self._current_covariance = (
            np.eye(self._state_dim, dtype=np.float64) - K @ self._H_ahrs
        ) @ self._current_covariance

    def correction_velocity(
        self,
        timestamp: float,
        velocity: Union[List[Union[int, float]], np.ndarray],
        body_frame: bool = True,
        scaling_strength: Union[float, int] = 1.0,
        threshold: float = 0.99,
    ) -> Tuple[float, bool]:
        """
        Correct the state of the EKF using velocity measurements.

        Args:
            timestamp (float): Timestamp of the measurement in seconds.
            velocity (Union[List[Union[int, float]], np.ndarray]): Velocity measurement. Order: (vx, vy, vz).
            body_frame (bool): If True, the velocity is in body frame, otherwise in world frame.
            scaling_strength (Union[float, int]): Scaling strength for the adaptive measurement noise covariance.
                scale_factor = np.exp(scaling_strength * (d_squared / threshold - 1.0))
            threshold (float): Threshold for the adaptive measurement noise covariance indicating the confidence level.
                The default value is 0.99, which corresponds to a 99% confidence level.

        Returns:
            d_squared (float): Mahalanobis distance squared.
            success (bool): True if the correction was used, False if the correction was scaled.

        Raises:
            TypeError: If timestamp, velocity, body_frame, scaling_strength or threshold are not of the expected type.
            ValueError: If threshold is not between 0.0 and 1.0.
        """
        # Convert to numpy array
        if isinstance(velocity, list):
            velocity = np.array(velocity)

        # Check inputs type
        if not isinstance(timestamp, float):
            raise TypeError("Timestamp must be a float")
        if not isinstance(velocity, np.ndarray):
            raise TypeError("Velocity must be a numpy array")
        velocity = velocity.squeeze()
        if velocity.ndim != 1:
            raise ValueError("Velocity must be a 1D array")
        if velocity.shape[0] != 3:
            raise ValueError("Velocity must have 3 elements")
        if not isinstance(body_frame, bool):
            raise TypeError("body_frame must be a boolean")
        if not isinstance(scaling_strength, (float, int)):
            raise TypeError("Scaling strength must be a float or an int")
        if not isinstance(threshold, (float, int)):
            raise TypeError("Threshold must be a float or an int")
        if threshold <= 0.0 or threshold >= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")

        # Delta time computation update
        if self._dvl_last_timestamp == 0.0:
            self._dvl_last_timestamp = timestamp
        else:
            dt = timestamp - self._dvl_last_timestamp
            self._dvl_dt.append(dt)
            self._dvl_last_timestamp = timestamp

        # Extract velocity from current state
        v_world = np.vstack(self._current_state[7:10])

        if body_frame:
            # Rotate into body frame to define the predicted DVL measurement
            q = self._current_state[3:7]
            rot_v_w = quat2rot(q).T
            z_pred = rot_v_w @ v_world

            # Innovation
            y = np.vstack(velocity) - z_pred

            # H matrix
            H = np.zeros((3, self._state_dim))
            H[:, 7:10] = rot_v_w
        else:
            # Innovation
            y = np.vstack(velocity) - v_world

            # H matrix
            H = np.zeros((3, self._state_dim))
            H[:, 7:10] = np.eye(3, dtype=np.float64)

        # Innovation covariance
        S = H @ self._current_covariance @ H.T + self._R_vel
        S_inv = np.linalg.inv(S)

        # Mahalanobis distance
        d_squared = (y.T @ S_inv @ y).item()
        self._velocity_d_squared_acummulted += d_squared
        self._velocity_d_squared_count += 1
        self._velocity_q_tuner.update(
            self._velocity_d_squared_acummulted / self._velocity_d_squared_count
        )

        # Adaptive R scaling
        threshold_chi2 = chi2.ppf(threshold, df=3)
        scaled = False

        if d_squared > threshold_chi2:
            exponent = scaling_strength * ((d_squared / threshold_chi2) - 1.0)
            exponent = np.clip(exponent, -20, 20)
            scale_factor = np.exp(exponent)
            R_scaled = self._R_vel.copy() * scale_factor
            S = H @ self._current_covariance @ H.T + R_scaled
            S_inv = np.linalg.inv(S)
            scaled = True

        # Kalman gain (K, shape=(n, 3) or (n, 4))
        K = self._current_covariance @ H.T @ S_inv

        # Update state estimate (x, shape=(n, 1) or (n, 4))
        self._current_state = np.squeeze(np.vstack(self._current_state) + K @ y)

        # Update covariance estimate (P, shape=(n, n))
        self._current_covariance = (
            np.eye(self._state_dim, dtype=np.float64) - K @ H
        ) @ self._current_covariance

        # Normalize quaternion and force it to have positive scalar part
        self._current_state[3:7] /= norm(self._current_state[3:7])
        if self._current_state[6] < 0:
            self._current_state[3:7] *= -1

        return d_squared, scaled

    def correction_bottom_height(
        self,
        bottom_height: Union[float, int],
        scaling_strength: Union[float, int] = 1.0,
        threshold: float = 0.99,
    ) -> Tuple[float, bool]:
        """
        Correct the state of the EKF using bottom height measurements.

        Args:
            bottom_height (Union[float, int]): Bottom height measurement.
            scaling_strength (Union[float, int]): Scaling strength for the adaptive measurement noise covariance.
                scale_factor = np.exp(scaling_strength * (d_squared / threshold - 1.0))
            threshold (float): Threshold for the adaptive measurement noise covariance indicating the confidence level.
                The default value is 0.99, which corresponds to a 99% confidence level.

        Returns:
            d_squared (float): Mahalanobis distance squared.
            success (bool): True if the correction was used, False if the correction was scaled.

        Raises:
            TypeError: If bottom_height, scaling_strength or threshold are not of the expected type.
            ValueError: If threshold is not between 0.0 and 1.0.
        """
        # Check typing
        if not isinstance(bottom_height, (float, int)):
            raise TypeError("Bottom height must be a float or an int")
        if not isinstance(scaling_strength, (float, int)):
            raise TypeError("Scaling strength must be a float or an int")
        if not isinstance(threshold, (float, int)):
            raise TypeError("Threshold must be a float or an int")
        if threshold <= 0.0 or threshold >= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")

        if self._state_dim != 14:
            return np.nan, False

        # Measurement (z, shape=(1, 1))
        z = np.array([[bottom_height]])

        # H matrix
        H = self._H_bottom_height

        # Innovation or residual (y, shape=(1, 1))
        y = z - H @ np.vstack(self._current_state)

        # Innovation covariance
        S = H @ self._current_covariance @ H.T + self._R_bottom_height
        S_inv = np.linalg.inv(S)

        # Mahalanobis distance
        d_squared = (y.T @ S_inv @ y).item()

        # Adaptive R scaling
        threshold_chi2 = chi2.ppf(threshold, df=1)
        scaled = False

        if d_squared > threshold_chi2:
            exponent = scaling_strength * ((d_squared / threshold_chi2) - 1.0)
            exponent = np.clip(exponent, -20, 20)
            scale_factor = np.exp(exponent)
            R_scaled = self._R_bottom_height.copy() * scale_factor
            S = H @ self._current_covariance @ H.T + R_scaled
            S_inv = np.linalg.inv(S)
            scaled = True

        # Kalman gain (K, shape=(n, 1))
        K = self._current_covariance @ H.T @ S_inv

        # Update state estimate (x, shape=(n, 1) or (n, 4))
        self._current_state = np.squeeze(np.vstack(self._current_state) + K @ y)

        # Update covariance estimate (P, shape=(n, n))
        self._current_covariance = (
            np.eye(self._state_dim, dtype=np.float64) - K @ H
        ) @ self._current_covariance

        # Normalize quaternion and force it to have positive scalar part
        self._current_state[3:7] /= norm(self._current_state[3:7])
        if self._current_state[6] < 0:
            self._current_state[3:7] *= -1

        return d_squared, scaled

    def _state_transition_jacobian(
        self, dt: float, omega_body: Union[List[Union[int, float]], np.ndarray]
    ) -> np.ndarray:
        """
        State transition jacobian for the EKF.

        Args:
            dt (float): Time step.
            omega_body (Union[List[Union[int, float]], np.ndarray]): Angular velocity in body frame.

        Returns:
            jacobian (np.ndarray): State transition jacobian.
        """
        # State transition model for the state: [x, y, z, qx, qy, qz, qw, vx, vy, vz, wx, wy, wz, bh (optional)]
        J = np.zeros((self.state_dim, self.state_dim), dtype=np.float64)
        # Position state transition model (p(t + dt) = p(t) + v(t) * dt)
        J[:3, :3] = np.eye(3, dtype=np.float64)
        J[:3, 7:10] = dt * np.eye(3, dtype=np.float64)

        # Quaternion state transition model (q(t + dt) = R(q_delta) * q(t))
        axis, theta = axis_ang3(omega_body)
        q_delta = np.array(
            [
                np.sin(dt * theta / 2) * axis[0],
                np.sin(dt * theta / 2) * axis[1],
                np.sin(dt * theta / 2) * axis[2],
                np.cos(dt * theta / 2),
            ]
        )
        J[3:7, 3:7] = right_quat_product_matrix(q_delta)

        # Linear velocity state transition model (we assume constant velocity model, v(t + dt) = v(t))
        J[7:10, 7:10] = np.eye(3, dtype=np.float64)

        # Bottom height state transition model (if available) (bh(t + dt) = bh(t))
        if self.state_dim == 14:
            J[-1, -1] = 1.0

        return J

    def _process_noise_covariance(self, dt: float) -> np.ndarray:
        """
        Process noise covariance for the EKF.

        Args:
            dt (float): Time step.

        Returns:
            process_noise_covariance (np.ndarray): Process noise covariance matrix.
        """
        Q = np.zeros((self.state_dim, self.state_dim), dtype=np.float64)

        # Position - Velocity
        if self._velocity_d_squared_count > 0:
            new_alpha = self._velocity_q_tuner.alpha
        else:
            new_alpha = 1.0

        Q[:3, :3] = new_alpha * (dt**3 / 3) * self._q0_velocity  # Position
        Q[:3, 7:10] = (
            new_alpha * (dt**2 / 2) * self._q0_velocity
        )  # Position-Velocity cross
        Q[7:10, :3] = (
            new_alpha * (dt**2 / 2) * self._q0_velocity
        )  # Velocity-Position cross
        Q[7:10, 7:10] = (new_alpha * self._q0_velocity) * dt  # Velocity

        # Bottom height noise (if applicable)
        if self._state_dim == 14:
            Q[-1, -1] = new_alpha * dt * self._q0_velocity[2, 2]

        # Quaternion noise (due to angular noise)
        sigma_q = 1e-5  # very small; unit quaternions must stay normalized
        Q[3:7, 3:7] = (sigma_q * dt) * np.eye(4, dtype=np.float64)

        # Angular rate noise (due to gyro process noise or maneuvering)
        sigma_w = 1e-5  # rad^2/s^2
        Q[10:13, 10:13] = (sigma_w * dt) * np.eye(3, dtype=np.float64)

        return Q

    def _safe_nanmean(self, array: np.ndarray) -> float:
        """
        Compute the mean of an array, ignoring NaN values.
        If all values are NaN, return 1.0

        Args:
            array (np.ndarray): Input array.
        Returns:
            mean (float): Mean of the array, ignoring NaN values.
        """
        if np.all(np.isnan(array)):
            return 1.0
        else:
            return np.nanmean(array)


class _QTuner:
    """
    Class to tune the process noise covariance based on the observed Mahalanobis distance.
    """

    def __init__(
        self,
        initial_alpha=1.0,
        target_d2_mean=3.0,
        learning_rate=0.1,
        min_alpha=0.1,
        max_alpha=10.0,
    ) -> None:
        """
        Initialize the QTuner.

        Args:
            initial_alpha (float): Initial value for the process noise covariance.
            target_d2_mean (float): Target mean Mahalanobis distance.
            learning_rate (float): Learning rate for the tuning.
            min_alpha (float): Minimum value for the process noise covariance.
            max_alpha (float): Maximum value for the process noise covariance.
        """
        self.alpha = initial_alpha
        self.target_d2_mean = target_d2_mean
        self.learning_rate = learning_rate
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha

    def update(self, observed_d2_mean: float) -> None:
        """
        Update the process noise covariance based on the observed Mahalanobis distance.

        Args:
            observed_d2_mean (float): Observed mean Mahalanobis distance.
        """
        error = observed_d2_mean - self.target_d2_mean
        self.alpha *= 1.0 + self.learning_rate * error
        self.alpha = np.clip(self.alpha, self.min_alpha, self.max_alpha)
