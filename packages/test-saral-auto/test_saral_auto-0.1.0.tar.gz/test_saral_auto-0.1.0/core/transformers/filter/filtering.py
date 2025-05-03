"""
Image Filtering Module
---------------------
This module provides functions for filtering and processing images.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional

def apply_morphological_operations(
    image: np.ndarray,
    operation: str = 'close',
    kernel_size: int = 3,
    iterations: int = 1
) -> np.ndarray:
    """
    Apply morphological operations to an image.
    
    Args:
        image: Input image
        operation: Type of operation ('erode', 'dilate', 'open', 'close')
        kernel_size: Size of the kernel
        iterations: Number of iterations
        
    Returns:
        Processed image
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
    if operation == 'erode':
        return cv2.erode(image, kernel, iterations=iterations)
    elif operation == 'dilate':
        return cv2.dilate(image, kernel, iterations=iterations)
    elif operation == 'open':
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
    elif operation == 'close':
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    else:
        return image

def apply_threshold(
    image: np.ndarray,
    threshold_type: str = 'binary',
    threshold_value: int = 127,
    max_value: int = 255
) -> np.ndarray:
    """
    Apply thresholding to an image.
    
    Args:
        image: Input image
        threshold_type: Type of thresholding ('binary', 'binary_inv', 'trunc', 'tozero', 'tozero_inv')
        threshold_value: Threshold value
        max_value: Maximum value to use with binary thresholding
        
    Returns:
        Thresholded image
    """
    if threshold_type == 'binary':
        _, result = cv2.threshold(image, threshold_value, max_value, cv2.THRESH_BINARY)
    elif threshold_type == 'binary_inv':
        _, result = cv2.threshold(image, threshold_value, max_value, cv2.THRESH_BINARY_INV)
    elif threshold_type == 'trunc':
        _, result = cv2.threshold(image, threshold_value, max_value, cv2.THRESH_TRUNC)
    elif threshold_type == 'tozero':
        _, result = cv2.threshold(image, threshold_value, max_value, cv2.THRESH_TOZERO)
    elif threshold_type == 'tozero_inv':
        _, result = cv2.threshold(image, threshold_value, max_value, cv2.THRESH_TOZERO_INV)
    else:
        result = image
    
    return result

def apply_adaptive_threshold(
    image: np.ndarray,
    method: str = 'gaussian',
    block_size: int = 11,
    c: int = 2
) -> np.ndarray:
    """
    Apply adaptive thresholding to an image.
    
    Args:
        image: Input image
        method: Adaptive thresholding method ('mean', 'gaussian')
        block_size: Size of a pixel neighborhood
        c: Constant subtracted from the mean or weighted mean
        
    Returns:
        Thresholded image
    """
    if method == 'mean':
        return cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, c
        )
    elif method == 'gaussian':
        return cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c
        )
    else:
        return image

def apply_gaussian_blur(
    image: np.ndarray,
    kernel_size: int = 5,
    sigma_x: float = 0,
    sigma_y: Optional[float] = None
) -> np.ndarray:
    """
    Apply Gaussian blur to an image.
    
    Args:
        image: Input image
        kernel_size: Size of the kernel (must be odd)
        sigma_x: Standard deviation in X direction
        sigma_y: Standard deviation in Y direction (if None, same as sigma_x)
        
    Returns:
        Blurred image
    """
    if sigma_y is None:
        sigma_y = sigma_x
    
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma_x, sigma_y) 