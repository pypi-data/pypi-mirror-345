"""
This module contains functions to calibrate magnetometers using various methods
based on research papers and algorithms.

Functions:
    cal_mag_ellipsoid_fit: Standard ellipsoid fit method.
    cal_mag_ellipsoid_fit_fang: Ellipsoid fit method by Fang et al. [1]
    cal_mag_magfactor3: Factor graph based approach to full-magnetometer calibration.
    cal_mag_twostep_hi: TWOSTEP method for hard-iron estimation [2].
    cal_mag_twostep_hsi: TWOSTEP method for hard-iron and soft-iron estimation [2].
    cal_mag_sar_ls: The linear least squares for sensor bias calibration [3].
    cal_mag_sar_kf: The Kalman filter for sensor bias calibration [3].
    cal_mag_sar_aid: The adaptive identification for sensor bias calibration [3].
    cal_mag_sphere_fit: Standard sphere fit method.
    cal_mag_magyc_ls: MAGYC-LS method [4].
    cal_mag_magyc_nls: MAGYC-NLS method [4].
    cal_mag_magyc_bfg: MAGYC-BFG method [4].
    cal_mag_magyc_ifg: MAGYC-IFG method [4].

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org

References:
    [1] Section (III) in J. Fang, H. Sun, J. Cao, X. Zhang, and Y. Tao, “A novel
        calibration method of magnetic compass based on ellipsoid fitting,” IEEE
        Transactions on Instrumentation and Measurement, vol. 60, no. 6, pp.
        2053--2061, 2011.

    [2] Alonso, R. Shuster, M.D. (2002a). TWOSTEP: A fast, robust algorithm for
        attitude-independent magnetometer-bias determination. Journal of the
        Astronautical Sciences, 50(4):433-452.

    [3] Troni, G. and Whitcomb, L. L. (2019). Field sensor bias calibration
        with angular-rate sensors: Theory and experimental evaluation with
        application to magnetometer calibration. IEEE/ASME Transactions
        on Mechatronics, 24(4):1698--1710.

    [4] Rodríguez-Martínez, S., & Troni, G. (2025). Full Magnetometer and
        Gyroscope Bias Estimation Using Angular Rates: Theory and Experimental
        Evaluation of a Factor Graph-Based Approach. IEEE Journal of Oceanic
        Engineering.
"""
from __future__ import annotations

import warnings
from datetime import datetime
from functools import partial
from typing import Dict, List, Optional, Tuple, Union

import jax.numpy as npj
import numpy as np
from jax import jacfwd, jit
from jax.numpy import exp as expj
from numpy import exp as exp
from scipy.linalg import expm
from scipy.optimize import least_squares
from scipy.signal import savgol_filter

from navlib.math import rph2rot, vec_to_so3
from navlib.nav import ahrs_raw_hdg

# Manage gtsam incompatibility with python >= 3.12
try:
    import gtsam
    from gtsam.symbol_shorthand import B, S, W
except ImportError:
    warnings.warn("gtsam is not available for python 3.12", ImportWarning)
    warnings.warn(
        "gtsam-based magnetometer calibration methods will not be available",
        ImportWarning,
    )


def cal_mag_ellipsoid_fit(
    magnetic_field: Union[np.ndarray, list]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    The ellipsoid fit method is based on the fact that the error model of a magnetic
    compass is an ellipsoid, and a constraint least-squares method is adopted to
    estimate the parameters of an ellipsoid by rotating the magnetic compass in
    various random orientations.

    For further details about the implementation, refer to Aleksandr Bazhin [Github
    repository](https://github.com/aleksandrbazhin/ellipsoid_fit_python), where he
    ports to python [matlab's ellipsoid fit].(http://www.mathworks.com/matlabcentral/fileexchange/24693-ellipsoid-fit)

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.

    Returns:
        hard_iron (numpy.ndarray): Hard iron bias as a (3,) numpy array.
        soft_iron (numpy.ndarray): Soft iron matrix as a (3, 3) numpy array.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements.

    Raises:
        TypeError: If the input is not a numpy array or a list.
        ValueError: If the input is not a 3xN or Nx3 numpy array.
    """
    # Check if the input is a list and convert it to a numpy array
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)

    # Check if the input is a numpy array
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The input must be a numpy array or a list.")

    # Check if the input is a 3xN or Nx3 numpy array
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The input must be a 3xN or Nx3 numpy array.")

    # Force the array to be a Nx3 numpy array
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T

    # Compute magnetic field calibration
    x, y, z = magnetic_field[:, 0], magnetic_field[:, 1], magnetic_field[:, 2]

    d_matrix = np.array(
        [
            x * x + y * y - 2 * z * z,
            x * x + z * z - 2 * y * y,
            2 * x * y,
            2 * x * z,
            2 * y * z,
            2 * x,
            2 * y,
            2 * z,
            1 - 0 * x,
        ]
    )
    d2 = np.array(x * x + y * y + z * z).T
    u = np.linalg.solve(d_matrix.dot(d_matrix.T), d_matrix.dot(d2))
    a = np.array([u[0] + 1 * u[1] - 1])
    b = np.array([u[0] - 2 * u[1] - 1])
    c = np.array([u[1] - 2 * u[0] - 1])
    v = np.concatenate([a, b, c, u[2:]], axis=0).flatten()
    a_matrix = np.array(
        [
            [v[0], v[3], v[4], v[6]],
            [v[3], v[1], v[5], v[7]],
            [v[4], v[5], v[2], v[8]],
            [v[6], v[7], v[8], v[9]],
        ]
    )

    center = np.linalg.solve(-a_matrix[:3, :3], v[6:9])

    translation_matrix = np.eye(4)
    translation_matrix[3, :3] = center.T

    r_matrix = translation_matrix.dot(a_matrix).dot(translation_matrix.T)

    evals, evecs = np.linalg.eig(r_matrix[:3, :3] / -r_matrix[3, 3])
    evecs = evecs.T

    radii = np.sqrt(1.0 / np.abs(evals))
    radii *= np.sign(evals)

    a, b, c = radii
    r = (a * b * c) ** (1.0 / 3.0)
    D = np.array([[r / a, 0.0, 0.0], [0.0, r / b, 0.0], [0.0, 0.0, r / c]])
    transformation = evecs.dot(D).dot(evecs.T)

    hard_iron = center.reshape(3, 1)
    soft_iron = transformation.reshape(3, 3)

    # Calibrate magnetic field
    calibrated_magnetic_field = (
        np.linalg.inv(soft_iron)
        @ (magnetic_field.reshape(3, -1) - hard_iron.reshape(3, 1))
    ).T

    return hard_iron.flatten(), soft_iron, calibrated_magnetic_field


def cal_mag_ellipsoid_fit_fang(
    magnetic_field: Union[np.ndarray, list]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    The ellipsoid fit method is based on the fact that the error model of a magnetic
    compass is an ellipsoid, and a constraint least-squares method is adopted to
    estimate the parameters of an ellipsoid by rotating the magnetic compass in
    various random orientations.

    For further details about the implementation, refer to section (III) in J. Fang,
    H. Sun, J. Cao, X. Zhang, and Y. Tao, “A novel calibration method of magnetic
    compass based on ellipsoid fitting,” IEEE Transactions on Instrumentation
    and Measurement, vol. 60, no. 6, pp. 2053--2061, 2011.

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.

    Returns:
        hard_iron (numpy.ndarray): Hard iron bias as a (3,) numpy array.
        soft_iron (numpy.ndarray): Soft iron matrix as a (3, 3) numpy array.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements.

    Raises:
        TypeError: If the input is not a numpy array or a list.
        ValueError: If the input is not a 3xN or Nx3 numpy array.
        RuntimeWarning: If no positive eigenvalues are found.
    """
    # Check if the input is a list and convert it to a numpy array
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)

    # Check if the input is a numpy array
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The input must be a numpy array or a list.")

    # Check if the input is a 3xN or Nx3 numpy array
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The input must be a 3xN or Nx3 numpy array.")

    # Force the array to be a Nx3 numpy array
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T

    # Compute magnetic field calibration
    # Design matrix (S)
    s = np.concatenate(
        [
            np.square(magnetic_field[:, [0]]),
            magnetic_field[:, [0]] * magnetic_field[:, [1]],
            np.square(magnetic_field[:, [1]]),
            magnetic_field[:, [0]] * magnetic_field[:, [2]],
            magnetic_field[:, [1]] * magnetic_field[:, [2]],
            np.square(magnetic_field[:, [2]]),
            magnetic_field[:, :],
            np.ones((magnetic_field.shape[0], 1)),
        ],
        axis=1,
    )

    # Block Matrices: S_11, S_12, S_22
    sTs = s.T @ s
    s_11, s_12, s_22 = sTs[:3, :3], sTs[:3, 3:], sTs[3:, 3:]

    # Constrain matrix C_11
    c_11 = np.array([[0, 0, 2], [0, -1, 0], [2, 0, 0]])

    # Ellipsoid Parameters Estimation
    eigenvals, eigenvecs = np.linalg.eig(
        np.linalg.inv(c_11) @ (s_11 - s_12 @ np.linalg.inv(s_22) @ s_12.T)
    )

    if np.max(eigenvals) < 0:
        warnings.warn(
            "No positive eigenvalues: max eigenvalue = {:.6f}".format(
                np.max(eigenvals)
            ),
            RuntimeWarning,
        )

    a_1 = -eigenvecs[:, [np.argmax(eigenvals)]]
    a_2 = -np.linalg.inv(s_22) @ s_12.T @ a_1
    a = np.concatenate([a_1, a_2], axis=0).flatten()

    # Determine A and b
    a_matrix = np.array(
        [
            [a[0], a[1] / 2, a[3] / 2],
            [a[1] / 2, a[2], a[4] / 2],
            [a[3] / 2, a[4] / 2, a[5]],
        ]
    )
    hard_iron = np.linalg.inv(-2 * a_matrix) @ np.vstack(a[6:9])

    # Determine G and M
    u, s, vh = np.linalg.svd(a_matrix)
    g = u @ np.sqrt(np.diag(s)) @ vh
    soft_iron = np.linalg.inv(g)

    # Calibrate magnetic field
    calibrated_magnetic_field = (
        np.linalg.inv(soft_iron)
        @ (magnetic_field.reshape(3, -1) - hard_iron.reshape(3, 1))
    ).T

    return hard_iron.flatten(), soft_iron, calibrated_magnetic_field


def cal_mag_magfactor3(
    magnetic_field: Union[np.ndarray, list],
    rph: Union[np.ndarray, list],
    magnetic_declination: float,
    reference_magnetic_field: Union[np.ndarray, list],
    optimizer: str = "dogleg",
    relative_error_tol: float = 1.00e-12,
    absolute_error_tol: float = 1.00e-12,
    max_iter: int = 1000,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, list]:
    """
    The full-magnetometer calibration least-squares problems can also be modeled
    as a factor graph. This can be implemented using the [GTSAM](https://github.com/borglab/gtsam)
    python wrapper with the magFactor3 factor. This approach allows the user to get the soft-iron
    (SI) as the identity scaled by a constant and the hard-iron (HI) from the
    magnetometer bias.

    This method assumes that the rotation from the body frame with respect to
    the world frame and the local magnetic field are known.

    Args:
        magnetic_field (Union[np.ndarray, list]): Magnetic field raw data
        rph (Union[np.ndarray, list]): Roll, pitch and heading data
        magnetic_declination (float): Magnetic declination in degrees
        reference_magnetic_field (Union[np.ndarray, list]): Reference magnetic field
        optimizer (str): Optimization algorithm to use. Options are "dogleg" or "lm"
            for the Dogleg and Levenberg-Marquardt optimizers respectively.
        relative_error_tol (float): Relative error tolerance for the optimizer. Default is 1.00e-12
        absolute_error_tol (float): Absolute error tolerance for the optimizer. Default is 1.00e-12
        max_iter (int): Maximum number of iterations for the optimizer. Default is 1000

    Returns:
        hard_iron (np.ndarray): Hard-iron offset in as a (3.) numpy array
        soft_iron (np.ndarray): Soft-iron scaling matrix
        corrected_magnetic_field (np.ndarray): Corrected magnetic field data
        optimization_errors (list): List of optimization errors in each iteration

    Raises:
        TypeError: If the magnetic field input is not a numpy array or a list
        TypeError: If the reference magnetic field input is not a numpy array or a list
        TypeError: If the rph input is not a numpy array or a list
        ValueError: If the magnetic field input is not a 3xN or Nx3 numpy array
        ValueError: If the reference magnetic field input is not a 3, numpy array
        ValueError: If the rph input is not a 3xN or Nx3 numpy array
        TypeError: If the magnetic declination is not a float
        ValueError: If the optimizer is not a string or not "dogleg" or "lm"
        TypeError: If the relative error tolerance is not a float
        TypeError: If the absolute error tolerance is not a float
        ValueError: If the maximum number of iterations is not a positive integer
    """
    # Manage gtsam incompatibility with python >= 3.12
    try:
        import gtsam
    except ImportError:
        raise ImportError(
            "GTSAM is only available for Python ≤ 3.11. "
            "If you're on Python ≥ 3.12, please downgrade or install GTSAM manually."
        )

    # Check if the magnetic field input is a list and convert it to a numpy array
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)

    # Check if the reference magnetic field input is a list and convert it to a numpy array
    if isinstance(reference_magnetic_field, list):
        reference_magnetic_field = np.array(reference_magnetic_field).flatten()

    # Check if the rph input is a list and convert it to a numpy array
    if isinstance(rph, list):
        rph = np.array(rph)

    # Check if the magnetic field input is a numpy array
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field input must be a numpy array or a list.")

    # Check if the reference magnetic field input is a numpy array
    if not isinstance(reference_magnetic_field, np.ndarray):
        raise TypeError(
            "The reference magnetic field input must be a numpy array or a list."
        )

    # Check if the rph input is a numpy array
    if not isinstance(rph, np.ndarray):
        raise TypeError("The rph input must be a numpy array or a list.")

    # Check if the magnetic field input is a 3xN or Nx3 numpy array
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field input must be a 3xN or Nx3 numpy array.")

    # Check if the reference magnetic field input is a 3, numpy array
    reference_magnetic_field = reference_magnetic_field.flatten()
    if reference_magnetic_field.shape[0] != 3:
        raise ValueError(
            "The reference magnetic field input must be a 3, or 1x3, or 3x1 numpy array."
        )

    # Check if the rph input is is a 3xN or Nx3 numpy array
    if rph.ndim != 2 or (rph.shape[0] != 3 and rph.shape[1] != 3):
        raise ValueError("The rph input must be a 3xN or Nx3 numpy array.")

    # Force the magnetic field array to be a Nx3 numpy array
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T

    # Force the rph array to be a Nx3 numpy array
    if rph.shape[0] == 3:
        rph = rph.T

    # Check that the magnetic declination is a float
    if not isinstance(magnetic_declination, float):
        raise TypeError("The magnetic declination must be a float.")

    # Check that the optimizer is a string and is either "dogleg" or "lm"
    if not isinstance(optimizer, str) or optimizer not in ["dogleg", "lm"]:
        raise ValueError("The optimizer must be a string and either 'dogleg' or 'lm'.")

    # Check that the relative error tolerance is a float
    if not isinstance(relative_error_tol, float) or relative_error_tol <= 0:
        raise TypeError("The relative error tolerance must be a float.")

    # Check that the absolute error tolerance is a float
    if not isinstance(absolute_error_tol, float) or absolute_error_tol <= 0:
        raise TypeError("The absolute error tolerance must be a float.")

    # Check that the maximum number of iterations is a positive integer
    if not isinstance(max_iter, int) or max_iter <= 0:
        raise ValueError("The maximum number of iterations must be a positive integer.")

    # Compute attitude based on magnetic heading
    magnetic_hdg = ahrs_raw_hdg(magnetic_field, rph) - np.deg2rad(magnetic_declination)
    magnetic_rph = np.concatenate([rph[:, :2], magnetic_hdg.reshape(-1, 1)], axis=1)

    # Compute calibration
    # Smoothing and Mapping Factor Graph
    # 1. Create the non-linear graph
    graph = gtsam.NonlinearFactorGraph()

    # 2. noise model for each factor.
    residual_noise = gtsam.noiseModel.Isotropic.Sigma(3, 0.001)

    # 3. Creates values structure with initial values: S -> Scale, D -> Direction, B -> Bias
    initial = gtsam.Values()
    initial.insert(S(0), 1.0)
    initial.insert(B(0), gtsam.Point3(0, 0, 0))
    keys = [S(0), B(0)]

    # 4. Add factor for each measurement into a single node
    h0 = gtsam.Point3(reference_magnetic_field.flatten())

    for i in range(magnetic_field.shape[0]):
        mi = gtsam.Point3(magnetic_field[i, :])
        bRw = gtsam.Rot3(rph2rot(magnetic_rph[i, :]).T)

        # 5.1 magFactor3
        rf = gtsam.CustomFactor(
            residual_noise,
            keys,
            partial(_cal_mag_magfactor3_residual_factor, mi, h0, bRw),
        )
        graph.add(rf)

    # 5. If not online optimize the full batch
    # 5.1 Create optimizer parameters
    params = (
        gtsam.DoglegParams()
        if optimizer == "dogleg"
        else gtsam.LevenbergMarquardtParams()
    )
    params.setRelativeErrorTol(relative_error_tol)
    params.setAbsoluteErrorTol(absolute_error_tol)
    params.setMaxIterations(max_iter)
    params.setLinearSolverType("MULTIFRONTAL_CHOLESKY")

    # 5.2 Create optimizer
    if optimizer == "dogleg":
        optimizer = gtsam.DoglegOptimizer(graph, initial, params)
    else:
        optimizer = gtsam.LevenbergMarquardtOptimizer(graph, initial, params)

    # 5.3 Optimize
    result, optimization_errors = _cal_mag_magfactor3_gtsam_optimize(optimizer, params)

    # 7. Process Results
    hard_iron = np.vstack(result.atPoint3(B(0)))
    soft_iron = result.atDouble(S(0)) * np.eye(3)

    # Correct the magnetic field
    corrected_magnetic_field = (
        np.linalg.inv(soft_iron) @ (magnetic_field.T - hard_iron.reshape(3, -1))
    ).T

    return hard_iron.flatten(), soft_iron, corrected_magnetic_field, optimization_errors


def _cal_mag_magfactor3_residual_factor(
    magfield: "gtsam.Point3",
    local_magfield: "gtsam.Point3",
    bRw: "gtsam.Rot3",
    this: "gtsam.CustomFactor",
    v: "gtsam.Values",
    H: Optional[List[np.ndarray]],
) -> np.ndarray:
    """
    Unary factor for the magnetometer model:

    $$m_m(t) = \\text{scale} \\cdot m_t(t) + \\text{bias}$$

    Where $m_m(t) \\; \\in \\; \\mathbb{R}^3$ is the measured magnetic field,
    $m_t(t) \\; \\in \\; \\mathbb{R}^3$ is the true magnetic field, $\\text{scale} \\; \\in \\; \\mathbb{R}$
    is the scale factor and $\\text{bias} \\; \\in \\; \\mathbb{R}^3$ is the
    magnetometer bias.

    Args:
        magfield (gtsam.Point3): Magnetic field measurements in G as a (3, 1) gtsam Point3 object.
        local_magfield (gtsam.Point3): Local magnetic field from model in G as a (3, 1) gtsam Point 3 object.
        bRw (gtsam.Rot3): Attitude of the world frame with respect to the body frame as gtsam Rot3 object.
        this (gtsam.CustomFactor): Reference to the current CustomFactor being evaluated.
        v (gtsam.Values): A values structure that maps from keys to values.
        H (List[np.ndarray], optional): List of references to the Jacobian arrays.

    Returns:
        error (np.ndarray): The non-linear norm error with respect to the unitary norm as a gtsam factor.
    """
    key0, key1 = this.keys()[0], this.keys()[1]
    scale, bias = v.atDouble(key0), v.atPoint3(key1)

    # Cost Function
    rotated = gtsam.Point3(bRw.rotate(local_magfield))
    hx = scale * rotated + bias
    error = hx - magfield

    if H is not None:
        H[0] = np.vstack(rotated)
        H[1] = np.eye(3)

    return error


def _cal_mag_magfactor3_gtsam_optimize(
    optimizer: Union["gtsam.LevenbergMarquardtOptimizer", "gtsam.DoglegOptimizer"],
    optimizer_params: Union["gtsam.LevenbergMarquardtParams", "gtsam.DoglegParams"],
) -> Union["gtsam.Values", list]:
    """
    Wrapper for the batch optimization of the non-linear graph with a callback to
    store the optimization error and check the termination conditions.

    Args:
        optimizer (Union[gtsam.LevenbergMarquardtParams, gtsam.DoglegParams]): Optimizer parameters.
        optimizer_params (Union[gtsam.LevenbergMarquardtParams, gtsam.DoglegParams]): Optimizer parameters.

    Returns:
        gtsam.Values: The state value in each node as a gtsam.Values structure.
        optimization_error (list): The optimization error in each iteration.
    """
    optimization_error = []
    error_before = optimizer.error()

    while True:
        # Optimize
        optimizer.iterate()
        error_after = optimizer.error()

        # Store errors
        optimization_error.append(
            [error_before, error_after, error_before - error_after]
        )

        # Check termination condition
        # Condition 1: Maximum number of iterations
        condition_1 = optimizer.iterations() >= optimizer_params.getMaxIterations()

        # Condition 2: Convergence
        condition_2 = gtsam.checkConvergence(
            optimizer_params.getRelativeErrorTol(),
            optimizer_params.getAbsoluteErrorTol(),
            optimizer_params.getErrorTol(),
            error_before,
            error_after,
        )

        # Condition 3: Reach upper bound of lambda
        condition_3 = (
            isinstance(optimizer, gtsam.LevenbergMarquardtOptimizer)
            and optimizer.lambda_() > optimizer_params.getlambdaUpperBound()
        )

        if condition_1 or condition_2 or condition_3:
            return optimizer.values(), optimization_error

        error_before = error_after


def cal_mag_twostep_hi(
    magnetic_field: Union[np.ndarray, list],
    reference_magnetic_field: Union[np.ndarray, list],
    max_iterations: int = 2000,
    measurement_noise_std: float = 1e-3,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    The TWOSTEP method proposes a fast, robust algorithm for estimating magnetometer
    biases when the attitude is unknown. This algorithm combines the convergence
    in a single step of a heuristic algorithm currently in use with the correct
    treatment of the statistics of the measurements and does without discarding
    data.

    This algorithm was the in a first publication developed for the estimation of
    the hard-iron (Alonso, R. Shuster, M.D. (2002a). TWOSTEP: A fast, robust
    algorithm for attitude-independent magnetometer-bias determination. Journal
    of the Astronautical Sciences, 50(4):433-452.

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.
        reference_magnetic_field (numpy.ndarray or list): Reference magnetic field
            measurements in a 3, or 1x3, or 3x1 numpy array or list.
        max_iterations (int): Maximum number of iterations for the second step.
        measurement_noise_std (float): Standard deviation that characterizes the
            measurements' noise, by default 0.001 G.

    Returns:
        hard_iron (numpy.ndarray): Estimated hard-iron bias as a (3,) numpy array.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field as a
                3xN numpy array.

    Raises:
        TypeError: If the magnetic field or reference magnetic field inputs are not
            numpy arrays or lists.
        ValueError: If the magnetic field input is not a 3xN or Nx3 numpy array, if
            the reference magnetic field input is not a 3, or 1x3, or 3x1 numpy array,
            if the maximum number of iterations is not a positive integer, or if the
            measurement noise standard deviation is not a positive float.
    """
    # Check if the magnetic field input is a list and convert it to a numpy array
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)

    # Check if the reference magnetic field input is a list and convert it to a numpy array
    if isinstance(reference_magnetic_field, list):
        reference_magnetic_field = np.array(reference_magnetic_field).flatten()

    # Check if the magnetic field input is a numpy array
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field input must be a numpy array or a list.")

    # Check if the reference magnetic field input is a numpy array
    if not isinstance(reference_magnetic_field, np.ndarray):
        raise TypeError(
            "The reference magnetic field input must be a numpy array or a list."
        )

    # Check if the magnetic field input is a 3xN or Nx3 numpy array
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field input must be a 3xN or Nx3 numpy array.")

    # Check if the reference magnetic field input is a 3, numpy array
    if reference_magnetic_field.ndim != 1 and reference_magnetic_field.size != 3:
        raise ValueError(
            "The reference magnetic field input must be a 3, or 1x3, or 3x1 numpy array."
        )

    # Force the magnetic field array to be a Nx3 numpy array
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T

    # Check that the maximum number of iterations is a positive integer
    if not isinstance(max_iterations, int) or max_iterations <= 0:
        raise ValueError("The maximum number of iterations must be a positive integer.")

    # Check that the measurement noise standard deviation is a positive float
    if not isinstance(measurement_noise_std, float) or measurement_noise_std <= 0:
        raise ValueError(
            "The measurement noise standard deviation must be a positive float."
        )

    # Compute magnetic field calibration
    mf = magnetic_field

    # First step
    b0 = np.zeros((3, 1))

    # Effective measurement from paper equation (3a)
    b_matrix = np.ones((mf.shape)) * reference_magnetic_field
    z_k = (
        np.square(np.linalg.norm(mf, axis=1))
        - np.square(np.linalg.norm(b_matrix, axis=1))
    ).reshape(-1, 1)

    # Sensor measurements noise modeled as white gaussian with standard deviation epsilon_k
    epsilon_sq_k = np.ones(mf.shape) * (measurement_noise_std**2)

    # Sensor error scalar measurement noise characterization as gaussian.
    # Gaussian distribution mean, equation (7a)
    mu_k = -np.sum(epsilon_sq_k, axis=1, keepdims=True)

    # Gaussian distribution variance, equation (5.15)
    sigma_sq_k = (
        4
        * (
            (mf.reshape(-1, 1, 3) - b0.reshape(1, 3))
            @ np.apply_along_axis(np.diag, 1, epsilon_sq_k)
            @ (mf.reshape(-1, 3, 1) - b0)
        )
        + 2
        * np.apply_along_axis(
            lambda x: np.square(np.trace(np.diag(x))), 1, epsilon_sq_k
        ).reshape(-1, 1, 1)
    ).reshape(-1, 1)

    # Calculate  centered sigma squared, equation (14)
    sigma_sq_bar = 1 / np.sum(1 / sigma_sq_k)

    # Center  the  data
    mu_bar, mu_k_tilde = _cal_mag_twostep_center_data(mu_k, sigma_sq_k, sigma_sq_bar)
    z_bar, z_k_tilde = _cal_mag_twostep_center_data(z_k, sigma_sq_k, sigma_sq_bar)
    b_bar, b_k_tilde = _cal_mag_twostep_center_data(b_matrix, sigma_sq_k, sigma_sq_bar)

    # Offset and error covariance matrix calculation from paper equations (33) and (34)
    F_bb_tilde = np.einsum(
        "ijk->jk",
        (4 / sigma_sq_k.reshape(-1, 1, 1))
        * (b_k_tilde.reshape(-1, 3, 1) @ b_k_tilde.reshape(-1, 1, 3)),
    )
    F_zb = np.einsum(
        "ijk->jk",
        ((z_k_tilde - mu_k_tilde) * (2 / sigma_sq_k)).reshape(-1, 1, 1)
        * b_k_tilde.reshape(-1, 3, 1),
    )
    b = np.linalg.inv(F_bb_tilde) @ F_zb

    # Second Step: Iterative
    F_bb_bar = (
        (4 / sigma_sq_bar) * (b_bar.reshape(-1, 1) - b) @ (b_bar.reshape(-1, 1) - b).T
    )
    b_asterisk = np.copy(b)

    if np.max(np.diag(F_bb_bar) / np.diag(F_bb_tilde)) > 0.001:
        F_bb = F_bb_tilde + F_bb_bar
        gg = (F_bb_tilde @ (b - b_asterisk)) - (1 / sigma_sq_bar) * (
            z_bar - 2 * (b_bar @ b) + np.linalg.norm(b) ** 2 - mu_bar
        ) * 2 * (b_bar.reshape(-1, 1) - b)
        bn = b - np.linalg.inv(F_bb) @ gg

        iter = 1
        while ((bn - b).T @ F_bb @ (bn - b)) > 0.001:
            b = np.copy(bn)
            gg = (F_bb_tilde @ (b - b_asterisk)) - (1 / sigma_sq_bar) * (
                z_bar - 2 * (b_bar @ b) + np.linalg.norm(b) ** 2 - mu_bar
            ) * 2 * (b_bar.reshape(-1, 1) - b)
            F_bb_bar = (
                (4 / sigma_sq_bar)
                * (b_bar.reshape(-1, 1) - b)
                @ (b_bar.reshape(-1, 1) - b).T
            )
            F_bb = F_bb_tilde + F_bb_bar
            bn = b - np.linalg.inv(F_bb) @ gg

            iter += 1
            if iter > max_iterations:
                warnings.warn(
                    "Second step: Maximum number of iterations reached.", RuntimeWarning
                )
                break

    hard_iron = bn.reshape(3, 1)

    # Calibrate magnetic field
    calibrated_magnetic_field = magnetic_field - hard_iron.flatten()

    return hard_iron.flatten(), calibrated_magnetic_field


def cal_mag_twostep_hsi(
    magnetic_field: Union[np.ndarray, list],
    reference_magnetic_field: Union[np.ndarray, list],
    max_iterations: int = 2000,
    measurement_noise_std: float = 1e-3,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    The TWOSTEP method proposes a fast, robust algorithm for estimating magnetometer
    biases when the attitude is unknown. This algorithm combines the convergence
    in a single step of a heuristic algorithm currently in use with the correct
    treatment of the statistics of the measurements and does without discarding
    data.

    This algorithm was extended in a second iteration to compute also the soft-iron
    (Alonso, R. Shuster, M.D. (2002b). Complete linear attitude-independent
    magnetometer calibration. Journal of the Astronautical Science, 50(4):477-490).

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.
        reference_magnetic_field (numpy.ndarray or list): Reference magnetic field
            measurements in a 3, or 1x3, or 3x1 numpy array or list.
        max_iterations (int): Maximum number of iterations for the second step.
        measurement_noise_std (float): Standard deviation that characterizes the
            measurements' noise, by default 0.001 G.

    Returns:
        hard_iron (numpy.ndarray): Estimated hard-iron bias as a (3,) numpy array.
        soft_iron (numpy.ndarray): Estimated soft-iron matrix as a (3,3) numpy array.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field as a
            3xN numpy array.

    Raises:
        TypeError: If the magnetic field or reference magnetic field inputs are not
            numpy arrays or lists.
        ValueError: If the magnetic field input is not a 3xN or Nx3 numpy array, if
            the reference magnetic field input is not a 3, or 1x3, or 3x1 numpy array,
            if the maximum number of iterations is not a positive integer, or if the
            measurement noise standard deviation is not a positive float.
    """
    # Check if the magnetic field input is a list and convert it to a numpy array
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)

    # Check if the reference magnetic field input is a list and convert it to a numpy array
    if isinstance(reference_magnetic_field, list):
        reference_magnetic_field = np.array(reference_magnetic_field).flatten()

    # Check if the magnetic field input is a numpy array
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field input must be a numpy array or a list.")

    # Check if the reference magnetic field input is a numpy array
    if not isinstance(reference_magnetic_field, np.ndarray):
        raise TypeError(
            "The reference magnetic field input must be a numpy array or a list."
        )

    # Check if the magnetic field input is a 3xN or Nx3 numpy array
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field input must be a 3xN or Nx3 numpy array.")

    # Check if the reference magnetic field input is a 3, numpy array
    if reference_magnetic_field.ndim != 1 and reference_magnetic_field.size != 3:
        raise ValueError(
            "The reference magnetic field input must be a 3, or 1x3, or 3x1 numpy array."
        )

    # Force the magnetic field array to be a Nx3 numpy array
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T

    # Check that the maximum number of iterations is a positive integer
    if not isinstance(max_iterations, int) or max_iterations <= 0:
        raise ValueError("The maximum number of iterations must be a positive integer.")

    # Check that the measurement noise standard deviation is a positive float
    if not isinstance(measurement_noise_std, float) or measurement_noise_std <= 0:
        raise ValueError(
            "The measurement noise standard deviation must be a positive float."
        )

    # Compute magnetic field calibration
    mf = magnetic_field

    stop_tol = 1e-24  # Stop Condition from Alonso paper
    I3 = np.eye(3, dtype=np.float64)

    # TWOSTEP Centered estimate
    # Set initial guess for b and D.
    b0 = np.zeros((3, 1))
    d0 = np.zeros((3, 3))

    # Form L matrix, equations (5.10b) and (5.12a)
    l1 = 2 * mf
    l2 = -np.square(mf)
    l3 = -2 * mf[:, [0]] * mf[:, [1]]
    l4 = -2 * mf[:, [0]] * mf[:, [2]]
    l5 = -2 * mf[:, [1]] * mf[:, [2]]
    L_k = np.concatenate([l1, l2, l3, l4, l5], axis=1)

    # Compute sensor error as scalar measurement, equation (5.7a)
    h_matrix = np.ones((mf.shape)) * reference_magnetic_field
    z_k = (
        np.square(np.linalg.norm(mf, axis=1))
        - np.square(np.linalg.norm(h_matrix, axis=1))
    ).reshape(-1, 1)

    # Sensor measurements noise modeled as white gaussian with standard deviation epsilon_k
    epsilon_sq_k = np.ones(mf.shape) * (measurement_noise_std**2)

    # Sensor error scalar measurement noise characterization as gaussian.
    # Gaussian distribution mean, equation (5.14)
    mu_k = -np.sum(epsilon_sq_k, axis=1, keepdims=True)

    # Gaussian distribution variance, equation (5.15)
    sigma_sq_k = (
        4
        * np.einsum(
            "ijk->ikj",
            np.tile(I3 + d0, (mf.shape[0], 1, 1)) @ mf.reshape(-1, 3, 1)
            - np.tile(b0, (mf.shape[0], 1, 1)),
        )
        @ np.apply_along_axis(np.diag, 1, epsilon_sq_k)
        @ (
            np.tile(I3 + d0, (mf.shape[0], 1, 1)) @ mf.reshape(-1, 3, 1)
            - np.tile(b0, (mf.shape[0], 1, 1))
        )
        + 2
        * np.apply_along_axis(
            lambda x: np.square(np.trace(np.diag(x))), 1, epsilon_sq_k
        ).reshape(-1, 1, 1)
    ).reshape(-1, 1)

    # Calculate centered sigma squared, equation (5.18)
    sigma_sq_bar = 1 / np.sum(1 / sigma_sq_k)

    # Center the data, equation (5.19)
    mu_bar, mu_k_tilde = _cal_mag_twostep_center_data(mu_k, sigma_sq_k, sigma_sq_bar)
    z_bar, z_k_tilde = _cal_mag_twostep_center_data(z_k, sigma_sq_k, sigma_sq_bar)
    L_bar, L_k_tilde = _cal_mag_twostep_center_data(L_k, sigma_sq_k, sigma_sq_bar)

    # Compute fisher information matrix
    I_fisher_tilde, I_fishinv_tilde = _cal_mag_twostep_TS_fisher_centered(
        sigma_sq_k, L_k_tilde
    )

    # Compute centered estimate, equation (5.24)
    f_matrix = np.einsum(
        "ijk->jk",
        (
            (1 / sigma_sq_k).reshape(-1, 1, 1)
            * ((z_k_tilde - mu_k_tilde).reshape(-1, 1, 1) * L_k_tilde.reshape(-1, 9, 1))
        ),
    )
    theta_0_tilde = I_fishinv_tilde @ f_matrix

    # TWOSTEP Center correction
    theta_n, theta_np1 = (
        theta_0_tilde,
        theta_0_tilde,
    )  # Initiate theta for  first  iteration
    n = 0  # Initialise  iteration counter
    TS_err = np.Inf  # Initial  condition  for  error.

    # ABC is used to remove intensive calculations out of for loop
    abc = -np.einsum(
        "ijk->jk",
        (
            (1 / sigma_sq_k).reshape(-1, 1, 1)
            * ((z_k_tilde - mu_k_tilde).reshape(-1, 1, 1) * L_k_tilde.reshape(-1, 9, 1))
        ),
    )

    while TS_err > stop_tol and n < max_iterations:
        if n != 0:  # If  we are not  in the first	iteration
            theta_n = theta_np1

        # Extract  c  and  E  components
        c, e_matrix = _cal_mag_twostep_theta_to_c_E(theta_n)

        # Compute  second  derivative  of  b^2  wrt theta
        tmp = (
            np.linalg.solve((np.eye(3) + e_matrix), c)
            @ np.linalg.solve((np.eye(3) + e_matrix), c).T
        )
        dbsqdtheta_p = np.concatenate(
            [
                2 * np.linalg.solve((np.eye(3) + e_matrix), c),
                -np.diag(tmp).reshape(3, 1),
                np.vstack([-2 * tmp[0, 1], -2 * tmp[0, 2], -2 * tmp[1, 2]]),
            ]
        )
        # Compute gradient of J
        dJdThetap_tilde = abc + I_fisher_tilde @ theta_n
        dJdThetap_bar = (
            -(1 / sigma_sq_bar)
            * (L_bar.reshape(-1, 1) - dbsqdtheta_p)
            * (
                z_bar
                - (L_bar.reshape(1, -1) @ theta_n)
                + (c.T @ np.linalg.solve((np.eye(3) + e_matrix), c))
                - mu_bar
            )
        )
        dJdTheta = dJdThetap_tilde + dJdThetap_bar

        # Calculate Fisher matrix
        I_fisher_bar = _cal_mag_twostep_TS_fisher_center(
            sigma_sq_bar, L_bar, dbsqdtheta_p
        )

        # Update theta
        theta_np1 = theta_n - np.linalg.solve((I_fisher_tilde + I_fisher_bar), dJdTheta)

        # Compute error
        TS_err = ((theta_np1 - theta_n).T @ (I_fisher_tilde + I_fisher_bar)) @ (
            theta_np1 - theta_n
        )
        n += 1

    b, d_matrix = _cal_mag_twostep_theta_to_b_D(theta_np1)

    # Extract covariance matrix
    m_cd = np.array(
        [
            [b[0, 0], 0, 0, b[1, 0], b[2, 0], 0],
            [0, b[1, 0], 0, b[0, 0], 0, b[2, 0]],
            [0, 0, b[2, 0], 0, b[0, 0], b[1, 0]],
        ]
    )
    m_ed = np.array(
        [
            [2 * d_matrix[0, 0], 0, 0, 2 * d_matrix[0, 1], 2 * d_matrix[0, 2], 0],
            [0, 2 * d_matrix[1, 1], 0, 2 * d_matrix[0, 1], 0, 2 * d_matrix[1, 2]],
            [0, 0, 2 * d_matrix[2, 2], 0, 2 * d_matrix[0, 2], 2 * d_matrix[1, 2]],
            [
                d_matrix[0, 1],
                d_matrix[0, 1],
                0,
                d_matrix[0, 0] + d_matrix[1, 1],
                d_matrix[1, 2],
                d_matrix[0, 2],
            ],
            [
                d_matrix[0, 2],
                0,
                d_matrix[0, 2],
                d_matrix[1, 2],
                d_matrix[0, 0] + d_matrix[2, 2],
                d_matrix[0, 1],
            ],
            [
                0,
                d_matrix[1, 2],
                d_matrix[1, 2],
                d_matrix[0, 2],
                d_matrix[0, 1],
                d_matrix[1, 1] + d_matrix[2, 2],
            ],
        ]
    )
    dbD_dcE = np.eye(9)
    dbD_dcE[:3, :3], dbD_dcE[:3, 3:] = np.eye(3) + d_matrix, m_cd
    dbD_dcE[3:, :3], dbD_dcE[3:, 3:] = np.zeros((6, 3)), 2 * np.eye(6) @ m_ed
    dbD_dcE = np.linalg.inv(dbD_dcE)
    # Cov_est = dbD_dcE @ np.linalg.solve((I_fisher_tilde + I_fisher_bar), dbD_dcE.T)

    # END   TWOSTEP
    hard_iron = (np.linalg.inv(np.eye(3) + d_matrix)) @ b
    soft_iron = np.linalg.inv(np.eye(3) + d_matrix)

    # Calibrate magnetic field
    calibrated_magnetic_field = (
        np.linalg.inv(soft_iron)
        @ (magnetic_field.reshape(3, -1) - hard_iron.reshape(3, 1))
    ).T

    return hard_iron.flatten(), soft_iron, calibrated_magnetic_field


def _cal_mag_twostep_center_data(
    x: np.ndarray, sigma_sq_k: np.ndarray, sigma_sq_bar: float
) -> Tuple[float, np.ndarray]:
    """
    Calculates  the  centered  and  center  components  of  a vector X.
    Based on the equations (13a), (13b) and (14) in (Alonso, R. Shuster, M.D.
    (2002a). TWOSTEP: A fast robust algorithm for attitude-independent
    magnetometer-bias determination. Journal of the Astronautical Sciences,
    50(4):433-452).

    Args:
        x (np.ndarray): Column vector of data as a (n, 1) numpy array.
        sigma_sq_k (np.ndarray): Column vector with the variance of each sample as
            a (n, 1) numpy array.
        sigma_sq_bar (float): Inverse of the sum of the reciprocal of the variances.

    Returns:
        x_bar (float): The centered data, i.e., the sum of the samples weighted by
            the reciprocal of the variance, multiplied by the inverse of the sum of
            the reciprocal of the variances.
        x_tilde (np.ndarray): The samples with the X_bar subtracted.
    """
    # Center   component
    x_bar = sigma_sq_bar * np.sum(x * (1.0 / sigma_sq_k), axis=0)
    # Centered  component
    x_tilde = x - np.tile(x_bar, (x.shape[0], 1))

    return x_bar, x_tilde


def _cal_mag_twostep_TS_fisher_centered(
    sigma_sq: np.ndarray, L_tilde: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the fisher information matrix for the centered estimate, when
    given variance sigma_sq and centered vectors of L_tilde, based on (5.28)
    in Diane, J.P. (2013). Magnetic test facility - sensor and coil calibrations.
    Master's thesis, University of Adelaide, School of Electrical and Electronic
    Engineering.

    Args:
        sigma_sq (np.ndarray): Variance based of each sample defined in equation (5b)
            as a (-1, 1) numpy array.
        L_tilde (np.ndarray): L metric for each sample defined in equation (30) as a
            (n, 9) numpy array.

    Returns:
        I_fisher_tilde (np.ndarray): The fisher information matrix as a (9, 9) numpy array.
        Lfishinv_tilde (np.ndarray): The inverse of the fisher information matrix as a
            (9, 9) numpy array.
    """
    # Compute  fisher  information  matrix and the inverse
    I_fisher_tilde = L_tilde.T @ (L_tilde * (1 / sigma_sq))
    Lfishinv_tilde = np.linalg.inv(I_fisher_tilde)

    return I_fisher_tilde, Lfishinv_tilde


def _cal_mag_twostep_theta_to_c_E(theta: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extracts c and E elements from theta as equation (30) in Alonso, R. Shuster,
    M.D. (2002b). Complete linear attitude-independent magnetometer calibration.
    Journal of the Astronautical Science, 50(4):477-490.

    Args:
        theta (np.ndarray): Theta vector defined in equation (30) as a (9, 1) numpy array.

    Returns:
        c (np.ndarray): The vector c as a (3, 1) numpy array.
        E (np.ndarray): The matrix E as a (3, 3) numpy array.
    """
    c = theta[:3, :]
    e_matrix = np.array(
        [
            [theta[3, 0], theta[6, 0], theta[7, 0]],
            [theta[6, 0], theta[4, 0], theta[8, 0]],
            [theta[7, 0], theta[8, 0], theta[5, 0]],
        ]
    )
    return c, e_matrix


def _cal_mag_twostep_TS_fisher_center(
    sigma_sq_bar: float, L_bar: np.ndarray, dbsqdtheta_p: np.ndarray
) -> np.ndarray:
    """
    Computes center information matrix based in (5.29) in Diane, J.P. (2013).
    Magnetic test facility - sensor and coil calibrations. Master's thesis,
    University of Adelaide, School of Electrical and Electronic Engineering.

    Args:
        sigma_sq_bar (float): Inverse of the sum of the reciprocal of the variances.
        L_bar (np.ndarray): The centered L data, i.e., the sum of the samples
            weighted by the reciprocal of the variance, multiplied by the inverse
            of the sum of the reciprocal, as a (9, ) numpy array.
        dbsqdtheta_p (np.ndarray): The differentiation of the norm of the magnetic
            field measurements squared with respect to the theta prime value as
            described in equation (40) as a (9, 1) numpy array.

    Returns:
        I_fisher_bar (np.ndarray): The center of the Fisher matrix as a (9, 9) numpy array.
    """
    I_fisher_bar = (
        (L_bar.reshape(-1, 1) - dbsqdtheta_p)
        @ ((L_bar.reshape(-1, 1) - dbsqdtheta_p).T)
    ) / sigma_sq_bar
    return I_fisher_bar


def _cal_mag_twostep_theta_to_b_D(theta: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Converts a value of theta to usable physical values as described in
    equation (31) of Alonso, R. Shuster, M.D. (2002b). Complete linear
    attitude-independent magnetometer calibration. Journal of the Astronautical
    Science, 50(4):477-490.

    Args:
        theta (np.ndarray): Theta vector as a (9, 1) numpy array.

    Returns:
        b (np.ndarray): The vector b as a (3, 1) numpy array.
        d_matrix (np.ndarray): The matrix D as a (3, 3) numpy array.
    """
    c, e_matrix = _cal_mag_twostep_theta_to_c_E(theta)
    s_matrix, u_matrix = np.linalg.eig(e_matrix)
    w_matrix = -np.eye(3) + np.sqrt(np.eye(3) + np.diag(s_matrix))
    d_matrix = u_matrix @ w_matrix @ u_matrix.T
    # Calculate b  using  the  inverse of (I+D)
    b = np.linalg.solve(np.eye(3) + d_matrix, c)
    return b, d_matrix


def cal_mag_sphere_fit(
    magnetic_field: Union[np.ndarray, list]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    The sphere fit method fits a sphere to a collection of data using a closed
    form for the solution. With this purpose, propose an optimization problem that
    seeks to minimize the sum:

    $$\\sum_i ((x_i-x_c)^2+(y_i-y_c)^2+(z_i-z_c)^2-r^2)^2$$

    Where x, y, and z is the data; $x_c$, $y_c$, and $z_c$ are the sphere center;
    and r is the radius.

    The method assumes that points are not in a singular configuration and are
    real numbers to solve this problem. If you have coplanar data, use a circle
    fit with svd for determining the plane, recommended [Circle Fit (Pratt method),
    by Nikolai Chernov](http://www.mathworks.com/matlabcentral/fileexchange/22643)

    Inspired by Alan Jennings, University of Dayton, implementation ([source](
    https://www.mathworks.com/matlabcentral/fileexchange/34129-sphere-fit-least-squared))

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.

    Returns:
        hard_iron (numpy.ndarray): Hard iron bias as a (3,) numpy array.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements

    Raises:
        TypeError: If the input is not a numpy array or a list.
        ValueError: If the input is not a 3xN or Nx3 numpy array.
    """
    # Check if the input is a list and convert it to a numpy array
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)

    # Check if the input is a numpy array
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The input must be a numpy array or a list.")

    # Check if the input is a 3xN or Nx3 numpy array
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The input must be a 3xN or Nx3 numpy array.")

    # Force the array to be a Nx3 numpy array
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T

    # Compute magnetic field calibration
    mf = magnetic_field
    a_matrix = np.array(
        [
            [
                np.mean(mf[:, 0] * (mf[:, 0] - np.mean(mf[:, 0]))),
                2 * np.mean(mf[:, 0] * (mf[:, 1] - np.mean(mf[:, 1]))),
                2 * np.mean(mf[:, 0] * (mf[:, 2] - np.mean(mf[:, 2]))),
            ],
            [
                0,
                np.mean(mf[:, 1] * (mf[:, 1] - np.mean(mf[:, 1]))),
                2 * np.mean(mf[:, 1] * (mf[:, 2] - np.mean(mf[:, 2]))),
            ],
            [0, 0, np.mean(mf[:, 2] * (mf[:, 2] - np.mean(mf[:, 2])))],
        ]
    )

    a_matrix = a_matrix + a_matrix.T
    b_matrix = np.array(
        [
            [
                np.mean(
                    (mf[:, 0] ** 2 + mf[:, 1] ** 2 + mf[:, 2] ** 2)
                    * (mf[:, 0] - np.mean(mf[:, 0]))
                )
            ],
            [
                np.mean(
                    (mf[:, 0] ** 2 + mf[:, 1] ** 2 + mf[:, 2] ** 2)
                    * (mf[:, 1] - np.mean(mf[:, 1]))
                )
            ],
            [
                np.mean(
                    (mf[:, 0] ** 2 + mf[:, 1] ** 2 + mf[:, 2] ** 2)
                    * (mf[:, 2] - np.mean(mf[:, 2]))
                )
            ],
        ]
    )

    hard_iron = np.array(np.linalg.lstsq(a_matrix, b_matrix, rcond=None)[0])

    # Calibrate magnetic field
    calibrated_magnetic_field = magnetic_field - hard_iron.flatten()

    return hard_iron.flatten(), calibrated_magnetic_field


def cal_mag_sar_ls(
    magnetic_field: Union[np.ndarray, list],
    angular_rate: Union[np.ndarray, list],
    time: Union[np.ndarray, list],
) -> Tuple[np.ndarray, np.ndarray]:
    """
    The linear least squares for sensor bias calibration is seeks to minimize the
    sum of squared residuals

    $$\\sum_{i=1}^{n} \\frac{1}{\\sigma_i^2} ||\\dot{x}_i + \\omega_i \\times (x_i - b)||^2$$

    Where $x(t)$ is the measured magnetic field, $\\dot{x(t)}$ is the measured
    magnetic field differentiated with respect to time, $\\omega(t)$ is the
    measured angular-rate in instrument coordinates, $b$ is the hard-iron, and
    $\\times$ is the standard cross product operator.

    This optimization problem can be solved in an analytical way. For further
    information refer to section IV.A in Troni, G. and Whitcomb, L. L. (2019).
    Field sensor bias calibration with angular-rate sensors: Theory and experimental
    evaluation with application to magnetometer calibration. IEEE/ASME Transactions
    on Mechatronics, 24(4):1698--1710.

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.
        angular_rate (numpy.ndarray or list): Angular rate measurements in a 3xN or
            Nx3 numpy array or list.
        time (numpy.ndarray or list): Time measurements in a 1D numpy array or list.

    Returns:
        hard_iron (numpy.ndarray): Estimated hard-iron bias as a (3,) numpy array.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements.

    Raises:
        TypeError: If the magnetic field, angular rate, or time are not numpy arrays or lists.
        ValueError: If the magnetic field, angular rate, or time are not 3xN or Nx3 numpy arrays.
        ValueError: If the magnetic field, angular rate, and time do not have the same number of samples.
    """
    # Check if the magnetic_field, angular_rate, and time are lists and convert them to numpy arrays
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)

    # Check if the magnetic_field, angular_rate, and time are numpy arrays
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")

    # Check if the magnetic_field and angular_rate are 3xN or Nx3 numpy arrays
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")

    # Check if the time is a 1D numpy array
    time = time.flatten()
    if time.ndim != 1:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force the magnetic_field and angular_rate to be Nx3 numpy arrays
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T
    if angular_rate.shape[0] == 3:
        angular_rate = angular_rate.T

    # Check if the magnetic_field, angular_rate, and time have the same number of samples
    if (
        magnetic_field.shape[0] != angular_rate.shape[0]
        or magnetic_field.shape[0] != time.shape[0]
    ):
        raise ValueError(
            "The magnetic field, angular rate, and time must have the same number of samples."
        )

    # Compute the magnetic calibration
    # Get the data variance
    magnetic_field_variance = _cal_mag_sar_ls_get_sigma_noise(magnetic_field)
    sigma_i = np.linalg.norm(magnetic_field_variance).reshape(-1, 1, 1)

    # Compute the skew-symmetric matrix of the angular rate.
    skew_symmetric_angular_rate = np.apply_along_axis(vec_to_so3, 1, angular_rate)

    # Compute the magnetic field derivative
    magnetic_field_derivative = np.diff(magnetic_field, axis=0) / np.diff(time).reshape(
        -1, 1
    )
    magnetic_field_derivative = np.concatenate(
        [np.zeros((1, 3)), magnetic_field_derivative], axis=0
    )

    # Estimate b
    b1_inv = np.linalg.inv(
        np.einsum("ijk->jk", (skew_symmetric_angular_rate**2) * (1 / sigma_i))
    )

    yi = np.einsum(
        "ijk->ikj",
        np.cross(angular_rate.reshape(-1, 1, 3), magnetic_field.reshape(-1, 1, 3))
        + magnetic_field_derivative.reshape(-1, 1, 3),
    )
    b2 = np.einsum("ijk->jk", (skew_symmetric_angular_rate @ yi) * (1 / sigma_i))

    hard_iron = b1_inv @ b2

    # Calibrate magnetic field
    calibrated_magnetic_field = magnetic_field - hard_iron.flatten()

    return hard_iron.flatten(), calibrated_magnetic_field


def cal_mag_sar_kf(
    magnetic_field: Union[np.ndarray, list],
    angular_rate: Union[np.ndarray, list],
    time: Union[np.ndarray, list],
    gains: Tuple[float, float] = (1.0, 1.0),
    f_normalize: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    The Kalman filter for sensor bias calibration uses the system model with  a
    discretization of the continuous-time system the sensor bias estimation can
    be solved with a standard discrete-time Kalman filter implementation that
    does not require differentiation.

    $$\\dot{x}_i = -\\omega_i \\times (x_i - b)$$

    Where $x(t)$ is the measured magnetic field, $\\dot{x(t)}$ is the measured
    magnetic field differentiated with respect to time, $\\omega(t)$ is the
    measured angular-rate in instrument coordinates, and $b$ is the hard-iron.

    For further information refer to section IV.B in Troni, G. and Whitcomb, L. L.
    (2019). Field sensor bias calibration with angular-rate sensors: Theory and
    experimental evaluation with application to magnetometer calibration. IEEE/ASME
    Transactions on Mechatronics, 24(4):1698--1710.

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.
        angular_rate (numpy.ndarray or list): Angular rate measurements in a 3xN or
            Nx3 numpy array or list.
        time (numpy.ndarray or list): Time measurements in a 1D numpy array or list.
        gains (tuple): Kalman filter gains.
        f_normalize (bool): Whether the k2 gain should be scaled by and adaptive
            constant computed as the reciprocal of the norm of the gyroscope measurement
            for that step, by default False.

    Returns:
        hard_iron (numpy.ndarray): Estimated hard-iron bias as a (3,) numpy array.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements.
        calibrated_filtered_magnetic_field (numpy.ndarray): Calibrated and filtered magnetic field measurements.

    Raises:
        TypeError: If the magnetic field, angular rate, or time are not numpy arrays or lists.
        ValueError: If the magnetic field, angular rate, or time are not 3xN or Nx3 numpy arrays.
        ValueError: If the magnetic field, angular rate, and time do not have the same number of samples.
        TypeError: If the gains are not a tuple of floats.
        TypeError: If the f_normalize is not a boolean.
    """
    # Check if the magnetic_field, angular_rate, and time are lists and convert them to numpy arrays
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)

    # Check if the magnetic_field, angular_rate, and time are numpy arrays
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")

    # Check if the magnetic_field and angular_rate are 3xN or Nx3 numpy arrays
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")

    # Check if the time is a 1D numpy array
    time = time.flatten()
    if time.ndim != 1:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force the magnetic_field and angular_rate to be Nx3 numpy arrays
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T
    if angular_rate.shape[0] == 3:
        angular_rate = angular_rate.T

    # Check if the magnetic_field, angular_rate, and time have the same number of samples
    if (
        magnetic_field.shape[0] != angular_rate.shape[0]
        or magnetic_field.shape[0] != time.shape[0]
    ):
        raise ValueError(
            "The magnetic field, angular rate, and time must have the same number of samples."
        )

    # Check that the gains are a tuple of floats
    if not isinstance(gains, tuple):
        raise TypeError("The gains must be a tuple of floats.")
    if not all(isinstance(gain, float) for gain in gains):
        raise TypeError("The gains must be a tuple of floats.")

    # Check that the f_normalize is a boolean
    if not isinstance(f_normalize, bool):
        raise TypeError("The f_normalize must be a boolean.")

    # Compute the magnetic calibration
    # Initial parameters
    b0 = np.zeros((3,))
    k1a = gains[0]
    k1b = gains[1] if len(gains) >= 2 else gains[0]
    k2 = gains[2] if len(gains) >= 3 else gains[1]
    mf = magnetic_field.reshape(3, -1)
    w = angular_rate.reshape(3, -1)
    dt = np.diff(time)
    dt_vec = np.concatenate([np.array([dt[0]]), dt])

    # Kalman Model
    Bc = np.zeros([6, 1])
    # Measurement model
    H1 = np.hstack([np.eye(3), np.zeros([3, 3])])
    # Process noise covariance
    Qc = np.diag([k1a, k1a, k1a, k1b, k1b, k1b])
    # Variance in the measurements
    R = np.diag([k2, k2, k2])

    # KF
    F1 = _cal_mag_sar_kf_transition_matrix([0, 0, 0])
    n = F1.shape[0]
    m = F1.shape[1]
    MM = np.zeros([n, mf.shape[1]])
    PP = np.zeros([n, m, mf.shape[1]])
    AA = np.zeros([n, m, mf.shape[1]])
    QQ = np.zeros([n, m, mf.shape[1]])
    KK = np.zeros([n, H1.shape[0], mf.shape[1]])

    # Initial guesses for the state mean and covariance.
    x = np.hstack([mf[:, 0], b0])
    p01 = 0.001  # P0 gyro
    p02 = 0.001  # P0 bias
    P0 = np.diag([p01, p01, p01, p02, p02, p02])
    P = P0

    # Filtering steps.
    for ix in range(mf.shape[1]):
        # Discretization of the continous-time system (dtk)
        dtk = dt_vec[ix]
        u = w[:, ix]

        [Ak, Bk, Qk] = _cal_mag_sar_kf_lti_discretize(
            _cal_mag_sar_kf_transition_matrix(u), Bc, Qc, dtk
        )

        AA[:, :, ix] = Ak
        QQ[:, :, ix] = Qk

        # Prediction
        [x, P] = _cal_mag_sar_kf_predict(x, P, Ak, Qk)
        [x, P, K, dy, S] = _cal_mag_sar_kf_update(x, P, mf[:, ix], H1, R)

        MM[:, ix] = x
        PP[:, :, ix] = P
        KK[:, :, ix] = K

    # Final Bias averaging last 20%
    hard_iron = np.mean(
        MM[3:, -int(np.round(mf.shape[1] * 0.2)) :], axis=1, keepdims=True
    )

    # Calibrate magnetic field
    calibrated_magnetic_field = magnetic_field - hard_iron.flatten()
    calibrated_filtered_magnetic_field = MM[:3, :].T

    return (
        hard_iron.flatten(),
        calibrated_magnetic_field,
        calibrated_filtered_magnetic_field,
    )


def cal_mag_sar_aid(
    magnetic_field: Union[np.ndarray, list],
    angular_rate: Union[np.ndarray, list],
    time: Union[np.ndarray, list],
    gains: Tuple[float, float] = (1.0, 1.0),
    f_normalize: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    The adaptive identification for sensor bias calibration proposes that the
    unknown sensor bias, $b$, can be estimated on-line with a novel adaptive
    identification algorithm. The possible advantages of this adaptive approach
    are that (i) it does not require numerical differentiation of the sensor
    measurement $x(t)$, (ii) it is less computationally expensive than the SAR-KF,
    and (iii) it could be combined with other nonlinear observer methods.

    For further information refer to section IV.C in Troni, G. and Whitcomb, L. L.
    (2019). Field sensor bias calibration with angular-rate sensors: Theory and
    experimental evaluation with application to magnetometer calibration. IEEE/ASME
    Transactions on Mechatronics, 24(4):1698--1710.

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.
        angular_rate (numpy.ndarray or list): Angular rate measurements in a 3xN or
            Nx3 numpy array or list.
        time (numpy.ndarray or list): Time measurements in a 1D numpy array or list.
        gains (tuple): Gains defined in the set of equations (5) of the proposed method as
            a tuple of floats, by default (1.0, 1.0)
        f_normalize (bool): Whether the k2 gain should be scaled by and adaptive
            constant computed as the reciprocal of the norm of the gyroscope measurement
            for that step, by default False.

    Returns:
        hard_iron (numpy.ndarray): Estimated hard-iron bias as a (3,) numpy array.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements.
        calibrated_filtered_magnetic_field (numpy.ndarray): Calibrated and filtered magnetic field measurements.

    Raises:
        TypeError: If the magnetic field, angular rate, or time are not numpy arrays or lists.
        ValueError: If the magnetic field, angular rate, or time are not 3xN or Nx3 numpy arrays.
        ValueError: If the magnetic field, angular rate, and time do not have the same number of samples.
        TypeError: If the gains are not a tuple of floats.
        TypeError: If the f_normalize is not a boolean.
    """
    # Check if the magnetic_field, angular_rate, and time are lists and convert them to numpy arrays
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)

    # Check if the magnetic_field, angular_rate, and time are numpy arrays
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")

    # Check if the magnetic_field and angular_rate are 3xN or Nx3 numpy arrays
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")

    # Check if the time is a 1D numpy array
    time = time.flatten()
    if time.ndim != 1:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force the magnetic_field and angular_rate to be Nx3 numpy arrays
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T
    if angular_rate.shape[0] == 3:
        angular_rate = angular_rate.T

    # Check if the magnetic_field, angular_rate, and time have the same number of samples
    if (
        magnetic_field.shape[0] != angular_rate.shape[0]
        or magnetic_field.shape[0] != time.shape[0]
    ):
        raise ValueError(
            "The magnetic field, angular rate, and time must have the same number of samples."
        )

    # Check that the gains are a tuple of floats
    if not isinstance(gains, tuple):
        raise TypeError("The gains must be a tuple of floats.")
    if not all(isinstance(gain, float) for gain in gains):
        raise TypeError("The gains must be a tuple of floats.")

    # Check that the f_normalize is a boolean
    if not isinstance(f_normalize, bool):
        raise TypeError("The f_normalize must be a boolean.")

    # Compute the magnetic calibration
    # Initial parameters
    b0 = np.zeros((3,))
    k1 = gains[0]
    k2 = gains[1]
    mf = magnetic_field.reshape(3, -1)
    w = angular_rate.reshape(3, -1)
    dt = np.diff(time)
    dt_vec = np.concatenate([np.array([dt[0]]), dt])

    # Compute the skew-symmetric matrix of the angular rate.
    skew_symmetric_angular_rate = np.apply_along_axis(vec_to_so3, 1, angular_rate)

    # Adaptive ID system
    mh = np.zeros((3, mf.shape[1] + 1))
    mhd = np.zeros((3, mf.shape[1]))
    bh = np.zeros((3, mf.shape[1] + 1))
    bhd = np.zeros((3, mf.shape[1]))
    mh[:, 0] = magnetic_field[0, :]
    bh[:, 0] = b0

    for ix in range(mf.shape[1]):
        mhd[:, ix] = (
            -skew_symmetric_angular_rate[ix, :, :] @ mh[:, ix]
            + skew_symmetric_angular_rate[ix, :, :] @ bh[:, ix]
            - k1 * (mh[:, ix] - mf[:, ix])
        )

        if (np.linalg.norm(w[:, ix]) > 0.01) and f_normalize:
            k_adap = 1 / np.linalg.norm(w[:, ix])
            bhd[:, ix] = (
                -k_adap
                * k2
                * skew_symmetric_angular_rate[ix, :, :]
                @ (mh[:, ix] - mf[:, ix])
            )
        else:
            bhd[:, ix] = (
                -k2 * skew_symmetric_angular_rate[ix, :, :].T @ (mh[:, ix] - mf[:, ix])
            )

        mh[:, ix + 1] = mh[:, ix] + dt_vec[ix] * mhd[:, ix]
        bh[:, ix + 1] = bh[:, ix] + dt_vec[ix] * bhd[:, ix]

    # Final Bias averaging last 20%
    hard_iron = np.mean(
        bh[:, -int(np.round(mf.shape[1] * 0.2)) :], axis=1, keepdims=True
    )

    # Calibrate magnetic field
    calibrated_magnetic_field = magnetic_field - hard_iron.flatten()
    calibrated_filtered_magnetic_field = mh[:, :-1].T

    return (
        hard_iron.flatten(),
        calibrated_magnetic_field,
        calibrated_filtered_magnetic_field,
    )


def _cal_mag_sar_ls_get_sigma_noise(mat: np.ndarray) -> np.ndarray:
    """
    Gets a nxm array and returns an array of the same size where
    each row is the variance of each axis. The assumption is that the variance is
    the same for all samples, then all the rows are equals.

    Args:
        mat (np.ndarray): Data matrix as a (n, m) numpy array.

    Returns:
        np.ndarray: Data matrix where each column is the axis variance as a numpy array.
    """
    # Sensor Measurement
    mat_copy = np.copy(mat)

    # Compute data trend
    mat_center = savgol_filter(mat_copy, 25, 2, axis=0)

    # Remove the data trend to have a zero-mean data
    mat_centered = mat - mat_center
    var = np.var(mat_centered, axis=0, keepdims=True)
    sigma = np.tile(var, (mat.shape[0], 1))
    return sigma


def _cal_mag_sar_kf_lti_discretize(
    Ac: np.ndarray, Bc: np.ndarray = None, Qc: np.ndarray = None, dt: float = 1
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
        np.ndarray: Discrete state transition matrix.
        np.ndarray: Discrete input matrix.
        np.ndarray: Discrete covariance matrix.
    """
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


def _cal_mag_sar_kf_predict(
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
        np.ndarray: Updated state mean.
        np.ndarray: Updated state covariance.
    """

    # Check Arguments
    n = A.shape[0]

    # Default state transition matrix to the identity matrix if not provided
    if A is None:
        A = np.eye(n)

    # Default process noise covariance to zero matrix if not provided
    if Q is None:
        Q = np.zeros([n, 1])

    # Default input matrix to the identity matrix if not provided
    if (B is None) and (u is not None):
        B = np.eye(n)

    # Prediction step
    # State
    if u is None:
        x = np.dot(A, x)
    else:
        x = np.dot(A, x) + np.dot(B, u)

    # Covariance
    P = np.dot(np.dot(A, P), A.T) + Q

    return x, P


def _cal_mag_sar_kf_update(
    x: np.ndarray, P: np.ndarray, y: np.ndarray, H: np.ndarray, R: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Update step of the Kalman filter.

    Args:
        x (np.ndarray): State mean.
        P (np.ndarray): State covariance.
        y (np.ndarray): Measurement.
        H (np.ndarray): Measurement matrix.
        R (np.ndarray): Measurement noise covariance.
    """
    # Compute measurement residual
    dy = y - np.dot(H, x)
    # Compute covariance residual
    S = R + np.dot(np.dot(H, P), H.T)
    # Compute Kalman Gain
    K = np.dot(np.dot(P, H.T), np.linalg.inv(S))

    # Update state estimate
    dy = dy.flatten()
    x = x + np.dot(K, dy)
    P = P - np.dot(np.dot(K, H), P)

    return x, P, K, dy, S


def _cal_mag_sar_kf_transition_matrix(angular_rate: np.ndarray) -> np.ndarray:
    """
    Compute the transition matrix for the Kalman filter.
    """
    angular_rate = (
        angular_rate.flatten() if isinstance(angular_rate, np.ndarray) else angular_rate
    )
    skew_symmetric_angular_rate = vec_to_so3(angular_rate)
    a_matrix = np.zeros((6, 6))
    a_matrix[:3, :] = np.hstack(
        [-skew_symmetric_angular_rate, skew_symmetric_angular_rate]
    )
    return a_matrix


def cal_mag_magyc_ls(
    magnetic_field: Union[np.ndarray, list],
    angular_rate: Union[np.ndarray, list],
    time: Union[np.ndarray, list],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Proposed method for the full calibration of a three-axis magnetometer
    using magnetic field and angular rate measurements. This particular approach
    is based on a least squares optimization and poses the probems as a linear
    least squares optimization problem.

    Even though a closed solution can be computed, it is an ill-conditioned problem
    and the optimization is preferred.

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.
        angular_rate (numpy.ndarray or list): Angular rate measurements in a 3xN or
            Nx3 numpy array or list.
        time (numpy.ndarray or list): Time stamps of the measurements.

    Returns:
        hard_iron (numpy.ndarray): Estimated hard-iron bias as a (3,) numpy array.
        soft_iron (numpy.ndarray): Estimated soft-iron matrix as a (3, 3) numpy array.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements.

    Raises:
        TypeError: If the magnetic field, angular rate, and time are not numpy arrays or lists.
        ValueError: If the magnetic field and angular rate are not 3xN or Nx3 numpy
            arrays, or if the time is not a 1D numpy array.
    """
    # Check if the magnetic_field, angular_rate, and time are lists and convert them to numpy arrays
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)

    # Check if the magnetic_field, angular_rate, and time are numpy arrays
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")

    # Check if the magnetic_field and angular_rate are 3xN or Nx3 numpy arrays
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")

    # Check if the time is a 1D numpy array
    time = time.flatten()
    if time.ndim != 1:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force the magnetic_field and angular_rate to be Nx3 numpy arrays
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T
    if angular_rate.shape[0] == 3:
        angular_rate = angular_rate.T

    # Check if the magnetic_field, angular_rate, and time have the same number of samples
    if (
        magnetic_field.shape[0] != angular_rate.shape[0]
        or magnetic_field.shape[0] != time.shape[0]
    ):
        raise ValueError(
            "The magnetic field, angular rate, and time must have the same number of samples."
        )

    # Compute the skew symmetric matrix of the angular rate
    skew_symmetric_angular_rate = np.apply_along_axis(
        _cal_mag_magyc_vec_to_so3_jax, 1, angular_rate
    )

    # Compute the magnetic field derivative
    magnetic_field_derivative = np.diff(magnetic_field, axis=0) / np.diff(time).reshape(
        -1, 1
    )
    magnetic_field_derivative = np.concatenate(
        [np.zeros((1, 3)), magnetic_field_derivative], axis=0
    ).reshape(-1, 3, 1)

    # Reshape magnetic field
    magnetic_field_3d = magnetic_field.reshape(-1, 3, 1)

    # Compute the magnetic calibration
    # Least Squares Initial Guess and Constraints
    x0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    # Optimization
    res = least_squares(
        _cal_mag_magyc_ls_cost_function,
        x0,
        jac=_cal_mag_magyc_ls_jacobian,
        method="dogbox",
        verbose=0,
        loss="linear",
        max_nfev=1000,
        ftol=1.00e-06,
        gtol=None,
        xtol=None,
        x_scale="jac",
        args=(
            magnetic_field_3d,
            magnetic_field_derivative,
            skew_symmetric_angular_rate,
        ),
    )

    # Compute SI and HI
    x = res["x"]
    lower_triangular_matrix = np.array(
        [[exp(x[0]), 0, 0], [x[1], exp(x[2]), 0], [x[3], x[4], 1 / exp(x[0] + x[2])]]
    )
    soft_iron = np.linalg.inv(lower_triangular_matrix @ lower_triangular_matrix.T)
    hard_iron = soft_iron @ x[5:].reshape(3, 1)

    # Calibrate magnetic field
    calibrated_magnetic_field = (
        np.linalg.inv(soft_iron)
        @ (magnetic_field.reshape(3, -1) - hard_iron.reshape(3, 1))
    ).T

    return hard_iron.flatten(), soft_iron, calibrated_magnetic_field


def cal_mag_magyc_nls(
    magnetic_field: Union[np.ndarray, list],
    angular_rate: Union[np.ndarray, list],
    time: Union[np.ndarray, list],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Proposed method for the full calibration of a three-axis magnetometer
    and a three-axis gyroscope using magnetic field and angular rate measurements.
    This particular approach is based on a least squares optimization and poses
    the probems as a non-linear least squares optimization problem.

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.
        angular_rate (numpy.ndarray or list): Angular rate measurements in a 3xN or
            Nx3 numpy array or list.
        time (numpy.ndarray or list): Time stamps of the measurements.

    Returns:
        hard_iron (numpy.ndarray): Estimated hard-iron bias as a (3,) numpy array.
        soft_iron (numpy.ndarray): Estimated soft-iron matrix as a (3, 3) numpy array.
        gyro_bias (numpy.ndarray): Estimated gyroscope bias as a (3,) numpy array in rad/s.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements.
        calibrated_angular_rate (numpy.ndarray): Calibrated angular rate measurements in rad/s.

    Raises:
        TypeError: If the magnetic field, angular rate, and time are not numpy arrays or lists.
        ValueError: If the magnetic field and angular rate are not 3xN or Nx3 numpy
            arrays, or if the time is not a 1D numpy array.
    """
    # Check if the magnetic_field, angular_rate, and time are lists and convert them to numpy arrays
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)

    # Check if the magnetic_field, angular_rate, and time are numpy arrays
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")

    # Check if the magnetic_field and angular_rate are 3xN or Nx3 numpy arrays
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")

    # Check if the time is a 1D numpy array
    time = time.flatten()
    if time.ndim != 1:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force the magnetic_field and angular_rate to be Nx3 numpy arrays
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T
    if angular_rate.shape[0] == 3:
        angular_rate = angular_rate.T

    # Check if the magnetic_field, angular_rate, and time have the same number of samples
    if (
        magnetic_field.shape[0] != angular_rate.shape[0]
        or magnetic_field.shape[0] != time.shape[0]
    ):
        raise ValueError(
            "The magnetic field, angular rate, and time must have the same number of samples."
        )

    # Compute the skew symmetric matrix of the angular rate
    skew_symmetric_angular_rate = npj.apply_along_axis(
        _cal_mag_magyc_vec_to_so3_jax, 1, angular_rate
    )

    # Compute the magnetic field derivative
    magnetic_field_derivative = np.diff(magnetic_field, axis=0) / np.diff(time).reshape(
        -1, 1
    )
    magnetic_field_derivative = np.vstack(
        [np.zeros((1, 3)), magnetic_field_derivative]
    ).reshape(-1, 3, 1)

    # Reshape magnetic field
    magnetic_field_3d = magnetic_field.reshape(-1, 3, 1)

    # Compute the magnetic calibration
    # Least Squares Initial Guess and Constraints
    x0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    # Optimization
    res = least_squares(
        _cal_mag_magyc_nls_cost_function,
        x0,
        method="dogbox",
        jac=_cal_mag_magyc_compute_jacobian_nls_jax,
        verbose=0,
        loss="linear",
        max_nfev=1000,
        ftol=1.00e-06,
        gtol=None,
        xtol=None,
        x_scale="jac",
        args=(
            magnetic_field_3d,
            magnetic_field_derivative,
            skew_symmetric_angular_rate,
        ),
    )

    # Compute SI, HI and Wb
    x = res["x"]
    lower_triangular_matrix = np.array(
        [[exp(x[0]), 0, 0], [x[1], exp(x[2]), 0], [x[3], x[4], 1 / exp(x[0] + x[2])]]
    )
    soft_iron = np.linalg.inv(lower_triangular_matrix @ lower_triangular_matrix.T)
    hard_iron = soft_iron @ x[5:8].reshape(3, 1)
    gyro_bias = x[8:].reshape(3, 1)

    # Calibrate magnetic field
    calibrated_magnetic_field = (
        np.linalg.inv(soft_iron)
        @ (magnetic_field.reshape(3, -1) - hard_iron.reshape(3, 1))
    ).T

    # Calibrated gyroscope measurements
    calibrated_angular_rate = angular_rate - gyro_bias.flatten()

    return (
        hard_iron.flatten(),
        soft_iron,
        gyro_bias.flatten(),
        calibrated_magnetic_field,
        calibrated_angular_rate,
    )


def cal_mag_magyc_bfg(
    magnetic_field: Union[np.ndarray, list],
    angular_rate: Union[np.ndarray, list],
    time: Union[np.ndarray, list],
    measurements_window: int = 25,
    optimizer: str = "dogleg",
    relative_error_tol: float = 1.00e-07,
    absolute_error_tol: float = 1.00e-07,
    max_iter: int = 1000,
) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    Dict[str, Union[List[float], int]],
]:
    """
    Proposed method for the full calibration of a three-axis magnetometer
    using magnetic field and angular rate measurements. This particular approach
    is based on a factor graph processing all the data in a batch manner.

    In particular MAGYC-BFG embeds the volume constraint for the soft-iron into
    a reparametrization for the Cholesky decomposition of the soft-iron matrix,
    allowing for the use of half the factors.


    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.
        angular_rate (numpy.ndarray or list): Angular rate measurements in a 3xN or
            Nx3 numpy array or list.
        time (numpy.ndarray or list): Time stamps of the measurements.
        measurements_window (int): Window size for the measurements.
        optimizer (str): Optimization algorithm to use. Options are "dogleg" or "lm"
            for the Dogleg and Levenberg-Marquardt optimizers respectively.
        relative_error_tol (float): Relative error tolerance for the optimizer. Default is 1.00e-07
        absolute_error_tol (float): Absolute error tolerance for the optimizer. Default is 1.00e-07
        max_iter (int): Maximum number of iterations for the optimizer. Default is 1000

    Returns:
        hard_iron (numpy.ndarray): Estimated hard-iron bias as a (3,) numpy array.
        soft_iron (numpy.ndarray): Estimated soft-iron matrix as a (3, 3) numpy array.
        gyro_bias (numpy.ndarray): Estimated gyroscope bias as a (3,) numpy array in rad/s.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements.
        calibrated_angular_rate (numpy.ndarray): Calibrated angular rate measurements in rad/s.
        optimization_status (Dict[str, Union[List[float], int]]): Dictionary with
            the optimization status. The keys are "error" and "iterations".

    Raises:
        TypeError: If the magnetic field, angular rate, and time are not numpy arrays or lists.
        ValueError: If the magnetic field and angular rate are not 3xN or Nx3 numpy
            arrays, or if the time is not a 1D numpy array.
        ValueError: If the optimizer is not a string or not "dogleg" or "lm"
        TypeError: If the relative error tolerance is not a float
        TypeError: If the absolute error tolerance is not a float
        ValueError: If the maximum number of iterations is not a positive integer
        ValueError: If the measurements window is not a positive integer
    """
    # Manage gtsam incompatibility with python >= 3.12
    try:
        import gtsam
    except ImportError:
        raise ImportError(
            "GTSAM is only available for Python ≤ 3.11. "
            "If you're on Python ≥ 3.12, please downgrade or install GTSAM manually."
        )

    # Check if the magnetic_field, angular_rate, and time are lists and convert them to numpy arrays
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)

    # Check if the magnetic_field, angular_rate, and time are numpy arrays
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")

    # Check if the magnetic_field and angular_rate are 3xN or Nx3 numpy arrays
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")

    # Check if the time is a 1D numpy array
    time = time.flatten()
    if time.ndim != 1:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force the magnetic_field and angular_rate to be Nx3 numpy arrays
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T
    if angular_rate.shape[0] == 3:
        angular_rate = angular_rate.T

    # Check if the magnetic_field, angular_rate, and time have the same number of samples
    if (
        magnetic_field.shape[0] != angular_rate.shape[0]
        or magnetic_field.shape[0] != time.shape[0]
    ):
        raise ValueError(
            "The magnetic field, angular rate, and time must have the same number of samples."
        )

    # Check that the optimizer is a string and is either "dogleg" or "lm"
    if not isinstance(optimizer, str) or optimizer not in ["dogleg", "lm"]:
        raise ValueError("The optimizer must be a string and either 'dogleg' or 'lm'.")

    # Check that the relative error tolerance is a float
    if not isinstance(relative_error_tol, float) or relative_error_tol <= 0:
        raise TypeError("The relative error tolerance must be a float.")

    # Check that the absolute error tolerance is a float
    if not isinstance(absolute_error_tol, float) or absolute_error_tol <= 0:
        raise TypeError("The absolute error tolerance must be a float.")

    # Check that the maximum number of iterations is a positive integer
    if not isinstance(max_iter, int) or max_iter <= 0:
        raise ValueError("The maximum number of iterations must be a positive integer.")

    # Check that the measurements window is a positive integer
    if not isinstance(measurements_window, int) or measurements_window <= 0:
        raise ValueError("The measurements window must be a positive integer.")

    # Compute the magnetic field derivative
    magnetic_field_derivative = np.diff(magnetic_field, axis=0) / np.diff(time).reshape(
        -1, 1
    )
    magnetic_field_derivative = np.concatenate(
        [np.zeros((1, 3)), magnetic_field_derivative], axis=0
    )

    # Compute the magnetic calibration
    # Smoothing and Mapping Factor Graph
    # 1. Create the non-linear graph
    graph = gtsam.NonlinearFactorGraph()

    # 2. noise model for each factor.
    residual_noise = gtsam.noiseModel.Isotropic.Sigma(3, 1e-6)

    # 3. Creates values structure with initial values
    initial = gtsam.Values()
    initial.insert(S(0), np.array([0.0, 0.0, 0.0, 0.0, 0.0]))
    initial.insert(B(0), gtsam.Point3(0, 0, 0))
    initial.insert(W(0), gtsam.Point3(0, 0, 0))
    keys = [S(0), B(0), W(0)]

    # 4. Add factor for each measurement accumulates in the measurements window into a single node
    measurements_window = int(measurements_window)
    m_dot_window = np.empty((measurements_window, 3))
    m_window = np.empty((measurements_window, 3))
    w_window = np.empty((measurements_window, 3))

    # 5. Add factors to the graph
    for i in range(magnetic_field.shape[0]):
        # Get sensor measurements and estimated magnetic field derivative
        m_dot_window[i % measurements_window, :] = magnetic_field_derivative[i, :]
        m_window[i % measurements_window, :] = magnetic_field[i, :]
        w_window[i % measurements_window, :] = angular_rate[i, :]

        if i % measurements_window == 0 and i != 0:
            # Average measurements by the measurements window size.
            m_dot_meadian = np.median(m_dot_window, axis=0).reshape(3, 1)
            m_median = np.median(m_window, axis=0).reshape(3, 1)
            w_median = np.median(w_window, axis=0).reshape(3, 1)

            # 5.1 Residual factor
            rf = gtsam.CustomFactor(
                residual_noise,
                keys,
                partial(
                    _cal_mag_magyc_residual_factor, m_dot_meadian, m_median, w_median
                ),
            )
            graph.push_back(rf)

            # 5.2 Reset the measurements window
            m_dot_window = np.empty((measurements_window, 3))
            m_window = np.empty((measurements_window, 3))
            w_window = np.empty((measurements_window, 3))

    # 6. Optimize the graph
    # 6.1 Create optimizer parameters
    params = (
        gtsam.DoglegParams()
        if optimizer == "dogleg"
        else gtsam.LevenbergMarquardtParams()
    )
    params.setRelativeErrorTol(relative_error_tol)
    params.setAbsoluteErrorTol(absolute_error_tol)
    params.setMaxIterations(max_iter)
    params.setLinearSolverType("MULTIFRONTAL_CHOLESKY")

    # For dogleg method set the trust region. For good estimations, it ranges between 0.1 and 1.0
    if optimizer == "dogleg":
        params.setDeltaInitial(0.5)

    # 6.2 Create optimizer
    if optimizer == "dogleg":
        optimizer = gtsam.DoglegOptimizer(graph, initial, params)
    else:
        optimizer = gtsam.LevenbergMarquardtOptimizer(graph, initial, params)

    # 6.3 Optimize
    result, optimization_status = _cal_mag_magyc_gtsam_optimize(optimizer, params)

    # 7. Process Results
    l_params = result.atVector(S(0))
    b = result.atVector(B(0))
    d = result.atVector(W(0))

    lower_triangular_matrix = np.array(
        [
            [exp(l_params[0]), 0, 0],
            [l_params[1], exp(l_params[2]), 0],
            [l_params[3], l_params[4], 1 / exp(l_params[0] + l_params[2])],
        ]
    )
    soft_iron = np.linalg.inv(lower_triangular_matrix @ lower_triangular_matrix.T)
    hard_iron = soft_iron @ np.vstack(b)
    gyro_bias = np.vstack(d)

    # Calibrate magnetic field
    calibrated_magnetic_field = (
        np.linalg.inv(soft_iron)
        @ (magnetic_field.reshape(3, -1) - hard_iron.reshape(3, 1))
    ).T

    # Calibrated gyroscope measurements
    calibrated_angular_rate = angular_rate - gyro_bias.flatten()

    return (
        hard_iron.flatten(),
        soft_iron,
        gyro_bias.flatten(),
        calibrated_magnetic_field,
        calibrated_angular_rate,
        optimization_status,
    )


def cal_mag_magyc_ifg(
    magnetic_field: Union[np.ndarray, list],
    angular_rate: Union[np.ndarray, list],
    time: Union[np.ndarray, list],
    measurements_window: int = 25,
) -> Tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, np.ndarray]
]:
    """
    Proposed method for the full calibration of a three-axis magnetometer
    using magnetic field and angular rate measurements. This particular approach
    is based on a factor graph processing all the data in an incremental manner.

    In particular MAGYC-IFG embeds the volume constraint for the soft-iron into
    a reparametrization for the Cholesky decomposition of the soft-iron matrix,
    allowing for the use of half the factors.

    Args:
        magnetic_field (numpy.ndarray or list): Magnetic field measurements in a
            3xN or Nx3 numpy array or list.
        angular_rate (numpy.ndarray or list): Angular rate measurements in a 3xN or
            Nx3 numpy array or list.
        time (numpy.ndarray or list): Time stamps of the measurements.
        measurements_window (int): Window size for the measurements.

    Returns:
        hard_iron (numpy.ndarray): Estimated hard-iron bias as a (3,) numpy array.
        soft_iron (numpy.ndarray): Estimated soft-iron matrix as a (3, 3) numpy array.
        gyro_bias (numpy.ndarray): Estimated gyroscope bias as a (3,) numpy array in rad/s.
        calibrated_magnetic_field (numpy.ndarray): Calibrated magnetic field measurements.
        calibrated_angular_rate (numpy.ndarray): Calibrated angular rate measurements in rad/s.
        optimization_status (Dict[str, np.ndarray]): Dictionary with the SI, HI
            and Wb for each iterations. The keys are: "soft_iron", "hard_iron",
            "gyro_bias", and "time".

    Raises:
        TypeError: If the magnetic field, angular rate, and time are not numpy arrays or lists.
        ValueError: If the magnetic field and angular rate are not 3xN or Nx3 numpy
            arrays, or if the time is not a 1D numpy array.
        ValueError: If the measurements window is not a positive integer
    """
    # Manage gtsam incompatibility with python >= 3.12
    try:
        import gtsam
    except ImportError:
        raise ImportError(
            "GTSAM is only available for Python ≤ 3.11. "
            "If you're on Python ≥ 3.12, please downgrade or install GTSAM manually."
        )

    # Check if the magnetic_field, angular_rate, and time are lists and convert them to numpy arrays
    if isinstance(magnetic_field, list):
        magnetic_field = np.array(magnetic_field)
    if isinstance(angular_rate, list):
        angular_rate = np.array(angular_rate)
    if isinstance(time, list):
        time = np.array(time)

    # Check if the magnetic_field, angular_rate, and time are numpy arrays
    if not isinstance(magnetic_field, np.ndarray):
        raise TypeError("The magnetic field must be a numpy array or a list.")
    if not isinstance(angular_rate, np.ndarray):
        raise TypeError("The angular rate must be a numpy array or a list.")
    if not isinstance(time, np.ndarray):
        raise TypeError("The time must be a numpy array or a list.")

    # Check if the magnetic_field and angular_rate are 3xN or Nx3 numpy arrays
    if magnetic_field.ndim != 2 or (
        magnetic_field.shape[0] != 3 and magnetic_field.shape[1] != 3
    ):
        raise ValueError("The magnetic field must be a 3xN or Nx3 numpy array.")
    if angular_rate.ndim != 2 or (
        angular_rate.shape[0] != 3 and angular_rate.shape[1] != 3
    ):
        raise ValueError("The angular rate must be a 3xN or Nx3 numpy array.")

    # Check if the time is a 1D numpy array
    time = time.flatten()
    if time.ndim != 1:
        raise ValueError("The time must be a (n, ), (n, 1) or (1, n) numpy array.")

    # Force the magnetic_field and angular_rate to be Nx3 numpy arrays
    if magnetic_field.shape[0] == 3:
        magnetic_field = magnetic_field.T
    if angular_rate.shape[0] == 3:
        angular_rate = angular_rate.T

    # Check if the magnetic_field, angular_rate, and time have the same number of samples
    if (
        magnetic_field.shape[0] != angular_rate.shape[0]
        or magnetic_field.shape[0] != time.shape[0]
    ):
        raise ValueError(
            "The magnetic field, angular rate, and time must have the same number of samples."
        )

    # Check that the measurements window is a positive integer
    if not isinstance(measurements_window, int) or measurements_window <= 0:
        raise ValueError("The measurements window must be a positive integer.")

    # Compute the magnetic calibration
    # Smoothing and Mapping Factor Graph
    # 1. Create the non-linear graph
    graph = gtsam.NonlinearFactorGraph()

    # 2. Set iSAM2 parameters and create iSAM2 object
    isam_parameters = gtsam.ISAM2Params()
    dogleg_parameters = gtsam.ISAM2DoglegParams()
    dogleg_parameters.setInitialDelta(0.5)
    dogleg_parameters.setAdaptationMode("ONE_STEP_PER_ITERATION")
    isam_parameters.setOptimizationParams(dogleg_parameters)
    isam = gtsam.ISAM2(isam_parameters)

    # 3. noise model for each factor.
    residual_noise = gtsam.noiseModel.Isotropic.Sigma(3, 1e-6)

    # 4. Creates values structure with initial values
    initial = gtsam.Values()
    initial.insert(S(0), np.array([0.0, 0.0, 0.0, 0.0, 0.0]))
    initial.insert(B(0), gtsam.Point3(0, 0, 0))
    initial.insert(W(0), gtsam.Point3(0, 0, 0))
    keys = [S(0), B(0), W(0)]

    # Dictionary to save the progress of parameters during optimization
    optimization_status = {"S": [], "B": [], "W": [], "T": []}

    # 5. Add factor for each measurement accumulates in the measurements window into a single node
    measurements_window = int(measurements_window)
    m_window = np.empty((measurements_window, 3))
    w_window = np.empty((measurements_window, 3))
    t_window = np.empty((measurements_window,))

    # 6. Add factors to the graph
    for i in range(magnetic_field.shape[0]):
        # Get sensor measurements and estimated magnetic field derivative
        t_window[i % measurements_window] = time[i]
        m_window[i % measurements_window, :] = magnetic_field[i, :]
        w_window[i % measurements_window, :] = angular_rate[i, :]

        if i % measurements_window == 0 and i != 0:
            # Compute the derivative of the magnetic field for the window
            m_dot_window = np.diff(m_window, axis=0) / np.diff(t_window).reshape(-1, 1)

            # Average measurements by the measurements window size.
            m_dot_meadian = np.median(m_dot_window, axis=0).reshape(3, 1)
            m_median = np.median(m_window, axis=0).reshape(3, 1)
            w_median = np.median(w_window, axis=0).reshape(3, 1)

            # 6.1 Residual factor
            rf = gtsam.CustomFactor(
                residual_noise,
                keys,
                partial(
                    _cal_mag_magyc_residual_factor, m_dot_meadian, m_median, w_median
                ),
            )
            graph.push_back(rf)

            # 6.2 Perform incremental update to iSAM2's internal Bayes tree, optimizing only the affected variables.
            # Set iterations to start optimization, otherwise the optimizations starts as a ill-posed problem.
            # CHECK: If the measurement window is set to small values, the optimiaztion will raise RuntimeError
            # try:
            if (i // measurements_window) % 10 == 0:
                isam.update(graph, initial)
                current = isam.calculateEstimate()

                # Save the current parameters
                for key, variable in zip([S(0), B(0), W(0)], "SBW"):
                    vector = current.atVector(key).reshape(1, -1)
                    optimization_status[variable].append(vector)
                # Save the time as a unix timestamp in microseconds
                optimization_status["T"].append(int(datetime.now().timestamp() * 1e6))

                # except RuntimeError:
                #     warnings.warn("Skipping graph optimization due to indetermined system.")
                # finally:
                graph = gtsam.NonlinearFactorGraph()
                initial = gtsam.Values()

            # 6.5 Reset the measurements window
            t_window = np.empty((measurements_window,))
            m_window = np.empty((measurements_window, 3))
            w_window = np.empty((measurements_window, 3))

    # 7. Process Results
    # Update optimization status to have the actual matrices instead of the keys
    optimization_steps = len(optimization_status["S"])
    optimization_status_final = {
        "soft_iron": np.empty((optimization_steps, 9)),
        "hard_iron": np.empty((optimization_steps, 3)),
        "gyro_bias": np.empty((optimization_steps, 3)),
        "time": np.empty((optimization_steps,)),
    }

    for i in range(optimization_steps):
        # Get parameters
        l_params = optimization_status["S"][i].flatten()
        b = optimization_status["B"][i]
        d = optimization_status["W"][i]

        # Compute soft-iron, hard-iron and gyroscope bias
        lower_triangular_matrix = np.array(
            [
                [exp(l_params[0]), 0, 0],
                [l_params[1], exp(l_params[2]), 0],
                [l_params[3], l_params[4], 1 / exp(l_params[0] + l_params[2])],
            ]
        )
        soft_iron_i = np.linalg.inv(lower_triangular_matrix @ lower_triangular_matrix.T)
        hard_iron_i = soft_iron_i @ b.reshape(3, 1)
        gyro_bias_i = d.reshape(3, 1)

        # Fill the new optimization status dictionary
        optimization_status_final["soft_iron"][i, :] = soft_iron_i.flatten()
        optimization_status_final["hard_iron"][i, :] = hard_iron_i.flatten()
        optimization_status_final["gyro_bias"][i, :] = gyro_bias_i.flatten()
        optimization_status_final["time"][i] = optimization_status["T"][i]

    # Average the last 20% of the optimization steps to get the final calibration
    optimization_steps = int(0.2 * optimization_steps)
    soft_iron = np.mean(
        optimization_status_final["soft_iron"][-optimization_steps:], axis=0
    ).reshape(3, 3)
    hard_iron = np.mean(
        optimization_status_final["hard_iron"][-optimization_steps:], axis=0
    )
    gyro_bias = np.mean(
        optimization_status_final["gyro_bias"][-optimization_steps:], axis=0
    )

    # Calibrate magnetic field
    calibrated_magnetic_field = (
        np.linalg.inv(soft_iron)
        @ (magnetic_field.reshape(3, -1) - hard_iron.reshape(3, 1))
    ).T

    # Calibrated gyroscope measurements
    calibrated_angular_rate = angular_rate - gyro_bias.flatten()

    return (
        hard_iron.flatten(),
        soft_iron,
        gyro_bias.flatten(),
        calibrated_magnetic_field,
        calibrated_angular_rate,
        optimization_status_final,
    )


def _cal_mag_magyc_vec_to_so3_jax(vec):
    """
    Convert a 3D vector to a skew-symmetric matrix.

    Args:
        vec (np.ndarray): A 3D vector.

    Returns:
        np.ndarray: A 3x3 skew-symmetric matrix.
    """
    return npj.array([[0, -vec[2], vec[1]], [vec[2], 0, -vec[0]], [-vec[1], vec[0], 0]])


def _cal_mag_magyc_ls_cost_function(
    x: np.ndarray,
    magnetic_field: np.ndarray,
    magnetic_field_derivative: np.ndarray,
    skew_symmetric_angular_rate: np.ndarray,
) -> np.ndarray:
    """
    Function which computes the vector of residuals, and the minimization
    proceeds with respect to x for the MAGYC-LS method.

    Args:
        x (np.ndarray): Optimization variables as a (9, ) numpy array.
        magnetic_field (np.ndarray): Magnetic field as a (n, 3) numpy array.
        magnetic_field_derivative (np.ndarray): Magnetic field derivative as a
            (n, 3) numpy array.
        skew_symmetric_angular_rate (np.ndarray): Skew symmetric matrix of the
            angular rate as a (n, 3, 3) numpy array.

    Returns:
        ssr (np.ndarray): Vector of residuals for the optimization as a (9, ) numpy array.
    """
    # Compute C (SI**-1) and HI
    lower_triangular_matrix = npj.array(
        [[expj(x[0]), 0, 0], [x[1], expj(x[2]), 0], [x[3], x[4], 1 / expj(x[0] + x[2])]]
    )
    soft_iron_inv = lower_triangular_matrix @ lower_triangular_matrix.T
    mb = x[5:].reshape(3, 1)

    # Cost function
    sensor_model = (
        (soft_iron_inv @ magnetic_field_derivative)
        + (skew_symmetric_angular_rate @ soft_iron_inv @ magnetic_field)
        - (skew_symmetric_angular_rate @ mb)
    )

    # Residuals vector
    residuals_vector = (npj.linalg.norm(sensor_model.reshape(-1, 3), axis=1)).flatten()
    return residuals_vector


def _cal_mag_magyc_nls_cost_function(
    x: np.ndarray,
    magnetic_field: np.ndarray,
    magnetic_field_derivative: np.ndarray,
    skew_symmetric_angular_rate: np.ndarray,
) -> np.ndarray:
    """
    Function which computes the vector of residuals, and the minimization
    proceeds with respect to x for the MAGYC-NLS method.

    Args:
        x (np.ndarray): Optimization variables as a (9, ) numpy array.
        magnetic_field (np.ndarray): Magnetic field as a (n, 3) numpy array.
        magnetic_field_derivative (np.ndarray): Magnetic field derivative as a
            (n, 3) numpy array.
        skew_symmetric_angular_rate (np.ndarray): Skew symmetric matrix of the
            angular rate as a (n, 3, 3) numpy array.

    Returns:
        ssr (np.ndarray): Vector of residuals for the optimization as a (9, ) numpy array.
    """
    # Compute C (SI**-1), HI and Wb
    lower_triangular_matrix = npj.array(
        [[expj(x[0]), 0, 0], [x[1], expj(x[2]), 0], [x[3], x[4], 1 / expj(x[0] + x[2])]]
    )
    soft_iron_inv = lower_triangular_matrix @ lower_triangular_matrix.T
    mb = x[5:8].reshape(3, 1)
    wb = x[8:]

    # Compute skew symetric for wb
    skew_symmetric_wb = npj.array(
        [[0, -wb[2], wb[1]], [wb[2], 0, -wb[0]], [-wb[1], wb[0], 0]]
    )

    # Cost function
    sensor_model = (
        (soft_iron_inv @ magnetic_field_derivative)
        + (skew_symmetric_angular_rate @ soft_iron_inv @ magnetic_field)
        - (skew_symmetric_angular_rate @ mb)
        - (skew_symmetric_wb @ soft_iron_inv @ magnetic_field)
        + (skew_symmetric_wb @ mb)
    )

    # Residual Vector
    residual_vector = (npj.linalg.norm(sensor_model.reshape(-1, 3), axis=1)).flatten()
    return residual_vector


# Use JAX to compute the Jacobian of the cost functions for the least square methods
_cal_mag_magyc_nls_jacobian = jacfwd(_cal_mag_magyc_nls_cost_function)
_cal_mag_magyc_ls_jacobian = jacfwd(_cal_mag_magyc_ls_cost_function)

# JIT compile the cost function and Jacobian for performance
_cal_mag_magyc_nls_cost_function = jit(_cal_mag_magyc_nls_cost_function)
_cal_mag_magyc_ls_cost_function = jit(_cal_mag_magyc_ls_cost_function)
_cal_mag_magyc_nls_jacobian = jit(_cal_mag_magyc_nls_jacobian)
_cal_mag_magyc_ls_jacobian = jit(_cal_mag_magyc_ls_jacobian)


def _cal_mag_magyc_compute_jacobian_nls_jax(
    x: np.ndarray,
    magnetic_field: np.ndarray,
    magnetic_field_derivative: np.ndarray,
    skew_symmetric_angular_rate: np.ndarray,
) -> np.ndarray:
    return _cal_mag_magyc_nls_jacobian(
        x, magnetic_field, magnetic_field_derivative, skew_symmetric_angular_rate
    )


def _cal_mag_magyc_compute_jacobian_ls_jax(
    x: np.ndarray,
    magnetic_field: np.ndarray,
    magnetic_field_derivative: np.ndarray,
    skew_symmetric_angular_rate: np.ndarray,
) -> np.ndarray:
    return _cal_mag_magyc_ls_jacobian(
        x, magnetic_field, magnetic_field_derivative, skew_symmetric_angular_rate
    )


def _cal_mag_magyc_residual_factor(
    m_dot: np.ndarray,
    m: np.ndarray,
    g: np.ndarray,
    this: "gtsam.CustomFactor",
    v: "gtsam.Values",
    H: Optional[List[np.ndarray]],
) -> np.ndarray:
    """
    Unary factor for the residual of the system model:

    $$R_i = [w_i(t)]A^{-1}m_i(t) - [d]A^{-1}m_i(t) + A^{-1}\\dot{m}_i(t) - [w_i(t)]b + [d]b $$

    Where, $m_i(t) \\; \\in \\; \\mathbb{R}^3$ is the magnetic field measurement,
    $\\dot{m}_i(t) \\; \\in \\; \\mathbb{R}^3$ is the differentiation with respect
    to the time of the magnetic field measurement, $[w_i(t)] \\; \\in \\; \\mathbb{R}^{3\\times 3}$
    is the skew-symmetric matrix of the gyroscope measurements, $A \\; \\in \\; \\mathbb{R}^{3\\times 3}$
    is the soft-iron, $[d] \\; \\in \\; \\mathbb{R}^{3\\times 3}$
    is the skew-symmetric matrix of the gyroscope bias, and $b \\; \\in \\; \\mathbb{R}^3$
    is the hard-iron.

    The soft-iron is parameterized based on the Cholesky decomposition $A = LL^T$,
    where $L \\; \\in \\; \\mathbb{R}^{3\\times 3}$ is a lower triangular matrix,
    which is parameterized as:

    $$ \\begin{bmatrix}
            \\exp(l_0) & 0 & 0 \\\\
            l_1 & \\exp(l_2) & 0 \\\\
            l_3 & l_4 & 1/\\exp(l_0 + l_2)
        \\end{bmatrix}
    $$

    Args:
        m_dot (np.ndarray): Derivative of the magnetic field measurement in G/s as a (3, 1)
            numpy array.
        m (np.ndarray): Magnetic field measurements in G as a (3, 1) numpy array.
        g (np.ndarray): Gyroscope measurement in rad/s as a (3, 1) numpy array.
        this (gtsam.CustomFactor): Reference to the current CustomFactor being evaluated.
        v (gtsam.Values): A values structure that maps from keys to values.
        H (List[np.ndarray], Optional): List of references to the Jacobian arrays.

    Returns:
        error (np.ndarray): The non-linear residual error as a gtsam factor.
    """
    key1, key2, key3 = this.keys()[0], this.keys()[1], this.keys()[2]
    l, b, d = v.atVector(key1), v.atVector(key2), v.atVector(key3)

    # Convert state into single variables
    l_matrix = np.array(
        [
            [exp(l[0]), 0.0, 0.0],
            [l[1], exp(l[2]), 0.0],
            [l[3], l[4], 1 / exp(l[0] + l[2])],
        ]
    )

    # Get measurements
    m0, m1, m2, n0, n1, n2 = (
        m[0, 0],
        m[1, 0],
        m[2, 0],
        m_dot[0, 0],
        m_dot[1, 0],
        m_dot[2, 0],
    )
    w0, w1, w2 = g[0, 0], g[1, 0], g[2, 0]
    l0, l1, l2, l3, l4 = l[0], l[1], l[2], l[3], l[4]
    b0, b1, b2, d0, d1, d2 = b[0], b[1], b[2], d[0], d[1], d[2]

    # Jacobian construction
    # Residual Jacibian with respect to the li components
    j1 = np.zeros((3, 5))
    j1[0, 0] = (
        l1 * m0 * (d2 - w2) * exp(l0)
        + l1 * n1 * exp(l0)
        + l3 * n2 * exp(l0)
        + 2 * n0 * exp(2 * l0)
        + (-d1 + w1) * (l3 * m0 * exp(l0) - 2 * m2 * exp(-2 * l0 - 2 * l2))
    )
    j1[1, 0] = (
        l1 * n0 * exp(l0)
        + (d0 - w0) * (l3 * m0 * exp(l0) - 2 * m2 * exp(-2 * l0 - 2 * l2))
        + (-d2 + w2) * (l1 * m1 * exp(l0) + l3 * m2 * exp(l0) + 2 * m0 * exp(2 * l0))
    )
    j1[2, 0] = (
        l1 * m0 * (-d0 + w0) * exp(l0)
        + l3 * n0 * exp(l0)
        - 2 * n2 * exp(-2 * l0 - 2 * l2)
        + (d1 - w1) * (l1 * m1 * exp(l0) + l3 * m2 * exp(l0) + 2 * m0 * exp(2 * l0))
    )
    j1[0, 1] = (
        l3 * m1 * (-d1 + w1)
        + n1 * exp(l0)
        + (d2 - w2) * (2 * l1 * m1 + l3 * m2 + m0 * exp(l0))
    )
    j1[1, 1] = (
        2 * l1 * n1
        + l3 * m1 * (d0 - w0)
        + l3 * n2
        + m1 * (-d2 + w2) * exp(l0)
        + n0 * exp(l0)
    )
    j1[2, 1] = (
        l3 * n1
        + m1 * (d1 - w1) * exp(l0)
        + (-d0 + w0) * (2 * l1 * m1 + l3 * m2 + m0 * exp(l0))
    )
    j1[0, 2] = (-d1 + w1) * (l4 * m1 * exp(l2) - 2 * m2 * exp(-2 * l0 - 2 * l2)) + (
        d2 - w2
    ) * (l4 * m2 * exp(l2) + 2 * m1 * exp(2 * l2))
    j1[1, 2] = (
        l4 * n2 * exp(l2)
        + 2 * n1 * exp(2 * l2)
        + (d0 - w0) * (l4 * m1 * exp(l2) - 2 * m2 * exp(-2 * l0 - 2 * l2))
    )
    j1[2, 2] = (
        l4 * n1 * exp(l2)
        - 2 * n2 * exp(-2 * l0 - 2 * l2)
        + (-d0 + w0) * (l4 * m2 * exp(l2) + 2 * m1 * exp(2 * l2))
    )
    j1[0, 3] = (
        l1 * m2 * (d2 - w2)
        + n2 * exp(l0)
        + (-d1 + w1) * (l1 * m1 + 2 * l3 * m2 + m0 * exp(l0))
    )
    j1[1, 3] = (
        l1 * n2
        + m2 * (-d2 + w2) * exp(l0)
        + (d0 - w0) * (l1 * m1 + 2 * l3 * m2 + m0 * exp(l0))
    )
    j1[2, 3] = (
        l1 * m2 * (-d0 + w0)
        + l1 * n1
        + 2 * l3 * n2
        + m2 * (d1 - w1) * exp(l0)
        + n0 * exp(l0)
    )
    j1[0, 4] = m2 * (d2 - w2) * exp(l2) + (-d1 + w1) * (2 * l4 * m2 + m1 * exp(l2))
    j1[1, 4] = n2 * exp(l2) + (d0 - w0) * (2 * l4 * m2 + m1 * exp(l2))
    j1[2, 4] = 2 * l4 * n2 + m2 * (-d0 + w0) * exp(l2) + n1 * exp(l2)

    # Residual Jacibian with respect to the b components
    j2 = np.zeros((3, 3))
    j2[0, 0] = 0
    j2[1, 0] = d2 - w2
    j2[2, 0] = -d1 + w1
    j2[0, 1] = -d2 + w2
    j2[1, 1] = 0
    j2[2, 1] = d0 - w0
    j2[0, 2] = d2 - w2
    j2[1, 2] = -d1 + w1
    j2[2, 2] = 0

    # Residual Jacibian with respect to the d components
    j3 = np.zeros((3, 3))
    j3[0, 0] = 0
    j3[1, 0] = (
        -b2
        + l3 * m0 * exp(l0)
        + m1 * (l1 * l3 + l4 * exp(l2))
        + m2 * (l3**2 + l4**2 + exp(-2 * l0 - 2 * l2))
    )
    j3[2, 0] = (
        b1
        - l1 * m0 * exp(l0)
        - m1 * (l1**2 + exp(2 * l2))
        - m2 * (l1 * l3 + l4 * exp(l2))
    )
    j3[0, 1] = (
        b2
        - l3 * m0 * exp(l0)
        - m1 * (l1 * l3 + l4 * exp(l2))
        - m2 * (l3**2 + l4**2 + exp(-2 * l0 - 2 * l2))
    )
    j3[1, 1] = 0
    j3[2, 1] = -b0 + l1 * m1 * exp(l0) + l3 * m2 * exp(l0) + m0 * exp(2 * l0)
    j3[0, 2] = (
        -b1
        + l1 * m0 * exp(l0)
        + m1 * (l1**2 + exp(2 * l2))
        + m2 * (l1 * l3 + l4 * exp(l2))
    )
    j3[1, 2] = b0 - l1 * m1 * exp(l0) - l3 * m2 * exp(l0) - m0 * exp(2 * l0)
    j3[2, 2] = 0

    if H is not None:
        H[0] = j1
        H[1] = j2
        H[2] = j3

    # Cost Function
    c_matrix = l_matrix @ l_matrix.T
    error = (
        vec_to_so3(g.flatten() - d) @ (c_matrix @ m - np.vstack(b)) + c_matrix @ m_dot
    )
    return error


def _cal_mag_magyc_gtsam_optimize(
    optimizer: Union["gtsam.LevenbergMarquardtOptimizer", "gtsam.DoglegOptimizer"],
    optimizer_params: Union["gtsam.LevenbergMarquardtParams", "gtsam.DoglegParams"],
) -> Tuple["gtsam.Values", Dict[str, Union[List[float], int]]]:
    """
    Wrapper for the batch optimization of the non-linear graph with a callback to
    store the optimization error and check the termination conditions.

    Args:
        optimizer (Union[gtsam.LevenbergMarquardtParams, gtsam.DoglegParams]): Optimizer parameters.
        optimizer_params (Union[gtsam.LevenbergMarquardtParams, gtsam.DoglegParams]): Optimizer parameters.

    Returns:
        gtsam.Values: The state value in each node as a gtsam.Values structure.
        optimization_status (Dict[str, Union[List[float], int]]): Dictionary with
            the optimization status. The keys are "error" and "iterations".
    """
    error_before = optimizer.error()
    optimization_status = {"error": [error_before], "iterations": 0}

    while True:
        # Optimize
        optimizer.iterate()
        error_after = optimizer.error()

        # Store errors
        optimization_status["error"].append(error_after)

        # Check termination condition
        # Condition 1: Maximum number of iterations
        condition_1 = optimizer.iterations() >= optimizer_params.getMaxIterations()

        # Condition 2: Convergence
        condition_2 = gtsam.checkConvergence(
            optimizer_params.getRelativeErrorTol(),
            optimizer_params.getAbsoluteErrorTol(),
            optimizer_params.getErrorTol(),
            error_before,
            error_after,
        )

        # Condition 3: Reach upper bound of lambda
        condition_3 = (
            isinstance(optimizer, gtsam.LevenbergMarquardtOptimizer)
            and optimizer.lambda_() > optimizer_params.getlambdaUpperBound()
        )

        if condition_1 or condition_2 or condition_3:
            optimization_status["iterations"] = optimizer.iterations()
            return optimizer.values(), optimization_status

        error_before = error_after
