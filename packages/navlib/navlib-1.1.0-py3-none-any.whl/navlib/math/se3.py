"""
This module provides functions to work with the Special Euclidean Group SE(3).

Functions:
    xyzrph2matrix: Takes the pose as xyzrph and computes the corresponding
        transformation matrix.
    matrix2xyzrph: Computes the pose xyzrph from a transformation matrix.
    matrix_inverse: Compute the inverse of a transformation matrix.
    pose_diff: Compute the relative transformation between two poses.
    adjoint: Computes the adjoint representation of a transformation matrix.
    vec_to_se3: Converts a spacial velocity vector (spatial twist) into a (4, 4)
        matrix in se(3).
    se3_to_vec: Convert a se(3) (4, 4) matrix into a spatial velocity vector
        (spatial twist) in R6.
    axis_ang6: Convert the exponential coordinates of a homogeneous transformation
        S*theta to a screw axis-angle form.
    matrix_exp6: Computes the matrix exponential of an se(3) representation of
        exponential coordinates of a homogeneous transformation.
    matrix_log6: Compute the logarithm of a homogeneous transformation matrix in SE(3).
    project_to_SE3: Projects a matrix to the closest matrix in SE(3) using singular
        value decomposition.
    distance_to_SE3: Compute the frobenius norm to describe the distance of a matrix
        from the SE(3) manifold.

Authors: Sebastián Rodríguez-Martínez
Contact: srodriguez@mbari.org
"""
import math
from typing import Iterable, Tuple, Union

import numpy as np

from navlib.math.so3 import (
    axis_ang3,
    matrix_exp3,
    matrix_log3,
    project_to_so3,
    so3_to_vec,
    vec_to_so3,
)


def xyzrph2matrix(xyzrph: Union[Iterable[float], np.ndarray]) -> np.ndarray:
    """
    Takes the pose as xyzrph and computes the corresponding transformation
    matrix.

    Args:
        xyzrph (Union[Iterable[float], np.ndarray]): Pose as xyzrph.

    Returns:
        np.ndarray: Transformation matrix of the pose.

    Raises:
        ValueError: If the pose is not a numpy array or a list.
        ValueError: If the pose does not have 6 elements.

    Examples:
        >>> xyzrph = [1, 2, 3, 0.3, 0.2, 0.1]
        >>> t_mat = xyzrph2matrix(xyzrph)
        >>> print(t_mat)
        [[ 0.93629336 -0.27509585  0.21835066  1.0]
         [ 0.28962948  0.95642509 -0.03695701  2.0]
         [-0.19866933  0.0978434   0.97517033  3.0]
         [ 0.          0.          0.          1.0]]
    """
    if not isinstance(xyzrph, np.ndarray) and not isinstance(xyzrph, list):
        raise ValueError("Usage: The pose must be a numpy array or a list")

    xyzrph = (
        np.array(xyzrph).flatten() if isinstance(xyzrph, list) else xyzrph.flatten()
    )

    if xyzrph.shape[0] != 6:
        raise ValueError("Usage: The pose must have 6 elements")

    c1 = np.cos(xyzrph[5])
    s1 = np.sin(xyzrph[5])
    c2 = np.cos(xyzrph[4])
    s2 = np.sin(xyzrph[4])
    c3 = np.cos(xyzrph[3])
    s3 = np.sin(xyzrph[3])
    px = xyzrph[0]
    py = xyzrph[1]
    pz = xyzrph[2]
    transformation_matrix = np.array(
        [
            [c1 * c2, c1 * s2 * s3 - c3 * s1, s1 * s3 + c1 * c3 * s2, px],
            [c2 * s1, c1 * c3 + s1 * s2 * s3, c3 * s1 * s2 - c1 * s3, py],
            [-s2, c2 * s3, c2 * c3, pz],
            [0, 0, 0, 1],
        ]
    )

    return transformation_matrix


def matrix2xyzrph(T: np.ndarray) -> np.ndarray:
    """
    Computes the pose xyzrph from a transformation matrix.

    Args:
        T (np.ndarray) : Transformation matrix as a (4, 4) numpy array.

    Returns:
        xyzrph (np.ndarray): xyzrph pose from the body as a numpy array.

    Raises:
        ValueError: If the transformation matrix is not a numpy array.
        ValueError: If the transformation matrix does not have shape (4, 4).

    Examples:
        >>> T = np.array([[0.93629336, -0.27509585, 0.21835066, 1.0],
        ...               [0.28962948, 0.95642509, -0.03695701, 2.0],
        ...               [-0.19866933, 0.0978434, 0.97517033, 3.0],
        ...               [0.0, 0.0, 0.0, 1.0]])
        >>> xyzrph = matrix2xyzrph(T)
        >>> print(xyzrph)
        [1. 2. 3. 0.3 0.2 0.1]
    """
    if not isinstance(T, np.ndarray):
        raise ValueError("Usage: The transformation matrix must be a numpy array")

    if T.shape != (4, 4):
        raise ValueError("Usage: The transformation matrix must have shape (4, 4)")

    x = T[0, 3]
    y = T[1, 3]
    z = T[2, 3]
    h = math.atan2(T[1, 0], T[0, 0])
    p = math.atan2(-T[2, 0], math.sqrt(math.pow(T[2, 1], 2) + math.pow(T[2, 2], 2)))
    r = math.atan2(T[2, 1], T[2, 2])
    xyzrph = np.array([x, y, z, r, p, h])

    return xyzrph


def matrix_inverse(T: np.ndarray) -> np.ndarray:
    """
    Compute the inverse of a transformation matrix.

    Args:
        T (np.ndarray): Transformation matrix as a (4, 4) numpy array

    Returns:
        Tinv (np.ndarray): Inverse transformation matrix of T as a numpy array.

    Raises:
        ValueError: If the matrix is not a numpy array.
        ValueError: If the matrix does not have shape (4, 4).

    Examples:
        >>> T = np.array([[0.93629336, -0.27509585, 0.21835066, 1.0],
        ...               [0.28962948, 0.95642509, -0.03695701, 2.0],
        ...               [-0.19866933, 0.0978434, 0.97517033, 3.0],
        ...               [0.0, 0.0, 0.0, 1.0]])
        >>> Tinv = transformation_matrix_inverse(T)
        >>> print(Tinv)
        [[ 0.93629336  0.28962948 -0.19866933 -0.9800295 ]
         [-0.27509585  0.95642509  0.0978434   0.0197317 ]
         [ 0.21835066 -0.03695701  0.97517033 -2.80454357]
         [ 0.          0.          0.          1.        ]]
    """
    if not isinstance(T, np.ndarray):
        raise ValueError("Type Error: The matrix must be a numpy array.")

    if T.shape != (4, 4):
        raise ValueError("Shape Error: The matrix must be a (4, 4) numpy array.")

    Tinv = np.eye(4, dtype=np.float64)
    Tinv[:3, :3] = np.einsum("ij -> ji", T[0:3, 0:3])
    Tinv[:3, 3] = -(np.einsum("ij -> ji", T[0:3, 0:3]) @ T[0:3, 3])
    return Tinv


def pose_diff(t1: np.ndarray, t2: np.ndarray) -> np.ndarray:
    """
    Compute the relative transformation between two poses. The returned matrix
    is the pose of 2 with respect to 1:

    T_12 = T_1w @ T_w2 = inv(T_w1) @ T_w2

    Args:
        t1 (np.ndarray): Transformation matrix for pose 1 as a numpy array.
        t2 (np.ndarray): Transformation matrix for pose 2 as a numpy array.

    Returns:
        t12 (np.ndarray): The pose of 2 with respect to 1 as a numpy array.

    Raises:
        ValueError: If the matrices are not numpy arrays.
        ValueError: If the matrices do not have shape (4, 4).

    Examples:
        >>> t1 = np.array([[0.93629336, -0.27509585, 0.21835066, 1.0],
        ...                 [0.28962948, 0.95642509, -0.03695701, 2.0],
        ...                 [-0.19866933, 0.0978434, 0.97517033, 3.0],
        ...                 [0.0, 0.0, 0.0, 1.0]])
        >>> t2 = np.array([[0.93629336, -0.27509585, 0.21835066, 1.0],
        ...                 [0.28962948, 0.95642509, -0.03695701, 2.0],
        ...                 [-0.19866933, 0.0978434, 0.97517033, 3.0],
        ...                 [0.0, 0.0, 0.0, 1.0]])
        >>> t12 = poseDiff(t1, t2)
        >>> print(t12)
        [[ 1.00000000e+00 -1.11022302e-16  0.00000000e+00  0.00000000e+00]
         [ 1.11022302e-16  1.00000000e+00  0.00000000e+00  0.00000000e+00]
         [ 0.00000000e+00  0.00000000e+00  1.00000000e+00  0.00000000e+00]
         [ 0.00000000e+00  0.00000000e+00  0.00000000e+00  1.00000000e+00]]
    """
    if not isinstance(t1, np.ndarray) or not isinstance(t2, np.ndarray):
        raise ValueError("Type Error: The matrices must be numpy arrays.")

    if t1.shape != (4, 4) or t2.shape != (4, 4):
        raise ValueError("Shape Error: The matrices must be (4, 4) numpy arrays.")

    return matrix_inverse(t1) @ t2


def adjoint(T: np.ndarray) -> np.ndarray:
    """
    Computes the adjoint representation of a transformation matrix.

    Args:
        T (np.ndarray): Transformation matrix as a numpy array.

    Returns:
        adj_t (np.ndarray): Adjoint representation of the transformation matrix
        as a (6, 6) numpy array.

    Raises:
        ValueError: If the matrix is not a numpy array.
        ValueError: If the matrix does not have shape (4, 4).

    Examples:
        >>> T = np.array([[1, 0,  0, 0],
        ...               [0, 0, -1, 0],
        ...               [0, 1,  0, 3],
        ...               [0, 0,  0, 1]])
        >>> adj_t = adjoint(T)
        >>> print(adj_t)
        [[1, 0,  0, 0, 0,  0],
         [0, 0, -1, 0, 0,  0],
         [0, 1,  0, 0, 0,  0],
         [0, 0,  3, 1, 0,  0],
         [3, 0,  0, 0, 0, -1],
         [0, 0,  0, 0, 1,  0]]
    """
    if not isinstance(T, np.ndarray):
        raise ValueError("Type Error: The matrix must be a numpy array.")

    if T.shape != (4, 4):
        raise ValueError("Shape Error: The matrix must be a (4, 4) numpy array.")
    R, p = T[:3, :3], T[:3, 3]
    Adj = np.zeros((6, 6), dtype=np.float64)
    Adj[:3, :3] = R
    Adj[3:, 3:] = R
    Adj[3:, :3] = vec_to_so3(p) @ R
    return Adj


def vec_to_se3(vec: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Converts a spacial velocity vector (spatial twist) into a (4, 4) matrix in
    se(3).

    Args:
        vec (np.ndarray | Iterable[float]): Spatial velocity vector [ ws | vs ]
                in R6 as a numpy array or as a iterable of float values.

    Returns:
        matrix (np.ndarray): The spatial twist represented as a (4, 4) numpy array.

    Raises:
        ValueError: If the vector is not a numpy array or a list.
        ValueError: If the vector does not have 6 elements.

    Examples:
        >>> vec = [1, 2, 3, 4, 5, 6]
        >>> se3 = vec_to_se3(vec)
        >>> print(se3)
        [[ 0.         -3.          2.          4.        ]
        [ 3.          0.         -1.          5.        ]
        [-2.          1.          0.          6.        ]
        [ 0.          0.          0.          0.        ]]
    """
    if (not isinstance(vec, np.ndarray)) and (not isinstance(vec, list)):
        raise ValueError("Type Error: The vector must be a numpy array or a list.")

    if len(vec) != 6:
        raise ValueError("Shape Error: The vector must have only 6 components.")

    vec = np.array(vec).flatten() if isinstance(vec, list) else vec.flatten()

    matrix = np.zeros((4, 4), dtype=np.float64)
    matrix[:3, :3] = vec_to_so3(vec[:3])
    matrix[:3, 3] = vec[3:]
    return matrix


def se3_to_vec(mat: np.ndarray) -> np.ndarray:
    """
    Convert a se(3) (4, 4) matrix into a spatial velocity vector (spatial twist)
    in R6, [ ws | vs ].

    Args:
        mat (np.ndarray): se(3) matrix as a (4, 4) numpy array.

    Returns:
        vec (np.ndarray): Spatial velocity vector (spatial twist) as a (6, )
            numpy array.

    Raises:
        ValueError: If the matrix is not a numpy array.
        ValueError: If the matrix does not have shape (4, 4).

    Examples:
        >>> mat = np.array([[0, -3, 2, 4],
        ...                 [3, 0, -1, 5],
        ...                 [-2, 1, 0, 6],
        ...                 [0, 0, 0, 0]])
        >>> vec = se3_to_vec(mat)
        >>> print(vec)
        [1. 2. 3. 4. 5. 6.]
    """
    if not isinstance(mat, np.ndarray):
        raise ValueError("Type Error: The matrix must be a numpy array.")

    if mat.shape != (4, 4):
        raise ValueError("Shape Error: The matrix must be a (4, 4) numpy array.")

    vec = np.zeros((6,))
    vec[:3] = so3_to_vec(mat[:3, :3])
    vec[3:] = mat[:3, 3]
    return vec


def axis_ang6(vec: Union[np.ndarray, Iterable[float]]) -> Tuple[np.ndarray, float]:
    """
    Convert the exponential coordinates of a homogeneous transformation S*theta
    to a screw axis-angle form.

    Args:
        vec (Union[np.ndarray, Iterable[float]]): Exponential coordinates of a
            homogeneous transformation in R6 as a numpy array or as an iterable
            of float values.

    Returns:
        axis, theta (Tuple[np.ndarray, float]): The screw axis-angle representation
            of the exponential coordinates.

    Raises:
        ValueError: If the vector is not a numpy array or a list.
        ValueError: If the vector does not have 6 elements.

    Examples:
        >>> vec = [1, 2, 3, 4, 5, 6]
        >>> axis, theta = axis_ang6(vec)
        >>> print(axis)
        [0.13483997 0.26967994 0.40451992 0.53935989 0.67419986 0.80903984]
        >>> print(theta)
        7.810249675906654
    """
    if (not isinstance(vec, np.ndarray)) and (not isinstance(vec, list)):
        raise ValueError("Type Error: The vector must be a numpy array or a list.")

    if len(vec) != 6:
        raise ValueError("Shape Error: The vector must have only 6 components.")

    vec = np.array(vec).flatten() if isinstance(vec, list) else vec.flatten()

    vec_norm = np.linalg.norm(vec[:3])
    if np.abs(vec_norm) < 1.00e-06:
        vec_norm = np.linalg.norm(vec[3:])
    return vec / vec_norm, vec_norm


def matrix_exp6(mat: np.ndarray) -> np.ndarray:
    """
    Computes the matrix exponential of an se(3) representation of exponential
    coordinates of a homogeneous transformation.

    Args:
        mat (np.ndarray): se(3) matrix as a (4, 4) numpy array.

    Returns:
        mat (np.ndarray): The matrix exponential of an se(3) matrix as a SE(3)
            (4, 4) numpy array.

    Raises:
        ValueError: If the matrix is not a numpy array.
        ValueError: If the matrix does not have shape (4, 4).
    """
    if not isinstance(mat, np.ndarray):
        raise ValueError("Type Error: The matrix must be a numpy array.")

    if mat.shape != (4, 4):
        raise ValueError("Shape Error: The matrix must be a (4, 4) numpy array.")

    so3mat = mat[:3, :3]
    omega = so3_to_vec(so3mat)
    output = np.eye(4, dtype=np.float64)

    if np.abs(np.linalg.norm(omega)) < 1.00e-06:
        output[:3, 3] = mat[:3, 3]
        return output

    else:
        theta = axis_ang3(omega)[1]
        omega_mat = mat[0:3, 0:3] / theta
        output[:3, :3] = matrix_exp3(mat[:3, :3])
        v = mat[:3, 3] / theta
        output[:3, 3] = (
            np.eye(3, dtype=np.float64) * theta
            + (1 - np.cos(theta)) * omega_mat
            + (theta - np.sin(theta)) * (omega_mat @ omega_mat)
        ) @ v
        return output


def matrix_log6(mat: np.ndarray) -> np.ndarray:
    """
    Compute the logarithm of a homogeneous transformation matrix in SE(3).

    Args:
        mat (np.ndarray): Homogeneous transformation matrix as a SE(3) (4, 4)
            numpy array.

    Returns:
        log_mat (np.ndarray): The logarithm of the homogeneous transformation
            matrix as a (4, 4) numpy array.

    Raises:
        ValueError: If the matrix is not a numpy array.
        ValueError: If the matrix does not have shape (4, 4).
    """
    if not isinstance(mat, np.ndarray):
        raise ValueError("Type Error: The matrix must be a numpy array.")

    if mat.shape != (4, 4):
        raise ValueError("Shape Error: The matrix must be a (4, 4) numpy array.")

    R, p = mat[:3, :3], mat[:3, [-1]]
    omegatheta_mat = matrix_log3(R)
    output = np.zeros((4, 4), dtype=np.float64)

    # Check if the Identity matrix is close to the identity:
    if np.array_equal(omegatheta_mat, np.zeros((3, 3))):
        output[:3, [3]] = p
        return output
    else:
        theta = np.arccos((np.trace(R) - 1) * 0.5)
        output[:3, :3] = omegatheta_mat
        v = (
            np.eye(3, dtype=np.float64)
            - omegatheta_mat * 0.5
            + (
                (1.0 / theta - (0.5 / (np.tan(theta * 0.5))))
                * (omegatheta_mat @ omegatheta_mat)
            )
            / theta
        )
        output[:3, [3]] = v @ p
        return output


def project_to_se3(mat: np.ndarray) -> np.ndarray:
    """
    Projects a matrix to the closest matrix in SE(3) using singular value
    decomposition.
    Source: http://hades.mech.northwestern.edu/index.php/Modern_Robotics_Linear_Algebra_Review

    Args:
        mat (np.ndarray): Matrix near SE(3) as a (4, 4) numpy array.

    Returns:
        mat_se3 (np.ndarray): Matrix projected into SE(3) as a (4, 4) numpy array.

    Raises:
        ValueError: If the matrix is not a numpy array.
        ValueError: If the matrix does not have shape (4, 4).
    """
    if not isinstance(mat, np.ndarray):
        raise ValueError("Type Error: The matrix must be a numpy array.")

    if mat.shape != (4, 4):
        raise ValueError("Shape Error: The matrix must be a (4, 4) numpy array.")
    T = np.eye(4, dtype=np.float64)
    T[:3, :3], T[:3, 3] = project_to_so3(mat[:3, :3]), mat[:3, 3]
    return T


def distance_to_se3(mat: np.ndarray) -> float:
    """
    Compute the frobenius norm to describe the distance of a matrix from
    the SE(3) manifold.

    Args:
        mat (np.ndarray): Matrix near SE(3) as a (4, 4) numpy array.

    Returns:
        Frobenius norm of matrix as a float.

    Raises:
        ValueError: If the matrix is not a numpy array.
        ValueError: If the matrix does not have shape (4, 4).
    """
    if not isinstance(mat, np.ndarray):
        raise ValueError("Type Error: The matrix must be a numpy array.")

    if mat.shape != (4, 4):
        raise ValueError("Shape Error: The matrix must be a (4, 4) numpy array.")

    R = mat[:3, :3]
    if np.linalg.det(R) > 0:
        output = np.zeros((4, 4), dtype=np.float64)
        output[:3, :3], output[3, :] = R.T @ R, mat[3, :]
        return np.linalg.norm(output - np.eye(4, dtype=np.float64))
    else:
        return 1.00e10
