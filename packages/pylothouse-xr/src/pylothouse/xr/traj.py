import numpy as np

def load_poses(file_path):
    """
    Load poses from file with format [timestamp, [pose]].
    \b
    Typically the [pose] has the format [px, py, pz, qw, qx, qy, qz] OR [qw, qx, qy, qz, px, py, pz]

    :param file_path: The path to the file containing the poses
    :type file_path: str

    :return: Two numpy arrays containing the timestamps and poses loaded from the file
    """
    # Load dataset from file using readlines
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Parse lines to extract timestamps and poses
    timestamps = []
    poses = []
    for line in lines:
        if line.startswith('#'):
            continue
        data = line.strip().split(', ')
        try:
            ts = float(data[0])
        except Exception as e:
            print(e)
            continue

        timestamps.append(ts)
        poses.append(list(map(float, data[2:])))
    return np.array(timestamps), np.array(poses)

