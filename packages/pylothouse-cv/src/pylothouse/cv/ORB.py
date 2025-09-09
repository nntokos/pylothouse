
import cv2
import os
import csv
from nnmavutils import fileio
from nnmavcv import cvutils

def load_ts_keypoints_from_csv(csv_path:str, sort=True, delimiter=',', from_timestamp=0, to_timestamp=0, verbose=False):
    """
    Load the timestamps and keypoints from the CSV file in the format: timestamp, x, y, size, angle, response, octave, class_id
    Access the keypoints using the timestamp as the key.

    :param csv_path: Path to the CSV file.
    :type csv_path: str
    :param sort: If True, sort the timestamps - Default: True.
    :type sort: bool
    :param delimiter: Delimiter used in the CSV file - Default: ','.
    :type delimiter: str
    :param from_timestamp: Earliest timestamp to consider - Default: 0 (Does not have to be an existing timestamp).
    :type from_timestamp: int
    :param to_timestamp: Latest timestamp to consider - Default: 0, processes all (Does not have to be an existing timestamp).
    :type to_timestamp: int
    :param verbose: If True, print the keypoints - Default: False.
    :type verbose: bool

    :return: Dictionary of timestamps and keypoints: {timestamp: [cv2.KeyPoint, cv2.KeyPoint, ...], ...}
    :rtype: dict

    """
    print("Loading timestamps & keypoints...", end="")
    if to_timestamp == 0:
        to_timestamp = float('inf')
    _keypoints = {}
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")
    try:
        # from_ts_index = fileio.binary_position(file_path=csv_path, target=from_timestamp)
        old_timestamp = None
        prog_idx = 0
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            length = len(lines)
            # Position from_timestamp using binary search in lines
            from_ts_index = 0
            high = length
            while from_ts_index <= high:
                mid = (from_ts_index + high) // 2
                mid_timestamp = float(lines[mid].strip().split(delimiter)[0])
                if mid_timestamp < from_timestamp:
                    from_ts_index = mid + 1
                elif mid_timestamp > from_timestamp:
                    high = mid - 1
                else:
                    from_ts_index = mid
                    break

            # Find the index of the first timestamp greater than or equal to from_timestamp
            if from_ts_index > 0:
                while float(lines[from_ts_index-1].strip().split(delimiter)[0]) >= from_timestamp:
                    from_ts_index -= 1
            # Iterate through the lines and load the keypoints
            for i in range(from_ts_index, len(lines)):
                line = lines[i]
                if line.startswith('#'):
                    continue
                timestamp, x, y, size, angle, response, octave, class_id = map(float, line.strip().split(delimiter))
                timestamp = int(timestamp)
                # if timestamp < from_timestamp:
                #     continue
                if timestamp > to_timestamp:
                    break
                if timestamp not in _keypoints:
                    _keypoints[timestamp] = []
                if timestamp != old_timestamp:
                    old_timestamp = timestamp
                prog_idx += 1
                if verbose:
                    print(f"\n\tKeypoint: x={x}, y={y}, size={size}, angle={angle}, response={response}, octave={octave}, class_id={class_id}, {prog_idx} / {length}")
                else:
                    if prog_idx % 100 == 0:
                        print(f"\rLoading timestamps & keypoints... {prog_idx} / {length}", end="")
                _keypoints[timestamp].append(cv2.KeyPoint(x, y, size, angle, response, int(octave), int(class_id)))
        print(f"\nLoaded {len(_keypoints)} timestamps & keypoints\n")
        return _keypoints
    except Exception as e:
        print(f"Error: {e}")
        return e


def visualize_ORB_keypoints_from_file(images_dir, output_dir, keypoints_csv_path, from_timestamp=0, to_timestamp=0, max_frames=0, grayscale_images=False, verbose=False):
    """

    :param images_dir: Directory containing the images
    :param output_dir: Directory to save the images with ORB keypoints
    :param keypoints_csv_path: Path to the CSV file containing the keypoints in format: timestamp, x, y, size, angle, response, octave, class_id
    :param from_timestamp: Earliest timestamp to consider (Does not have to be an existing timestamp)
    :param to_timestamp: Earliest timestamp to consider (Does not have to be an existing timestamp)
    :param max_frames: Maximum number of frames to consider (Overrides to_timestamp)
    :param grayscale_images: Whether to load the images in grayscale
    :return: Writes the images with ORB keypoints to the output directory
    """
    print("Visualize ORB keypoints")
    if max_frames == 0:
        max_frames = float('inf')
    if to_timestamp == 0:
        to_timestamp = float('inf')
    _keypoints = load_ts_keypoints_from_csv(keypoints_csv_path, from_timestamp=from_timestamp, to_timestamp=to_timestamp, verbose=verbose)
    _keypoints = {k: v for k, v in _keypoints.items() if from_timestamp <= k <= to_timestamp}
    image_paths = cvutils.sorted_image_paths_from_directory(images_dir)

    frame_count = 0
    max_frames = min(max_frames, len(image_paths))
    print("Adding ORB keypoints to images...")

    for image_path in image_paths:
        frame_count += 1
        if frame_count >= max_frames:
            break
        print(f"\rProgress: {100 * frame_count / max_frames:.2f}%", end="")

        image = cvutils.load_image(image_path, grayscale=grayscale_images)
        timestamp = image_path.split('/')[-1].split('.')[0]
        if int(timestamp) not in _keypoints:
            continue
        image_with_keypoints = cv2.drawKeypoints(image, _keypoints[int(timestamp)], None, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        output_path = os.path.join(output_dir, f'{timestamp}.png')
        cv2.imwrite(output_path, image_with_keypoints)

    print(f"\rProgress: {100 * frame_count / max_frames:.2f}%")
    print(f"\nORB keypoints added to {frame_count} images")