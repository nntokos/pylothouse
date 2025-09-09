import cv2
import numpy as np


def average_px_intensity(image, precision=5):
    """
    Calculate the average pixel intensity of the image
    :param image: image to calculate the average pixel intensity. Should be a grayscale image
    :return: average pixel intensity of the image
    """
    average_px_intensity = np.mean(image).round(precision)
    return average_px_intensity

def luminosity(image, precision=5):
    """
    Calculate the luminosity of the image
    :param image: image to calculate the luminosity. Should be a grayscale image
    :return: luminosity of the image
    """
    luminosity = np.sum(image).round(precision)
    return luminosity


def stdev_px_intensity(image, precision=5):
    """
    Calculate the standard deviation of the luminance of the image
    :param image: image to calculate the standard deviation of the luminance. Should be a grayscale image
    :return: standard deviation of the luminance of the image
    """
    stdev_px_intensity = np.std(image).round(precision)
    return stdev_px_intensity

def contrast_michelson(image, precision=5):
    """
    Calculate the contrast ratio of the image
    :param image: image to calculate the contrast ratio. Should be a grayscale image
    :return: contrast ratio of the image
    """
    L_max = np.max(image).round(precision)
    L_min = np.min(image).round(precision)
    # Clip values to prevent overflow
    L_max = np.clip(L_max, -1e10, 1e10)
    L_min = np.clip(L_min, -1e10, 1e10)
    if L_max + L_min == 0:
        return float('inf')
    
    contrast_ratio = ((L_max - L_min) / (L_max + L_min)).round(precision)
    return contrast_ratio

def contrast_ratio(image, precision=5):
    """
    Calculate the contrast ratio of the image
    :param image: image to calculate the contrast ratio. Should be a grayscale image
    :return: contrast ratio of the image
    """
    L_max = np.max(image).round(precision)
    L_min = np.min(image).round(precision)
    # Clip values to prevent overflow
    L_max = np.clip(L_max, -1e10, 1e10)
    L_min = np.clip(L_min, -1e10, 1e10)
    if L_min == 0:
        return float('inf')
    
    contrast_ratio = L_max / L_min
    return contrast_ratio


def lighting_uniformity_avg(image):
    """
    Calculate the lighting uniformity of the image
    :param image: image to calculate the lighting uniformity. Should be a grayscale image
    :return: lighting uniformity of the image
    """
    L_avg = np.mean(image)
    L_min = np.min(image)
    L_avg = np.clip(L_avg, -1e10, 1e10)
    L_min = np.clip(L_min, -1e10, 1e10)
    if L_avg == 0:
        return float('inf')  # or handle appropriately

    lighting_uniformity = L_min / L_avg
    return lighting_uniformity

