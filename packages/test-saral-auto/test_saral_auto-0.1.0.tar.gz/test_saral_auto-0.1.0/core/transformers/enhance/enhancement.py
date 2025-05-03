"""
Image Enhancement Module
-----------------------
This module provides functions for enhancing and improving image quality.
"""

import cv2
import numpy as np
from typing import Tuple, Optional

def enhance_contrast(image: np.ndarray, clip_limit: float = 2.0, tile_size: int = 8) -> np.ndarray:
    """
    Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
    
    Args:
        image: Input image
        clip_limit: Threshold for contrast limiting
        tile_size: Size of grid for histogram equalization
        
    Returns:
        Enhanced image
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    cl = clahe.apply(l)
    
    # Merge channels and convert back to BGR
    enhanced = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced

def remove_noise(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    Remove noise from image using median blur.
    
    Args:
        image: Input image
        kernel_size: Size of the kernel for median blur
        
    Returns:
        Denoised image
    """
    return cv2.medianBlur(image, kernel_size)

def sharpen_image(image: np.ndarray, kernel_size: int = 3, sigma: float = 1.0) -> np.ndarray:
    """
    Sharpen image using unsharp masking.
    
    Args:
        image: Input image
        kernel_size: Size of the Gaussian kernel
        sigma: Standard deviation of the Gaussian kernel
        
    Returns:
        Sharpened image
    """
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
    
    # Unsharp masking
    sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)
    
    return sharpened

def adjust_brightness_contrast(
    image: np.ndarray,
    brightness: float = 0,
    contrast: float = 1.0
) -> np.ndarray:
    """
    Adjust image brightness and contrast.
    
    Args:
        image: Input image
        brightness: Brightness adjustment (-100 to 100)
        contrast: Contrast adjustment (0.0 to 3.0)
        
    Returns:
        Adjusted image
    """
    # Convert brightness to alpha and beta
    alpha = contrast
    beta = brightness
    
    # Apply adjustment
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    return adjusted 