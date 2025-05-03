"""
Line Detection Module
--------------------
This module provides functions for detecting and processing lines in images.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional

def detect_hough_lines(
    image: np.ndarray,
    rho: float = 1,
    theta: float = np.pi/180,
    threshold: int = 100,
    min_line_length: int = 50,
    max_line_gap: int = 20
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Detect lines in an image using Hough Transform.
    
    Args:
        image: Input image
        rho: Distance resolution in pixels
        theta: Angle resolution in radians
        threshold: Minimum number of votes
        min_line_length: Minimum line length
        max_line_gap: Maximum allowed gap between line segments
        
    Returns:
        List of lines as ((x1, y1), (x2, y2)) coordinate pairs
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Detect lines using Hough Transform
    lines = cv2.HoughLinesP(
        edges, rho, theta, threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap
    )
    
    if lines is None:
        return []
    
    # Convert lines to coordinate pairs
    return [((x1, y1), (x2, y2)) for x1, y1, x2, y2 in lines.reshape(-1, 4)]

def detect_horizontal_lines(
    image: np.ndarray,
    angle_threshold: float = 10.0,
    **kwargs
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Detect horizontal lines in an image.
    
    Args:
        image: Input image
        angle_threshold: Maximum angle deviation from horizontal (in degrees)
        **kwargs: Additional arguments for detect_hough_lines
        
    Returns:
        List of horizontal lines as ((x1, y1), (x2, y2)) coordinate pairs
    """
    lines = detect_hough_lines(image, **kwargs)
    
    # Filter for horizontal lines
    horizontal_lines = []
    for (x1, y1), (x2, y2) in lines:
        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
        if angle < angle_threshold or angle > 180 - angle_threshold:
            horizontal_lines.append(((x1, y1), (x2, y2)))
    
    return horizontal_lines

def detect_vertical_lines(
    image: np.ndarray,
    angle_threshold: float = 10.0,
    **kwargs
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Detect vertical lines in an image.
    
    Args:
        image: Input image
        angle_threshold: Maximum angle deviation from vertical (in degrees)
        **kwargs: Additional arguments for detect_hough_lines
        
    Returns:
        List of vertical lines as ((x1, y1), (x2, y2)) coordinate pairs
    """
    lines = detect_hough_lines(image, **kwargs)
    
    # Filter for vertical lines
    vertical_lines = []
    for (x1, y1), (x2, y2) in lines:
        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
        if 90 - angle_threshold < angle < 90 + angle_threshold:
            vertical_lines.append(((x1, y1), (x2, y2)))
    
    return vertical_lines

def merge_nearby_lines(
    lines: List[Tuple[Tuple[int, int], Tuple[int, int]]],
    distance_threshold: float = 20.0,
    angle_threshold: float = 10.0
) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Merge nearby and similar lines.
    
    Args:
        lines: List of lines as ((x1, y1), (x2, y2)) coordinate pairs
        distance_threshold: Maximum distance between lines to merge
        angle_threshold: Maximum angle difference between lines to merge
        
    Returns:
        List of merged lines
    """
    if not lines:
        return []
    
    # Calculate line parameters (angle and distance from origin)
    line_params = []
    for (x1, y1), (x2, y2) in lines:
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        distance = np.abs((y2 - y1) * x1 - (x2 - x1) * y1) / np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        line_params.append((angle, distance, (x1, y1), (x2, y2)))
    
    # Group similar lines
    groups = []
    for angle, distance, line in line_params:
        matched = False
        for group in groups:
            if (abs(group[0] - angle) < angle_threshold and
                abs(group[1] - distance) < distance_threshold):
                group[2].append(line)
                matched = True
                break
        if not matched:
            groups.append([angle, distance, [line]])
    
    # Merge lines in each group
    merged_lines = []
    for angle, distance, group_lines in groups:
        if not group_lines:
            continue
        
        # Find the longest line in the group
        longest_line = max(group_lines, key=lambda line: np.sqrt(
            (line[1][0] - line[0][0])**2 + (line[1][1] - line[0][1])**2
        ))
        merged_lines.append(longest_line)
    
    return merged_lines

def draw_lines(
    image: np.ndarray,
    lines: List[Tuple[Tuple[int, int], Tuple[int, int]]],
    color: Tuple[int, int, int] = (0, 0, 255),
    thickness: int = 2
) -> np.ndarray:
    """
    Draw lines on an image.
    
    Args:
        image: Input image
        lines: List of lines to draw
        color: Line color
        thickness: Line thickness
        
    Returns:
        Image with lines drawn
    """
    result = image.copy()
    for (x1, y1), (x2, y2) in lines:
        cv2.line(result, (x1, y1), (x2, y2), color, thickness)
    return result 