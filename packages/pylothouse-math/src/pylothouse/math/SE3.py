import argparse
import numpy as np
from pyrr import Vector3


def check_coordinate_system(matrix):
    # Ensure the matrix is a numpy array
    matrix = np.array(matrix)

    # Check if the matrix is 4x4
    if matrix.shape != (4, 4):
        raise ValueError("Input matrix must be 4x4")

    # Extract the rotation part of the matrix
    rotation_matrix = matrix[:3, :3]

    # Calculate the determinant of the rotation matrix
    determinant = np.linalg.det(rotation_matrix)

    # Check the determinant
    if np.isclose(determinant, 1):
        return "Right-handed"
    elif np.isclose(determinant, -1):
        return "Left-handed"
    else:
        return "Invalid"


def pose_to_homogeneous(q, t):
    """
        Takes a quaternion (qw, qx, qy, qz) and a translation vector (px, py, pz) and returns a 4x4 homogeneous transformation matrix
    Args:
        q: The quaternion in the format (qw, qx, qy, qz)
        t: The translation vector in the format (px, py, pz)

    Returns: 4x4 homogeneous transformation matrix with the 3x3 rotation matrix R and 3x1 translation vector t
    [R t]\n
    [0 1]
    """
    # Convert pose to homogeneous transformation
    homo = q_to_homogeneous(q)
    homo[:3, 3] = t
    return homo


def q_to_homogeneous(q):
    """
        Takes a quaternion [qw, qx, qy, qz] and returns a 4x4 homogeneous matrix with only the rotation part
    Args:
        q: The quaternion in the format (qw, qx, qy, qz)

    Returns: 4x4 homogeneous transformation matrix with only the 3x3 rotation matrix R
    \n
    [R 0]
    [0 0]
    """
    # Convert quaternion to homogeneous transformation matrix

    # Extract the values from Q
    q0 = q[0]
    q1 = q[1]
    q2 = q[2]
    q3 = q[3]
    if (q0 > 0):
        q0, q1, q2, q3 = -q0, -q1, -q2, -q3

    # First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)

    # Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)

    # Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1

    # Uncomment below to change the sign of the rotation matrix
    # r00, r11, r22 = -r00, -r11, -r22

    # 3x3 rotation matrix
    rot_matrix = np.array([[r00, r01, r02],
                           [r10, r11, r12],
                           [r20, r21, r22]])
    # print(rot_matrix)

    homo = np.eye(4)
    homo[:3, :3] = rot_matrix
    return homo


def homogeneous_to_q(m):
    """
        Takes a homogeneous matrix with a 3x3 Rotation matrix and outputs the quaternion from that rotation matrix.
        This function works with the rotation matrix being at the to pleft of the homogenous matrix like:\n
        [R ...]\n
        [... ...]
    Args:
        m: The homogeneous matrix

    Returns: The quaternion in the format [qw, qx, qy, qz].

    """
    tr = m[0][0] + m[1][1] + m[2][2]

    if tr > 0:
        S = ((tr + 1.0) ** 0.5) * 2  # S=4*qw
        qw = 0.25 * S
        qx = (m[2][1] - m[1][2]) / S
        qy = (m[0][2] - m[2][0]) / S
        qz = (m[1][0] - m[0][1]) / S
    elif (m[0][0] > m[1][1]) and (m[0][0] > m[2][2]):
        S = ((1.0 + m[0][0] - m[1][1] - m[2][2]) ** 0.5) * 2  # S=4*qx
        qw = (m[2][1] - m[1][2]) / S
        qx = 0.25 * S
        qy = (m[0][1] + m[1][0]) / S
        qz = (m[0][2] + m[2][0]) / S
    elif m[1][1] > m[2][2]:
        S = ((1.0 + m[1][1] - m[0][0] - m[2][2]) ** 0.5) * 2  # S=4*qy
        qw = (m[0][2] - m[2][0]) / S
        qx = (m[0][1] + m[1][0]) / S
        qy = 0.25 * S
        qz = (m[1][2] + m[2][1]) / S
    else:
        S = ((1.0 + m[2][2] - m[0][0] - m[1][1]) ** 0.5) * 2  # S=4*qz
        qw = (m[1][0] - m[0][1]) / S
        qx = (m[0][2] + m[2][0]) / S
        qy = (m[1][2] + m[2][1]) / S
        qz = 0.25 * S

    if (qw < 0):  # Change the quaternion sign if qw is negative to match the format of the output data
        qw = -qw
        qx = -qx
        qy = -qy
        qz = -qz
    return [qw, qx, qy, qz]


def relative_rotation(q1, q2):
    """
    Calculate the relative rotation between two quaternions, that is qrel = q2 * q1^-1

    Args:
    - q1: 4x1 numpy array (qw, qx, qy, qz)
    - q2: 4x1 numpy array (qw, qx, qy, qz)

    Returns:
    - relative_rotation: 4x1 numpy array quaternion (qw, qx, qy, qz)
    """
    # Find conjugate quaternion of q1 (q1^-1)
    q1_conj = np.array([q1[0], -q1[1], -q1[2], -q1[3]])

    # Multiply q2 by q1^-1
    relative_rotation = quat_multiply(q2, q1_conj)

    return relative_rotation


def rotate_quaternion(quaternion, rotation_quaternion):
    """
    Rotate the quaternion using the rotation quaternion

    Args:
    - quaternion: 4x1 numpy array (qw, qx, qy, qz)
    - rotation_quaternion: 4x1 numpy array (qw, qx, qy, qz)

    Returns:
    - rotated_quaternion: 4x1 numpy array (qw, qx, qy, qz)
    """
    # Multiply the quaternions
    rotated_quaternion = quat_multiply(rotation_quaternion, quaternion)

    return rotated_quaternion


def rotate_xyz(xyz, quaternion):
    """
    Rotate the acceleration vector using the quaternion

    Args:
    - xyz: 1x3 numpy array (ax, ay, az)
    - quaternion: 4x1 numpy array (qw, qx, qy, qz)

    Returns:
    - rotated_xyz: 3x1 numpy array (ax, ay, az)
    """
    # Transpose the xyz vector
    xyz = np.array(xyz).reshape(3, 1)
    rot_matrix = q_to_homogeneous(quaternion)[:3, :3]

    # Rotate the acceleration vector
    rotated_xyz = np.dot(rot_matrix, xyz)  # a_2 = R * a_1, where:
    # xyz is the original 1x3 xyz vector transposed to 3x1,
    # rot_matrix is the 3x3 rotation matrix derived by the quaternion
    # rotated_xyz is the 3x1 rotated xyz vector

    # Return the rotated xyz vector
    rotated_xyz = rotated_xyz.reshape(1, 3)

    return rotated_xyz.flatten()

def angular_acceleration(angular_velocity, angular_velocity_next, delta_t):
    """
    Calculate the angular acceleration using the angular velocity

    Args:
    - angular_velocity: 3x1 numpy array (wx, wy, wz)
    - angular_velocity_next: 3x1 numpy array (wx, wy, wz)
    - delta_t: float, time interval

    Returns:
    - angular_acceleration: 3x1 numpy array (w'x, w'y, w'z)
    """
    # Calculate the angular acceleration
    angular_acceleration = (angular_velocity_next - angular_velocity) / delta_t

    return angular_acceleration

def a_rot(ang_vel, ang_accel, accelerometer_offset):
    """
    Takes the angular velocity, angular acceleration, and accelerometer offset and returns the acceleration caused by rotation around a point with offset: accelerometer_offset
    Formula used: a_rot = w'*t + w*(w*t)
    Args:
        ang_vel: The angular velocity of the device in the format (wx, wy, wz)
        ang_accel: The angular acceleration of the device in the format (w'x, w'y, w'z)
        accelerometer_offset: The offset of the accelerometer in the format (tx, ty, tz)

    Returns:
        The acceleration caused by rotation around a point with offset: accelerometer_offset
    """
    a_rot = np.cross(ang_accel, accelerometer_offset) + np.cross(ang_vel, np.cross(ang_vel, accelerometer_offset))
    return a_rot


def transform_poses(poses, extrinsic_calibration, inverse_calibration=False, debug=False):
    """
    Transform poses using extrinsic calibration

    Args:
    - quaternions: Nx4 numpy array (qw, qx, qy, qz)
    - translations: Nx3 numpy array (px, py, pz)
    - extrinsic_calibration: 4x4 numpy array
    - inverse_calibration: boolean, whether to apply the inverse calibration (Default: False)
    - debug: boolean, whether to print debug information

    Returns:
    - transformed_poses: list of transformed poses in the format (px, py, pz, qw, qx, qy, qz)
    """
    transformed_poses = []
    i = 0
    for pose in poses:
        i += 1

        # Convert pose to homogeneous transformation matrix
        homo_pose = q_to_homogeneous(pose[3:7])
        if (inverse_calibration):
            homo_pose = np.linalg.inv(homo_pose)
        homo_pose[:3, 3] = pose[:3]

        # Apply extrinsic calibration
        transformed_homo_pose = np.dot(homo_pose, extrinsic_calibration)

        # Extract transformed pose
        transformed_pose = np.zeros(len(pose))
        transformed_pose[:3] = transformed_homo_pose[:3, 3]
        if (not inverse_calibration):
            transformed_homo_pose = np.linalg.inv(transformed_homo_pose)
        transformed_quaternion = homogeneous_to_q(transformed_homo_pose[:3, :3])
        transformed_pose[3:7] = transformed_quaternion

        if debug:
            print("pose\n", pose)
            print("homo pose\n", homo_pose)
            print("transformed homo pose\n", transformed_homo_pose)
            print("transformed_quaternion\n", transformed_quaternion)
            # # Do the inverse calculation just to test
            # # print(transformed_pose[3:7])
            back_to_initial_pose = q_to_homogeneous(transformed_quaternion)
            back_to_initial_pose = np.linalg.inv(back_to_initial_pose)
            print("back to initial pose\n", back_to_initial_pose)
            back_to_initial_pose[:3, 3] = transformed_pose[:3]
            extrinsic_calibration_inv = np.linalg.inv(
                extrinsic_calibration)  # Inverse of the extrinsic calibration matrix

            # transformed_back_to_initial_homo = np.dot(transformed_back_to_initial_homo, extrinsic_calibration_inv)
            transformed_back_to_initial_homo = np.dot(back_to_initial_pose, extrinsic_calibration_inv)
            transformed_quaternion = homogeneous_to_q(transformed_back_to_initial_homo[:3, :3])
            new_formatted_transformed_pose = np.zeros(len(pose))
            new_formatted_transformed_pose[:3] = transformed_back_to_initial_homo[:3, 3]
            new_formatted_transformed_pose[3:7] = transformed_quaternion
            # print(f"formatted transformed pose {i}\n", transformed_pose)
            print("transformed_quaternion\n", transformed_quaternion)
            # print("new pose\n", back_to_initial_pose)
            print("transformed back to init homo\n", transformed_back_to_initial_homo)
            print(f"new transformed pose {i}\n", new_formatted_transformed_pose)
            if i > 0:
                debug = False
                # break #This is for debugging purposes to get just the first element of the poses. Comment out for full run
                print("IMU coordinate system:", check_coordinate_system(homo_pose))
                print("Extrinsic calibration coordinate system:", check_coordinate_system(extrinsic_calibration))
                print("Transformed pose coordinate system:", check_coordinate_system(transformed_homo_pose))
                break
            if check_coordinate_system(homo_pose) != check_coordinate_system(extrinsic_calibration):
                print(f"Error: Coordinate systems do not match at line {i}")
                print("IMU coordinate system:", check_coordinate_system(homo_pose))
                print("Extrinsic calibration coordinate system:", check_coordinate_system(extrinsic_calibration))
                break

        transformed_pose[7:] = pose[7:]
        transformed_poses.append(transformed_pose)

    return np.array(transformed_poses)


def quat_multiply(q1, q2):
    """
    Multiplying two quaternions in the format (qx, qy, qz, qw).
    Essentially using the formula q1*q2 = (scalar1*scalar2 - dot(vector1, vector2), scalar1*vector2 + scalar2*vector1 + cross(vector1, vector2)

    Parameters: q1, q2 quaternions

    Returns: q1*q2
    """
    scalar1 = q1[3]
    scalar2 = q2[3]
    vector1 = q1[:3]
    vector2 = q2[:3]
    scal = scalar1 * scalar2 - np.dot(vector1, vector2)

    v1 = Vector3([vector1])
    v2 = Vector3([vector2])
    vect = np.dot(scalar1, v1) + np.dot(scalar2, v2) + np.cross(vector1, vector2)
    arr = np.zeros(4)
    arr[0] = scal
    arr[1:4] = vect
    print("arr:", arr)
    return arr
