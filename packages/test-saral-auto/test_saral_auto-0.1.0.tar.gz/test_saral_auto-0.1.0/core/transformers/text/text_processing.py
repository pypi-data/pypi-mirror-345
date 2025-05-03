"""
Text Processing Module
---------------------
This module provides functions for text detection and analysis in images.
"""

import cv2
import numpy as np
import pytesseract
from typing import Tuple, List, Dict, Any

def get_text_boundary(img):
    """
    Get the boundary of text in an image
    
    Args:
        img: Input image
        
    Returns:
        tuple: ((min_x, min_y), (max_x, max_y)) Boundary coordinates
    """
    # Convert to grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        # Return default values instead of infinity
        return ((0, 0), (min(img.shape[1], 10), min(img.shape[0], 10)))
    
    # Find the bounding box of all contours
    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = float("-inf"), float("-inf")
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)
    
    return ((min_x, min_y), (max_x, max_y))


def is_text_bold(image: np.ndarray) -> Tuple[bool, float]:
    """
    Determine if the font in the given image is bold.
    
    Args:
        image: Grayscale image of the text
        
    Returns:
        Tuple containing:
        - Boolean indicating if the font is bold
        - Ratio of white to black pixels
    """
    # Thresholding
    _, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

    # Dilation
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=1)

    # Difference
    diff = dilated - binary

    # Analysis
    white_pixels = np.sum(diff == 255)
    black_pixels = np.sum(binary == 255)

    if white_pixels == 0 or black_pixels == 0:
        return False, 0
        
    ratio = white_pixels / black_pixels
    return ratio < 0.27, ratio

def get_text_roi(circle: Tuple[int, int, int], img_width: int) -> Tuple[int, int, int, int]:
    """
    Get the ROI for text to the left of a circle.
    
    Args:
        circle: Tuple of (center_x, center_y, radius)
        img_width: Width of the image
        
    Returns:
        Tuple of (left, top, right, bottom) coordinates
    """
    (cx, cy, r) = circle
    left_bound = max(0, cx - r - 200)  # 200 pixels left to the circle
    right_bound = max(0, cx - r)  # right at the circle's left boundary
    top_bound = max(0, cy - r)
    bottom_bound = min(img_width, cy + r)

    return (left_bound, top_bound, right_bound, bottom_bound)

def get_text_rois_on_left_of_circle(circles, img):
    """
    Get text ROIs on the left of circles
    
    Args:
        circles: List of circles
        img: Input image
        
    Returns:
        tuple: (rois, img) where rois is a list of ROI coordinates and img is the processed image
    """
    rois = []
    
    for circle in circles:
        cx, cy, radius = circle
        
        # Define ROI on the left of the circle
        roi_left = max(0, cx - 300)
        roi_right = max(0, cx - radius - 10)
        roi_top = max(0, cy - radius - 10)
        roi_bottom = min(img.shape[0], cy + radius + 10)
        
        # Draw the ROI
        cv2.rectangle(img, (roi_left, roi_top), (roi_right, roi_bottom), (255, 0, 0), 2)
        
        # Store the ROI
        rois.append((roi_left, roi_top, roi_right, roi_bottom))
    
    return rois, img


def put_text_in_contour_center(img, contour, text, font_scale=0.5, color=(0, 0, 255), thickness=1):
    """
    Put text in the center of a contour
    
    Args:
        img: Input image
        contour: Contour
        text: Text to put
        font_scale: Font scale
        color: Text color
        thickness: Text thickness
        
    Returns:
        None (modifies the image in-place)
    """
    # Calculate the center of the contour
    M = cv2.moments(contour)
    
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        
        # Calculate text position
        text_x = cx - text_size[0] // 2
        text_y = cy + text_size[1] // 2
        
        # Put text
        cv2.putText(img, text, (text_x, text_y), font, font_scale, color, thickness)

def put_text_in_circle_center(img, circle, text, font_scale=0.5, color=(0, 0, 255), thickness=1):
    """
    Put text in the center of a circle
    
    Args:
        img: Input image
        circle: Circle (center, radius)
        text: Text to put
        font_scale: Font scale
        color: Text color
        thickness: Text thickness
        
    Returns:
        None (modifies the image in-place)
    """
    # Get circle center
    cx, cy, radius = circle
    
    # Get text size
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    # Calculate text position
    text_x = cx - text_size[0] // 2
    text_y = cy + text_size[1] // 2
    
    # Put text
    cv2.putText(img, text, (text_x, text_y), font, font_scale, color, thickness)