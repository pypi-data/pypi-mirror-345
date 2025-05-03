"""
Layout Analysis Module
--------------------
This module provides functions for analyzing and processing document layouts.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any

def analyze_layout(image: np.ndarray) -> Dict[str, Any]:
    """
    Analyze the layout of a document image.
    
    Args:
        image: Input image as numpy array
        
    Returns:
        Dictionary containing layout analysis results including:
        - page_orientation: 'portrait' or 'landscape'
        - content_regions: List of content region coordinates
        - margins: Dictionary of margin sizes
        - text_blocks: List of detected text block coordinates
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Get image dimensions
    height, width = gray.shape
    
    # Determine page orientation
    page_orientation = 'portrait' if height > width else 'landscape'
    
    # Detect content regions using adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Find contours
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    # Filter and sort contours by area
    content_regions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:  # Minimum area threshold
            x, y, w, h = cv2.boundingRect(contour)
            content_regions.append((x, y, x + w, y + h))
    
    # Calculate margins
    if content_regions:
        left_margin = min(region[0] for region in content_regions)
        right_margin = width - max(region[2] for region in content_regions)
        top_margin = min(region[1] for region in content_regions)
        bottom_margin = height - max(region[3] for region in content_regions)
    else:
        left_margin = right_margin = top_margin = bottom_margin = 0
    
    margins = {
        'left': left_margin,
        'right': right_margin,
        'top': top_margin,
        'bottom': bottom_margin
    }
    
    # Detect text blocks using connected components
    _, labels = cv2.connectedComponents(thresh)
    text_blocks = []
    
    for label in range(1, np.max(labels) + 1):
        mask = (labels == label).astype(np.uint8) * 255
        x, y, w, h = cv2.boundingRect(mask)
        if w > 10 and h > 10:  # Minimum size threshold
            text_blocks.append((x, y, x + w, y + h))
    
    return {
        'page_orientation': page_orientation,
        'content_regions': content_regions,
        'margins': margins,
        'text_blocks': text_blocks
    }

def detect_columns(image: np.ndarray) -> List[Tuple[int, int]]:
    """
    Detect columns in a document image.
    
    Args:
        image: Input image as numpy array
        
    Returns:
        List of column boundaries as (left, right) coordinate pairs
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Project the image vertically
    vertical_projection = np.sum(thresh, axis=0)
    
    # Find valleys in the projection
    valleys = []
    for i in range(1, len(vertical_projection) - 1):
        if (vertical_projection[i] < vertical_projection[i-1] and
            vertical_projection[i] < vertical_projection[i+1]):
            valleys.append(i)
    
    # Group nearby valleys
    columns = []
    if valleys:
        current_group = [valleys[0]]
        for valley in valleys[1:]:
            if valley - current_group[-1] < 50:  # Maximum gap between columns
                current_group.append(valley)
            else:
                columns.append((current_group[0], current_group[-1]))
                current_group = [valley]
        columns.append((current_group[0], current_group[-1]))
    
    return columns 