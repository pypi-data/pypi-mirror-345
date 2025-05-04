"""
This module provides functions to work in the special orthogonal group SO(3) and its Lie algebra so(3).

Functions:
    rot_inv(rot): Compute the inverse of a rotation matrix.
    hpr2quat(hpr): Convert Heading, Pitch and Roll (HPR) angles to quaternion using the ZYX Euler angles convention.
    rph2quat(rph): Convert Roll, Pitch, Heading (RPH) angles to quaternion using the ZYX Euler angles convention.
    quat2hpr(quat): Convert quaternion to Heading, Pitch and Roll (HPR) angles using the ZYX Euler angles convention.
    quat2rph(quat): Convert quaternion to Roll, Pitch, Heading (RPH) angles using the ZYX Euler angles convention.
    hpr2rot(hpr): Convert Heading, Pitch and Roll (HPR) angles to SO(3) rotation matrix using the ZYX Euler angles
                  convention.
    rph2rot(rph): Convert Roll, Pitch, Heading (RPH) angles to SO(3) rotation matrix using the ZYX Euler angles
                  convention.
    quat2rot(quat): Convert quaternion to a rotation matrix in SO(3) using the ZYX Euler angles convention.
    rot2hpr(rot): Convert SO(3) rotation matrix to Roll, Pitch, Heading (RPH) angles using the ZYX Euler angles
                  convention.
    rot2rph(rot): Convert SO(3) rotation matrix to Roll, Pitch, Heading (RPH) angles using the ZYX Euler angles
                  convention.
    rot2quat(rot): Convert SO(3) rotation matrix to quaternion using the ZYX Euler angles convention.
    rot_diff(rot_1, rot_2): Compute the relative rotation between two matrices.
    vec_to_so3(vec): Compute the skew-symmetric representation for a vector of R3.
    so3_to_vec(mat): Convert a so3 matrix into a R3 vector.
    axis_ang3(vec): Converts a R3 representing a rotation into a exponential coordinates parametrization.
    matrix_exp3(mat): Compute the matrix exponential of a matrix in so(3) representing the exponential coordinates
                      for rotation.
    matrix_log3(mat): Compute the matrix logarithm of a matrix in SO(3) representing the exponential coordinates
                        for rotation.
    project_to_so3(mat): Project a matrix in R3 to SO(3).
    distance_to_so3(mat_1, mat_2): Compute the distance between two matrices in SO(3).
    left_quat_product_matrix(quat): Compute the left quaternion product matrix for a quaternion.
    right_quat_product_matrix(quat): Compute the right quaternion product matrix for a quaternion.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

import math
from typing import Any, Callable, Iterable, Tuple, Union

import numpy as np
import pymanopt


def rot_inv(rot: np.ndarray) -> np.ndarray:
    """
    Compute the inverse of a rotation matrix.

    Args:
        rot (np.ndarray): The rotation matrix as a (3,3) numpy array.

    Returns:
        rot_mat (np.ndarray): The inverse of the rotation matrix as a (3,3) numpy array.

    Raises:
        ValueError: If the input rotation matrix is not a (3,3) numpy array.

    Examples:
        >>> rot_mat = np.array([[0.93629336, -0.27509585, 0.21835066],
                                [0.28962948, 0.95642509, -0.03695701],
                                [-0.19866933, 0.0978434, 0.97517033]])
        >>> rot_inv = rot_inv(rot_mat)
        >>> print(rot_inv)
        [[ 0.93629336  0.28962948 -0.19866933]
         [-0.27509585  0.95642509  0.0978434 ]
         [ 0.21835066 -0.03695701  0.97517033]]

    Notes:
        The input rotation matrix must be orthonormal and have a determinant of +1 to represent a valid rotation.
    """
    if not isinstance(rot, np.ndarray) and not isinstance(rot, list):
        raise ValueError("Usage: The rotation matrix must be a numpy array or a list.")

    rot = np.array(rot) if isinstance(rot, list) else rot

    if rot.shape != (3, 3):
        raise ValueError("Usage: The rotation matrix must have shape (3, 3)")

    return np.einsum("ij -> ji", rot)


def hpr2quat(hpr: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Convert Heading, Pitch and Roll (HPR) angles to quaternion using the ZYX Euler angles convention.

    Args:
        hpr (Union[np.ndarray, Iterable[float]]): hpr angles in radians as a numpy array or as a list.

    Returns:
        quat (np.ndarray): The quaternion using hpr with the convention ZYX in order (x, y, z, w)

    Raises:
        ValueError: If the input HPR angles are not a 3-element numpy array or list.

    Examples:
        >>> hpr = np.array([0.3, 0.2, 0.1])
        >>> quat = hpr2quat(hpr)
        >>> print(quat)
        [0.93629336 0.28962948 0.19866933 0.0978434 ]

    Notes:
        The HPR angles represent rotations around the Z, Y, and X axes, respectively.
        The resulting quaternion represents a rotation of the input HPR angles using the ZYX Euler angles convention.
    """
    hpr = np.array(hpr).flatten() if isinstance(hpr, list) else hpr.flatten()
    if hpr.shape[0] != 3:
        raise ValueError("Usage: quat=hpr2quat([angH angP angR])")

    angH = hpr[0]
    angP = hpr[1]
    angR = hpr[2]

    ch = math.cos(angH / 2)
    sh = math.sin(angH / 2)
    cp = math.cos(angP / 2)
    sp = math.sin(angP / 2)
    cr = math.cos(angR / 2)
    sr = math.sin(angR / 2)

    quat = np.array(
        [
            ch * cp * sr - sh * sp * cr,
            ch * sp * cr + sh * cp * sr,
            sh * cp * cr - ch * sp * sr,
            ch * cp * cr + sh * sp * sr,
        ]
    )

    return quat


def rph2quat(rph: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Convert Roll, Pitch, Heading (RPH) angles to quaternion using the ZYX Euler angles convention.

    Args:
        rph (Union[np.ndarray, Iterable[float]]): rph angles in radians as a numpy array or as a list.

    Returns:
        quat (np.ndarray): The quaternion using rph with the convention ZYX in order (x, y, z, w)

    Raises:
        ValueError: If the input RPH angles are not a 3-element numpy array or list.

    Examples:
        >>> rph = np.array([0.1, 0.2, 0.3])
        >>> quat = rph2quat(rph)
        >>> print(quat)
        [0.93629336 0.28962948 0.19866933 0.0978434 ]

    Notes:
        The RPH angles represent rotations around the X, Y, and Z axes, respectively.
        The resulting quaternion represents a rotation of the input RPH angles using the ZYX Euler angles convention.
    """
    rph = np.array(rph).flatten() if isinstance(rph, list) else rph.flatten()
    if rph.shape[0] != 3:
        raise ValueError("Usage: quat=rph2quat([angH angP angR])")

    angR = rph[0]
    angP = rph[1]
    angH = rph[2]

    ch = math.cos(angH / 2)
    sh = math.sin(angH / 2)
    cp = math.cos(angP / 2)
    sp = math.sin(angP / 2)
    cr = math.cos(angR / 2)
    sr = math.sin(angR / 2)

    quat = np.array(
        [
            ch * cp * sr - sh * sp * cr,
            ch * sp * cr + sh * cp * sr,
            sh * cp * cr - ch * sp * sr,
            ch * cp * cr + sh * sp * sr,
        ]
    )

    return quat


def quat2hpr(quat: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Convert quaternion to Heading, Pitch and Roll (HPR) angles using the ZYX Euler angles convention.

    Args:
        quat (Union[np.ndarray, Iterable[float]]): The quaternion as a numpy array or as a list in the order
                                                    (x, y, z, w).

    Returns:
        hpr (np.ndarray): The HPR angles in radians as a numpy array with the convention ZYX.

    Raises:
        ValueError: If the input quaternion is not a 4-element numpy array or list.
        ValueError: If the input quaternion is not normalized.

    Examples:
        >>> quat = np.array([0.93629336, 0.28962948, 0.19866933, 0.0978434])
        >>> hpr = quat2hpr(quat)
        >>> print(hpr)
        [0.3 0.2 0.1]

    Notes:
        The resulting HPR angles represent rotations around the Z, Y, and X axes, respectively.
        The input quaternion must be normalized to represent a valid rotation.
    """
    quat = np.array(quat).flatten() if isinstance(quat, list) else quat.flatten()
    if quat.shape[0] != 4:
        raise ValueError("Usage: hpr=quat2hpr([x y z w])")

    if abs(np.linalg.norm(quat) - 1.0) >= 1e-6:
        raise ValueError("Usage: The quaternion must be normalized.")

    q0 = quat[3]
    q1 = quat[0]
    q2 = quat[1]
    q3 = quat[2]

    angH = math.atan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 * q2 + q3 * q3))
    angP = math.asin(2 * (q0 * q2 - q3 * q1))
    angR = math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 * q1 + q2 * q2))

    return np.array([angH, angP, angR])


def quat2rph(quat: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Convert quaternion to Roll, Pitch, Heading (RPH) angles using the ZYX Euler angles convention.

    Args:
        quat (Union[np.ndarray, Iterable[float]]): The quaternion as a numpy array or as a list in the order
                                                    (x, y, z, w).

    Returns:
        rph (np.ndarray): The RPH angles in radians as a numpy array with the convention ZYX.

    Raises:
        ValueError: If the input quaternion is not a 4-element numpy array or list.
        ValueError: If the input quaternion is not normalized.

    Examples:
        >>> quat = np.array([0.93629336, 0.28962948, 0.19866933, 0.0978434])
        >>> rph = quat2rph(quat)
        >>> print(rph)
        [0.1 0.2 0.3]

    Notes:
        The resulting RPH angles represent rotations around the X, Y, and Z axes, respectively.
        The input quaternion must be normalized to represent a valid rotation.
    """
    quat = np.array(quat).flatten() if isinstance(quat, list) else quat.flatten()
    if quat.shape[0] != 4:
        raise ValueError("Usage: rph=quat2rph([x y z w])")

    if abs(np.linalg.norm(quat) - 1.0) >= 1e-6:
        raise ValueError("Usage: The quaternion must be normalized.")

    q0 = quat[3]
    q1 = quat[0]
    q2 = quat[1]
    q3 = quat[2]

    angR = math.atan2(2 * (q0 * q1 + q2 * q3), 1 - 2 * (q1 * q1 + q2 * q2))
    angP = math.asin(2 * (q0 * q2 - q3 * q1))
    angH = math.atan2(2 * (q0 * q3 + q1 * q2), 1 - 2 * (q2 * q2 + q3 * q3))

    return np.array([angR, angP, angH])


def hpr2rot(hpr: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Convert Heading, Pitch and Roll (HPR) angles to SO(3) rotation matrix using the ZYX Euler angles convention.

    Args:
        hpr (Union[np.ndarray, Iterable[float]]): hpr angles in radians as a numpy array or as a list.

    Returns:
        rot (np.ndarray): The rotation matrix using hpr with the convention ZYX

    Raises:
        ValueError: If the input HPR angles are not a 3-element numpy array or list.

    Examples:
        >>> hpr = np.array([0.3, 0.2, 0.1])
        >>> rot_mat = hpr2rot(hpr)
        >>> print(rot_mat)
        [[ 0.93629336 -0.27509585  0.21835066]
         [ 0.28962948  0.95642509 -0.03695701]
         [-0.19866933  0.0978434   0.97517033]]

    Notes:
        The HPR angles represent rotations around the Z, Y, and X axes, respectively.
        The resulting rotation matrix represents a rotation of the input HPR angles using the ZYX Euler angles
        convention.
    """
    hpr = np.array(hpr).flatten() if isinstance(hpr, list) else hpr.flatten()
    if hpr.shape[0] != 3:
        raise ValueError("Usage: RotMat=hpr2rot([angH angP angR])")

    angH = hpr[0]
    angP = hpr[1]
    angR = hpr[2]

    c1 = math.cos(angH)
    s1 = math.sin(angH)
    c2 = math.cos(angP)
    s2 = math.sin(angP)
    c3 = math.cos(angR)
    s3 = math.sin(angR)

    RotMat = np.array(
        [
            [c1 * c2, c1 * s2 * s3 - c3 * s1, s1 * s3 + c1 * c3 * s2],
            [c2 * s1, c1 * c3 + s1 * s2 * s3, c3 * s1 * s2 - c1 * s3],
            [-s2, c2 * s3, c2 * c3],
        ]
    )

    return RotMat


def rph2rot(rph: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Convert Roll, Pitch, Heading (RPH) angles to SO(3) rotation matrix using the ZYX Euler angles convention.

    Args:
        rph (Union[np.ndarray, Iterable[float]]): rph angles in radians as a numpy array or as a list.

    Returns:
        rot (np.ndarray): The rotation matrix using rph with the convention ZYX

    Raises:
        ValueError: If the input RPH angles are not a 3-element numpy array or list.

    Examples:
        >>> rph = np.array([0.1, 0.2, 0.3])
        >>> rot_mat = rph2rot(rph)
        >>> print(rot_mat)
        [[ 0.93629336 -0.27509585  0.21835066]
         [ 0.28962948  0.95642509 -0.03695701]
         [-0.19866933  0.0978434   0.97517033]]

    Notes:
        The RPH angles represent rotations around the X, Y, and Z axes, respectively.
        The resulting rotation matrix represents a rotation of the input RPH angles using the ZYX Euler angles
        convention.
    """
    rph = np.array(rph).flatten() if isinstance(rph, list) else rph.flatten()
    if rph.shape[0] != 3:
        raise ValueError("Usage: RotMat=rph2rot([angH angP angR])")

    angR = rph[0]
    angP = rph[1]
    angH = rph[2]

    c1 = math.cos(angH)
    s1 = math.sin(angH)
    c2 = math.cos(angP)
    s2 = math.sin(angP)
    c3 = math.cos(angR)
    s3 = math.sin(angR)

    RotMat = np.array(
        [
            [c1 * c2, c1 * s2 * s3 - c3 * s1, s1 * s3 + c1 * c3 * s2],
            [c2 * s1, c1 * c3 + s1 * s2 * s3, c3 * s1 * s2 - c1 * s3],
            [-s2, c2 * s3, c2 * c3],
        ]
    )

    return RotMat


def quat2rot(quat: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Convert quaternion to a rotation matrix in SO(3) using the ZYX Euler angles convention.

    Args:
        quat (Union[np.ndarray, Iterable[float]]): The quaternion as a numpy array or as a list in the order
                                                    (x, y, z, w).

    Returns:
        rot (np.ndarray): The RPH angles in radians as a numpy array with the convention ZYX.

    Raises:
        ValueError: If the input quaternion is not a 4-element numpy array or list.
        ValueError: If the input quaternion is not normalized.

    Examples:
        >>> quat = np.array([0.93629336, 0.28962948, 0.19866933, 0.0978434])
        >>> rotmat = quat2rot(quat)
        >>> print(rotmat)
        [[ 0.93629336 -0.27509585  0.21835066]
         [ 0.28962948  0.95642509 -0.03695701]
         [-0.19866933  0.0978434   0.97517033]]

    Notes:
        The input quaternion must be normalized to represent a valid rotation.
    """
    quat = np.array(quat).flatten() if isinstance(quat, list) else quat.flatten()
    if quat.shape[0] != 4:
        raise ValueError("Usage: rph=quat2rph([x y z w])")

    if abs(np.linalg.norm(quat) - 1.0) >= 1e-6:
        raise ValueError("Usage: The quaternion must be normalized.")

    rph = quat2rph(quat)
    rot = rph2rot(rph)

    return rot


def rot2hpr(rot: np.ndarray) -> np.ndarray:
    """
    Convert SO(3) rotation matrix to Roll, Pitch, Heading (RPH) angles using the ZYX Euler angles convention.

    Args:
        rot (np.ndarray): The rotation matrix as a (3,3) numpy array.

    Returns:
        hpr (np.ndarray): The RPH angles in radians as a numpy array with the convention ZYX.

    Raises:
        ValueError: If the input rotation matrix is not a (3,3) numpy array or list.

    Examples:
        >>> rot_mat = np.array([[0.93629336, -0.27509585, 0.21835066],
                                [0.28962948, 0.95642509, -0.03695701],
                                [-0.19866933, 0.0978434, 0.97517033]])
        >>> hpr = rot2hpr(rot_mat)
        >>> print(hpr)
        [0.3 0.2 0.1]

    Notes:
        The resulting RPH angles represent rotations around the X, Y, and Z axes, respectively.
        The input rotation matrix must be orthonormal and have a determinant of +1 to represent a valid rotation.
    """
    if (not isinstance(rot, np.ndarray)) and (not isinstance(rot, list)):
        raise ValueError("Usage: The rotation matrix must be a numpy array or a list.")

    rot = np.array(rot) if isinstance(rot, list) else rot

    if rot.shape != (3, 3):
        raise ValueError("Usage: The rotation matrix must have shape (3, 3)")

    h = math.atan2(rot[1, 0], rot[0, 0])
    p = math.atan2(
        -rot[2, 0], math.sqrt(math.pow(rot[2, 1], 2) + math.pow(rot[2, 2], 2))
    )
    r = math.atan2(rot[2, 1], rot[2, 2])

    return np.array([h, p, r])


def rot2rph(rot: np.ndarray) -> np.ndarray:
    """
    Convert SO(3) rotation matrix to Roll, Pitch, Heading (RPH) angles using the ZYX Euler angles convention.

    Args:
        rot (np.ndarray): The rotation matrix as a (3,3) numpy array.

    Returns:
        rph (np.ndarray): The RPH angles in radians as a numpy array with the convention ZYX.

    Raises:
        ValueError: If the input rotation matrix is not a (3,3) numpy array.

    Examples:
        >>> rot_mat = np.array([[0.93629336, -0.27509585, 0.21835066],
                                [0.28962948, 0.95642509, -0.03695701],
                                [-0.19866933, 0.0978434, 0.97517033]])
        >>> rph = rot2rph(rot_mat)
        >>> print(rph)
        [0.1 0.2 0.3]

    Notes:
        The resulting RPH angles represent rotations around the X, Y, and Z axes, respectively.
        The input rotation matrix must be orthonormal and have a determinant of +1 to represent a valid rotation.
    """
    if (not isinstance(rot, np.ndarray)) and (not isinstance(rot, list)):
        raise ValueError("Usage: The rotation matrix must be a numpy array or a list.")

    rot = np.array(rot) if isinstance(rot, list) else rot

    if rot.shape != (3, 3):
        raise ValueError("Usage: The rotation matrix must have shape (3, 3)")

    h = math.atan2(rot[1, 0], rot[0, 0])
    p = math.atan2(
        -rot[2, 0], math.sqrt(math.pow(rot[2, 1], 2) + math.pow(rot[2, 2], 2))
    )
    r = math.atan2(rot[2, 1], rot[2, 2])

    return np.array([r, p, h])


def rot2quat(rot: np.ndarray) -> np.ndarray:
    """
    Convert SO(3) rotation matrix to quaternion using the ZYX Euler angles convention.

    Args:
        rot (np.ndarray): The rotation matrix as a (3,3) numpy array.

    Returns:
        quat (np.ndarray): The quaternion as a numpy array with the convention ZYX in order (x, y, z, w)

    Raises:
        ValueError: If the input rotation matrix is not a (3,3) numpy array.

    Examples:
        >>> rot_mat = np.array([[0.50000000, -0.1464466,  0.8535534],
                                [0.50000000,  0.8535534, -0.1464466],
                                [-0.7071068,  0.5000000,  0.5000000]])
        >>> quat = rot2quat(rot_mat)
        >>> print(quat)
        [0.1913417, 0.4619398, 0.1913417, 0.8446232]

    Notes:
        The input rotation matrix must be orthonormal and have a determinant of +1 to represent a valid rotation.
    """
    if (not isinstance(rot, np.ndarray)) and (not isinstance(rot, list)):
        raise ValueError("Usage: The rotation matrix must be a numpy array or a list.")

    rot = np.array(rot) if isinstance(rot, list) else rot

    if rot.shape != (3, 3):
        raise ValueError("Usage: The rotation matrix must have shape (3, 3)")

    rph = rot2rph(rot)
    quat = rph2quat(rph)

    return quat


def rot_diff(rot_1: np.ndarray, rot_2: np.ndarray) -> np.ndarray:
    """
    Compute the relative rotation between two matrices.

    The returned matrix is the attitude of 2 with respect to 1:

    $$ R_{12} = R_{1w} \\cdot R_{w2} = R_{w1}^{-1} \\cdot R_{w2} $$

    Args:
        rot_1 (np.ndarray): Rotation matrix for attitude 1 as a numpy array.
        rot_2 (np.ndarray): Rotation matrix for attitude 2 as a numpy array.

    Returns:
        rot_1_2 (np.ndarray): The attitude of 2 with respect to 1 as a numpy array.

    Raises:
        ValueError: If the input rotation matrices are not (3,3) numpy arrays.

    Examples:
        >>> rot_mat_1 = np.array([[0.93629336, -0.27509585, 0.21835066],
                                [0.28962948, 0.95642509, -0.03695701],
                                [-0.19866933, 0.0978434, 0.97517033]])
        >>> rot_mat_2 = np.array([[0.82298387, -0.41998535, 0.38175244],
                                [0.56975033, 0.81758362, -0.08209422],
                                [-0.0, 0.3939193, 0.91914503]])
        >>> rot_diff = rotDiff(rot_mat_1, rot_mat_2)
        >>> print(rot_diff)
        [[ 0.93557083, -0.23469286,  0.15104944],
         [ 0.31852406,  0.93603611, -0.09360322],
         [ 0.1586428 ,  0.26221888,  0.98271281]]

    Notes:
        The input rotation matrices must be orthonormal and have a determinant of +1 to represent valid rotations.
    """
    if not isinstance(rot_1, np.ndarray) or not isinstance(rot_2, np.ndarray):
        raise ValueError("Usage: The rotation matrices must be numpy arrays.")
    if rot_1.shape != (3, 3) or rot_2.shape != (3, 3):
        raise ValueError("Usage: The rotation matrix must have shape (3, 3)")
    return np.einsum("ij -> ji", rot_1) @ rot_2


def vec_to_so3(vec: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Compute the skew-symmetric representation for a vector of $\\mathbf{R}^3$.

    $$ \\lfloor x \\rfloor =
    \\begin{bmatrix}
    0 & -z & y \\\\
    z & 0 & -x \\\\
    -y & x & 0
    \\end{bmatrix}
    $$

    Args:
        vec (Union[np.ndarray, Iterable[float]]): The vector as a numpy array or a list.

    Returns:
        skew (np.ndarray): The skew-symmetric matrix as a numpy array.

    Raises:
        ValueError: If the input vector is not a numpy array or a list.
        ValueError: If the input vector does not have 3 components.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> skew_sym = vec_to_so3(vec)
        >>> print(skew_sym)
        [[ 0. -3.  2.]
         [ 3.  0. -1.]
         [-2.  1.  0.]]
    """
    if (not isinstance(vec, np.ndarray)) and (not isinstance(vec, list)):
        raise ValueError("Type Error: The vector must be a numpy array or a list.")
    if isinstance(vec, np.ndarray):
        vec = vec.flatten()
    if len(vec) != 3:
        raise ValueError("Shape Error: The vector must have only 3 components.")
    matrix = np.zeros((3, 3))
    matrix[0, 1], matrix[0, 2], matrix[1, 2] = -vec[2], vec[1], -vec[0]
    return matrix - matrix.T


def so3_to_vec(mat: np.ndarray) -> np.ndarray:
    """
    Convert a so3 matrix into a $\\mathbf{R}^3$ vector.

    Args:
        mat (np.ndarray): The skew-symmetric matrix as a (3,3) numpy array.

    Returns:
        vec (np.ndarray): The vector as a (3, ) numpy array.

    Raises:
        ValueError: If the input matrix is not a (3,3) numpy array.

    Examples:
        >>> skew_sym = np.array([[0, -3, 2], [3, 0, -1], [-2, 1, 0]])
        >>> vec = so3_to_vec(skew_sym)
        >>> print(vec)
        [1. 2. 3.]
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise ValueError("Type Error: The matrix must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    if mat.shape != (3, 3):
        raise ValueError("Shape Error: The matrix must have shape (3, 3).")

    return np.array([mat[2][1], mat[0][2], mat[1][0]])


def axis_ang3(vec: Union[Iterable[float], np.ndarray]) -> Tuple[np.ndarray, float]:
    """
    Converts a $\\mathbf{R}^3$ representing a rotation into a exponential coordinates
    parametrization, i.e., a unit vector representing the axis (w) and an
    angle theta.

    Args:
        vec (Union[Iterable[float], np.ndarray]): R3 vector representing a rotation in so3.

    Returns:
        axis (np.ndarray): Unit vector representing the axis of rotation as a numpy array.
        angle (float): Angle of rotation in radians.

    Raises:
        ValueError: If the input vector is not a numpy array or a list.
        ValueError: If the input vector does not have 3 components.

    Examples:
        >>> vec = np.array([1, 2, 3])
        >>> axis, angle = axis_ang_3(vec)
        >>> print(axis)
        [0.26726124 0.53452248 0.80178373]
        >>> print(angle)
        3.7416573867739413
    """
    if (not isinstance(vec, np.ndarray)) and (not isinstance(vec, list)):
        raise ValueError("Type Error: The vector must be a numpy array or a list.")

    vec = np.array(vec).flatten() if isinstance(vec, list) else vec.flatten()

    if len(vec) != 3:
        raise ValueError("Shape Error: The vector must have only 3 components.")

    if np.allclose(vec, np.zeros(3)):
        return np.zeros(3), 0

    vec_norm = np.linalg.norm(vec)
    return vec / vec_norm, vec_norm


def matrix_exp3(mat: np.ndarray) -> np.ndarray:
    """
    Compute the matrix exponential of a matrix in so(3) representing the
    exponential coordinates for rotation, i.e., [w]*theta, where [w] is the
    skew-symmetric matrix of the unitary rotation axis. To compute the exponential
    matrix, the Rodrigues' formula is used.

    Args:
        mat (np.ndarray): Skew-symmetric matrix representing the exponential coordinates of rotation as a (3, 3)
            numpy array.

    Returns:
        mat_exp3 (np.ndarray): Matrix exponential of the exponential coordinates as a numpy array.

    Raises:
        ValueError: If the input matrix is not a (3,3) numpy array.
        ValueError: If the input matrix is not a skew-symmetric matrix.

    Examples:
        >>> skew_sym = np.array([[0, -3, 2], [3, 0, -1], [-2, 1, 0]])
        >>> exp_mat = matrix_exp_3(skew_sym)
        >>> print(exp_mat)
        [[-0.69492056  0.71352099  0.08929286]
         [-0.19200697 -0.30378504  0.93319235]
         [ 0.69297817  0.63134970   0.34810748]]
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise ValueError("Type Error: The matrix must be a numpy array or a list.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    if mat.ndim != 2:
        raise ValueError("Shape Error: The matrix must be a 2-dimensional numpy array.")
    if mat.shape != (3, 3):
        raise ValueError("Shape Error: The matrix must be a (3, 3) numpy array.")

    rotation = so3_to_vec(mat)

    # Check if the rotation is zero to avoid singularity
    if np.abs(np.linalg.norm(rotation)) < 1.00e-06:
        return np.eye(3, dtype=np.float64)

    else:
        theta = axis_ang3(rotation)[1]
        unit_mat = mat / theta
        return (
            np.eye(3, dtype=np.float64)
            + np.sin(theta) * unit_mat
            + (1 - np.cos(theta)) * (unit_mat @ unit_mat)
        )


def matrix_log3(R: np.ndarray) -> np.ndarray:
    """
    Computes the matrix logarithm of a rotation matrix.

    Args:
        R (np.ndarray): Rotation matrix as a (3, 3) numpy array.

    Returns:
        mat_log3 (np.ndarray): Matrix logarithm of the rotation matrix as a numpy array.

    Raises:
        ValueError: If the input matrix is not a (3,3) numpy array.
        ValueError: If the input matrix is not a rotation matrix.

    Examples:
        >>> rot_mat = np.array([[0.93629336, -0.27509585, 0.21835066],
                                [0.28962948, 0.95642509, -0.03695701],
                                [-0.19866933, 0.0978434, 0.97517033]])
        >>> log_mat = matrix_log_3(rot_mat)
        >>> print(log_mat)
        [[ 0.        , -0.28874894,  0.21322592],
         [ 0.28874894,  0.        , -0.06892461],
         [-0.21322592,  0.06892461,  0.        ]]
    """
    if not isinstance(R, np.ndarray) and not isinstance(R, list):
        raise ValueError("Type Error: The matrix must be a numpy array or a list.")

    R = np.array(R) if isinstance(R, list) else R

    if R.ndim != 2:
        raise ValueError("Shape Error: The matrix must be a 2-dimensional numpy array.")
    if R.shape != (3, 3):
        raise ValueError("Shape Error: The matrix must be a (3, 3) numpy array.")

    acos_arg = (np.trace(R) - 1) * 0.5

    # acos is undefined
    if acos_arg >= 1:
        return np.zeros((3, 3))

    # if theta = pi, three possible solutions.
    elif acos_arg <= -1:
        if not (np.abs(1 + R[2, 2]) < 1.00e-06):
            omg = (1.0 / np.sqrt(2 * (1 + R[2, 2]))) * (
                R[:, 2] + np.array([0.0, 0.0, 1.0])
            )
        elif not (np.abs(1 + R[1, 1]) < 1.00e-06):
            omg = (1.0 / np.sqrt(2 * (1 + R[1, 1]))) * (
                R[:, 1] + np.array([0.0, 1.0, 0.0])
            )
        else:
            omg = (1.0 / np.sqrt(2 * (1 + R[0, 0]))) * (
                R[:, 0] + np.array([1.0, 0.0, 0.0])
            )
        return vec_to_so3(np.pi * omg)

    else:
        theta = np.arccos(acos_arg)
        return theta * (1 / (2.0 * np.sin(theta))) * (R - R.T)


def project_to_so3(mat: np.ndarray) -> np.ndarray:
    """
    Projects a matrix to the closest matrix in SO(3) using singular value
    decomposition.
    Source: http://hades.mech.northwestern.edu/index.php/Modern_Robotics_Linear_Algebra_Review

    Args:
        mat (np.ndarray): The matrix as a (3,3) numpy array.

    Returns:
        mat_so3 (np.ndarray): The closest matrix in SO(3) as a numpy array.

    Raises:
        ValueError: If the input matrix is not a (3,3) numpy array.

    Examples:
        >>> mat = np.array([[ 0.675,  0.150,  0.720],
                            [ 0.370,  0.771, -0.511],
                            [-0.630,  0.619,  0.472]])
        >>> proj_mat = projectToSO3(mat)
        >>> print(proj_mat)
        [[ 0.67901136,  0.14894516,  0.71885945],
         [ 0.37320708,  0.77319584, -0.51272279],
         [-0.63218672,  0.61642804,  0.46942137]]
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise ValueError("Type Error: The matrix must be a numpy array.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    if mat.ndim != 2:
        raise ValueError("Shape Error: The matrix must be a 2-dimensional numpy array.")
    if mat.shape != (3, 3):
        raise ValueError("Shape Error: The matrix must be a (3, 3) numpy array.")

    U, s, V = np.linalg.svd(mat)
    R = U @ V
    if np.linalg.det(R) < 0:
        # Results may be far from mat.
        R[:, s[2, 2]] = -R[:, s[2, 2]]
    return R


def distance_to_so3(mat: np.ndarray) -> float:
    """
    Compute the frobenius norm to describe the distance of a matrix from
    the SO(3) manifold.

    Args:
        mat (np.ndarray): The matrix as a (3,3) numpy array.

    Returns:
        dist_so3 (float): The frobenius norm as a float.

    Raises:
        ValueError: If the input matrix is not a (3,3) numpy array.

    Examples:
        >>> mat = np.array([[ 0.675,  0.150,  0.720],
                            [ 0.370,  0.771, -0.511],
                            [-0.630,  0.619,  0.472]])
        >>> dist = distanceToSO3(mat)
        >>> print(dist)
        0.0663128178912833
    """
    if not isinstance(mat, np.ndarray) and not isinstance(mat, list):
        raise ValueError("Type Error: The matrix must be a numpy array.")

    mat = np.array(mat) if isinstance(mat, list) else mat

    if mat.ndim != 2:
        raise ValueError("Shape Error: The matrix must be a 2-dimensional numpy array.")
    if mat.shape != (3, 3):
        raise ValueError("Shape Error: The matrix must be a (3, 3) numpy array.")

    if np.linalg.det(mat) > 0:
        return np.linalg.norm(mat.T @ mat - np.eye(3, dtype=np.float64))
    else:
        return 1.00e10


def so3_optimization(
    objective_function: Callable, *args: Any, **kwargs: Any
) -> np.ndarray:
    """
    Perform optimization on the Special Orthogonal Group (SO(3)).
    This function uses the pymanopt library to optimize a given objective
    function on the SO(3) manifold.

    Args:
        objective_function (Callable): The objective function to be optimized.
            If the cost function uses numpy for computations, it MUST use
            the numpy module from autograd, i.e., autograd.numpy. Also, the
            function must return a scalar value.
        *args (Any): Positional arguments to be passed to the objective function.
        **kwargs (Any): Keyword arguments to be passed to the objective function.

    Returns:
        mat_so3_opt (np.ndarray): The optimized SO(3) matrix as a numpy array.

    Raises:
        TypeError: If the objective_function is not callable.
        ValueError: If the optimization does not return a valid SO(3) matrix.
        ValueError: If the result is not a (3,3) numpy array.

    Notes:
        For the cost function you can use `import autograd.numpy as np` to
        use numpy functions.
    """
    # Type check: Ensure objective_function is callable.
    if not callable(objective_function):
        raise TypeError("The objective_function must be callable.")

    manifold = pymanopt.manifolds.SpecialOrthogonalGroup(3)
    cost = pymanopt.function.autograd(manifold)(
        lambda x: objective_function(x, *args, **kwargs)
    )
    problem = pymanopt.Problem(manifold=manifold, cost=cost)
    optimizer = pymanopt.optimizers.TrustRegions(verbosity=0)
    result = optimizer.run(problem).point

    # Check that the result is a (3,3) numpy array.
    if not isinstance(result, np.ndarray) or result.shape != (3, 3):
        raise ValueError(
            "Optimization did not return a valid SO(3) matrix of shape (3, 3)."
        )

    return result


def left_quat_product_matrix(quat: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Compute the left quaternion product matrix for a given quaternion, such that
    q * p = L(q) * p. For a quaternion q = (x, y, z, w), the left quaternion product
    matrix is defined as:

    $$
    L(q) =
    \\begin{bmatrix}
        w & -z & y & x \\\\
        z & w & -x & y \\\\
        -y & x & w & z \\\\
        -x & -y & -z & w
    \\end{bmatrix}
    $$

    Args:
        quat (Union[np.ndarray, Iterable[float]]): The quaternion as a numpy array or as a list in the order
            (x, y, z, w).

    Returns:
        left_quat_product_matrix (np.ndarray): The left quaternion product matrix as a (4, 4) numpy array.

    Raises:
        ValueError: If the input quaternion is not a 4-element numpy array or list.
        ValueError: If the input quaternion is not normalized.
        TypeError: If the input quaternion is not a numpy array or list.
    """
    # Convert to numpy array if input is a list
    if isinstance(quat, list):
        quat = np.array(quat)

    # Check if the input is a numpy array
    if not isinstance(quat, np.ndarray):
        raise TypeError("The quaternion must be a numpy array or a list.")

    # Check if the input quaternion has 4 elements
    quat = quat.squeeze()
    if quat.shape[0] != 4:
        raise ValueError("The quaternion must have 4 elements.")
    if quat.ndim != 1:
        raise ValueError("The quaternion must be a 1-dimensional numpy array or list.")

    # Check if the quaternion is normalized
    if abs(np.linalg.norm(quat) - 1.0) >= 1e-6:
        raise ValueError("The quaternion must be normalized.")

    # Extract quaternion components
    x, y, z, w = quat[0], quat[1], quat[2], quat[3]

    # Construct the left quaternion product matrix
    left_quat_product_matrix = np.array(
        [
            [w, -z, y, x],
            [z, w, -x, y],
            [-y, x, w, z],
            [-x, -y, -z, w],
        ]
    )
    return left_quat_product_matrix


def right_quat_product_matrix(quat: Union[np.ndarray, Iterable[float]]) -> np.ndarray:
    """
    Compute the right quaternion product matrix for a given quaternion, such that
    q * p = R(p) * q For a quaternion q = (x, y, z, w), the right quaternion product
    matrix is defined as:

    $$
    R(q) =
    \\begin{bmatrix}
        w & z & -y & x \\\\
        -z & w & x & y \\\\
        y & -x & w & z \\\\
        -x & -y & -z & w
    \\end{bmatrix}
    $$

    Args:
        quat (Union[np.ndarray, Iterable[float]]): The quaternion as a numpy array or as a list in the order
            (x, y, z, w).

    Returns:
        right_quat_product_matrix (np.ndarray): The right quaternion product matrix as a (4, 4) numpy array.

    Raises:
        ValueError: If the input quaternion is not a 4-element numpy array or list.
        ValueError: If the input quaternion is not normalized.
        TypeError: If the input quaternion is not a numpy array or list.
    """
    # Convert to numpy array if input is a list
    if isinstance(quat, list):
        quat = np.array(quat)

    # Check if the input is a numpy array
    if not isinstance(quat, np.ndarray):
        raise TypeError("The quaternion must be a numpy array or a list.")

    # Check if the input quaternion has 4 elements
    quat = quat.squeeze()
    if quat.shape[0] != 4:
        raise ValueError("The quaternion must have 4 elements.")
    if quat.ndim != 1:
        raise ValueError("The quaternion must be a 1-dimensional numpy array or list.")

    # Check if the quaternion is normalized
    if abs(np.linalg.norm(quat) - 1.0) >= 1e-6:
        raise ValueError("The quaternion must be normalized.")

    # Extract quaternion components
    x, y, z, w = quat[0], quat[1], quat[2], quat[3]

    # Construct the right quaternion product matrix
    right_quat_product_matrix = np.array(
        [
            [w, z, -y, x],
            [-z, w, x, y],
            [y, -x, w, z],
            [-x, -y, -z, w],
        ]
    )
    return right_quat_product_matrix
