import cv2
import os
import json
from nnmavutils import fileio
import numpy as np
from _internal import _helpers

# Load/Save utilities
def load_image(image_path, grayscale=False, to_rgb=False):
    """

    :param image_path: Path to the image file.
    :param grayscale: Boolean flag to read the image in grayscale. (Default: False)
    :param to_rgb: Boolean flag to convert the image to RGB. Only applicable if grayscale is True. (Default: False)
    :return:
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image {image_path} does not exist.")
    if grayscale:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    else:
        image = cv2.imread(image_path)

    if image is None:
        print(f"Error reading {image_path}")
        return None

    if grayscale and to_rgb:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    return image

def load_image_with_timestamp(images_dir, timestamp, format='png', grayscale=False, to_rgb=False):
    if not os.path.exists(images_dir):
        raise FileNotFoundError(f"Directory {images_dir} does not exist.")
    if not format in ['png', 'jpg', 'jpeg']:
        raise ValueError("Invalid image format. Supported formats: ['png', 'jpg', 'jpeg']")
    image_path = os.path.join(images_dir, f"{timestamp}.png")

    return load_image(image_path, grayscale=grayscale, to_rgb=to_rgb)



def sorted_timestamps_from_csv(csv_path:str, column_index=0, from_timestamp=0, to_timestamp=0, delimiter=','):
    """

    :param csv_path: Path to the CSV file.
    :type csv_path: str
    :param column_index: Column index of the timestamps - Default: 0.
    :type column_index: int
    :param from_timestamp: The earliest timestamp to consider - Default: 0 (Does not have to be an existing timestamp).
    :type from_timestamp: int
    :param to_timestamp: The latest timestamp to consider - Default: 0, processes all (Does not have to be an existing timestamp).
    :type to_timestamp: int
    :param delimiter: CSV delimiter - Default: ','.
    :type delimiter: str
    :return: Sorted timestamps from the CSV file.
    :rtype: list
    """
    timestamps = fileio.load_column_from_file(csv_path, column=column_index, from_number=from_timestamp, to_number=to_timestamp, delimiter=delimiter, out_type=int)
    timestamps.sort()
    return timestamps


def image_paths_from_directory(directory, extensions=('.png', '.jpg', '.jpeg')):
    """
    :param directory: Directory containing images.
    :param extensions: Extensions of the images to be considered. (Default: ('.png', '.jpg', '.jpeg'))
    :return: List of image paths.
    """
    image_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extensions)]
    if not image_paths:
        raise FileNotFoundError("No images found in the directory.")
    return image_paths

def sorted_image_paths_from_directory(directory, extensions=('.png', '.jpg', '.jpeg')):
    """
    :param directory: Directory containing images.
    :param extensions: Extensions of the images to be considered. (Default: ('.png', '.jpg', '.jpeg'))
    :return: Sorted list of image paths.
    """
    image_paths = image_paths_from_directory(directory, extensions)
    image_paths.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    return image_paths

# Basic image processing utilities

def draw_point_on_image(image, point, color=(0, 0, 255), radius=2):
    """
    Draw a point on an image.

    :param image: Input image.
    :type image: numpy.ndarray
    :param point: Point to be drawn on the image.
    :type point: tuple
    :param color: Color of the point in BGR format. (Default: (0, 0, 255))
    :type color: tuple
    :return: Image with point drawn.
    :rtype: numpy.ndarray

    """
    if isinstance(point, list) or isinstance(point, np.ndarray) or isinstance(point, tuple):
        center = [int(point[0]), int(point[1])]
    else:
        raise ValueError(_helpers.func_str(draw_point_on_image, "Invalid point. Expected a list, tuple, or numpy array of two integers (x, y)"))
    return cv2.circle(image, center, radius=radius, color=color, thickness=-1)



def draw_quad_on_image(image, quad, color=(0, 255, 0), thickness=2, fill=False, fill_color=(0, 255, 0)):
    """
    Draw a quadrilateral on an image.

    :param image: Input image.
    :type image: numpy.ndarray
    :param quad: List of four points representing the quadrilateral.
    :type quad: list
    :param color: Color of the quadrilateral in BGR format. (Default: (0, 255, 0))
    :type color: tuple
    :param thickness: Thickness of the lines. (Default: 2)
    :type thickness: int
    :param fill: Fill the quadrilateral with the fill color. (Default: False)
    :type fill: bool
    :param fill_color: Fill color of the quadrilateral in BGR format. (Default: (0, 255, 0))
    :type fill_color: tuple
    :return: Image with quadrilateral drawn.
    :rtype: numpy.ndarray

    """
    quad = np.array(quad, np.int32)
    if fill:
        cv2.fillPoly(image, [quad], color=fill_color)
    else:
        cv2.polylines(image, [quad], isClosed=True, color=color, thickness=thickness)
    return image

def draw_pgram_on_image(image, x, y, w, h, color=(0, 255, 0), thickness=2, fill=False, fill_color=(0, 255, 0)):
    pgram = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    return draw_quad_on_image(image, pgram, color=color, thickness=thickness, fill=fill, fill_color=fill_color)


def write_text_on_image(image, text, row=1, position='topleft', font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, font_color=(255, 255, 255), line_type=2, background_color:tuple=None):
    """
    Add text to an image.

    :param image: Input image.
    :type image: numpy.ndarray
    :param text: Text to be added to the image.
    :type text: str
    :param row: Row number for the text. (Default: 1). For bottom positions, row is counted from the bottom.
    :type row: int
    :param position: Position of the text. (Default: 'topleft'). Options: ['topleft', 'topright', 'bottomleft', 'bottomright']. Position can also be a tuple or list of coordinates (x, y)
    :type position: str
    :param font: Font type. (Default: cv2.FONT_HERSHEY_SIMPLEX)
    :type font: int
    :param font_scale: Font scale factor. (Default: 1)
    :type font_scale: float
    :param font_color: Font color in BGR format. (Default: (0, 0, 255))
    :type font_color: tuple
    :param line_type: Type of line. (Default: 2)
    :type line_type: int
    :return: Image with text added.
    :rtype: numpy.ndarray

    """
    _padding = 15
    text_size = cv2.getTextSize(text, font, font_scale, line_type)
    if isinstance(position, tuple) or isinstance(position, list):
        posX = position[0]
        posY = position[1]
    else:
        if not position in ['topleft', 'topright', 'bottomleft', 'bottomright']:
            raise ValueError(_helpers.func_str(write_text_on_image, f"Invalid position parameter: {position}. Options: ['topleft', 'topright', 'bottomleft', 'bottomright'] or tuple/list of coordinates (x, y)"))
        if position == 'topleft' or position == 'bottomleft': # Left/Right
            posX = _padding
        else:
            posX = image.shape[1] - text_size[0][0] - _padding
        if position == 'topleft' or position == 'topright': # Top/Bottom
            posY = text_size[0][1] * row + _padding*row
        else:
            posY = image.shape[0] - text_size[0][1] * row - _padding*row
    if background_color != None:
        if len(background_color) != 3:
            raise ValueError(_helpers.func_str(write_text_on_image, "Invalid background color. Expected a tuple of 3 integers (B, G, R)"))
        else:
            draw_pgram_on_image(image, posX, posY-text_size[0][1]-_padding/2, text_size[0][0], text_size[0][1]+_padding, color=background_color, fill=True, fill_color=background_color, thickness=-1)
    coordinates = (posX, posY)
    cv2.putText(image, text, coordinates, font, font_scale, font_color, line_type)
    return image


def write_filenames_on_images(images_directory, row=1, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, font_color=(255, 255, 255), line_type=2):
    """
    Write filenames on images in a directory.

    :param images_directory: Directory containing images.
    :type images_directory: str
    :param row: Row number for the text. (Default: 1)
    :type row: int
    :param font: Font type. (Default: cv2.FONT_HERSHEY_SIMPLEX)
    :type font: int
    :param font_scale: Font scale factor. (Default: 1)
    :type font_scale: float
    :param font_color: Font color in BGR format. (Default: (0, 0, 255))
    :type font_color: tuple
    :param line_type: Type of line. (Default: 2)
    :type line_type: int
    :return: Writes filenames on images in the directory.
    :rtype: None

    """
    image_paths = sorted_image_paths_from_directory(images_directory)
    for image_path in image_paths:
        image = cv2.imread(image_path)
        image = write_text_on_image(image, os.path.basename(image_path), row=row, font=font, font_scale=font_scale, font_color=font_color, line_type=line_type)
        cv2.imwrite(image_path, image)
    print(f"File names written on images in {images_directory}")


def compress_image(image, quality=50, output_path=None):
    """
    Compress an image.

    :param image: Input image.
    :type image: numpy.ndarray
    :param quality: Quality of the compressed image. (Default: 50)
    :type quality: int
    :param output_path: Output path for the compressed image. If None, the image is not saved. (Default: None)
    :type output_path: str
    :return: Compressed image.
    :rtype: numpy.ndarray

    """
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encoded_image = cv2.imencode('.jpg', image, encode_params)
    if not result:
        raise ValueError("Error compressing the image.")
    compressed_image = cv2.imdecode(encoded_image, 1)
    if output_path:
        cv2.imwrite(output_path, compressed_image)
    return compressed_image


# Video processing utilities
def create_video_from_timestamped_images(images_directory, output_video_file, fps, quality=100, verbose=True):
    """
    Create a video from a directory containing images named with their timestamps as <timestamp>.extension. Allowed image formats: [.png, .jpg, and .jpeg].

    :param images_directory: Directory containing input images for creating the video. Images should be named with their timestamps (<timestamp>.png).
    :type images_directory: str
    :param output_video_file: Path and filename of the output video. The extension determines the video format. Available formats: ['mp4', 'mov', 'avi', 'mkv']. Codecs: ['mp4': mp4v, 'mov': avc1, 'avi': XVID, 'mkv': X264]
    :type output_video_file: str
    :param fps: Frames per second for the video.
    :type fps: int
    :param quality: Quality of the compressed images. (Default: 100, uncompressed).
    :type quality: int
    :param verbose: Print progress messages. (Default: True)
    :type verbose: bool
    :return: Writes all images into a video.
    :rtype: None

    """
    quality = int(quality)
    if quality < 0 or quality > 100:
        raise ValueError(_helpers.func_str(create_video_from_timestamped_images, "Quality should be between 0 and 100"))

    # Get sorted list of all images in the directory
    image_paths = sorted_image_paths_from_directory(images_directory)

    # Read the first image to get the size
    first_image = cv2.imread(image_paths[0])
    height, width, layers = first_image.shape
    size = (width, height)
    fps = float(fps)

    # Check existence of the output directory. If not, create it.
    output_directory = os.path.dirname(output_video_file)
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Define the codec and create VideoWriter object based on file extension
    if output_video_file.endswith('.mp4'):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    elif output_video_file.endswith('.mov'):
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Codec for MOV
    elif output_video_file.endswith('.avi'):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for AVI
    elif output_video_file.endswith('.mkv'):
        fourcc = cv2.VideoWriter_fourcc(*'X264')  # Codec for MKV
    else:
        raise ValueError("Unsupported file format. Please use [.mp4, .mov, .avi, or .mkv] as the extension for the output video file")

    # Define the codec and create VideoWriter object
    out = cv2.VideoWriter(output_video_file, fourcc, fps, size)

    if verbose:
        print(f"Creating video from {len(image_paths)} images at {fps} fps. Source: {images_directory}")

    # Progress
    _total_images = len(image_paths)
    _image_counter = 0
    # Process each image and write to the video
    for image_path in image_paths:
        img = cv2.imread(image_path)
        if quality < 100:
            img = compress_image(img, quality=quality)
        out.write(img)
        _image_counter += 1
        print(f"[create_video_from_timestamped_images]: Processed {_image_counter} of {_total_images} images", end="\r")

    # Release the VideoWriter object
    out.release()
    print(f"Video saved as {output_video_file}")

# ML, DL utilities

def load_timestamped_bounding_boxes_from_file(file_path, from_timestamp=0, to_timestamp=0):
    """
    Load bounding boxes from a file containing timestamps and bounding boxes. The file should be in JSON format with timestamps as keys and bounding boxes as values that include the confidence.

    :param file_path: Path to the file containing timestamps and bounding boxes.
    :type file_path: str
    :return: Dictionary with timestamps as keys and bounding boxes as values. Format {timestamp: [bbox1, bbox2, ...]}
    :rtype: dict

    """
    if to_timestamp <= 0:
        to_timestamp = float('inf')
    timestamped_bboxes = {}
    with open(file_path, 'r') as f:
        data = json.load(f)
        sorted_timestamps = sorted([int(timestamp) for timestamp in data.keys()])

    length = len(sorted_timestamps)
    prog_idx = 0
    for timestamp in sorted_timestamps:
        if timestamp < from_timestamp:
            continue
        if timestamp > to_timestamp:
            continue
        timestamped_bboxes[timestamp] = data[str(timestamp)]
        prog_idx += 1
        print(f"Loading Detections: {prog_idx}/{length}", end="\r")
    print(f"\nLoaded {len(timestamped_bboxes)} detections from {file_path}\n")
    return timestamped_bboxes

def remove_color_from_image(image_path, target_color, output_path):
    """
    Removes all pixels of a given color from an image and saves the result.

    Parameters:
        image_path (str): Path to the input image.
        target_color (tuple): The BGR color to remove (e.g., (255, 255, 255) for white).
        output_path (str): Path to save the modified image.
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    # Convert the image to the desired color space if needed (e.g., BGR to HSV)
    # target_color should be in BGR format

    # Create a mask for the target color
    lower_bound = np.array(target_color) - 1  # Slight tolerance below the color
    upper_bound = np.array(target_color) + 1  # Slight tolerance above the color
    mask = cv2.inRange(image, lower_bound, upper_bound)

    # Remove the target color by setting it to black (or transparent)
    image[mask == 255] = [0, 0, 0]  # Set the color to black

    # Save the modified image
    cv2.imwrite(output_path, image)

    print(f"Modified image saved at {output_path}")
