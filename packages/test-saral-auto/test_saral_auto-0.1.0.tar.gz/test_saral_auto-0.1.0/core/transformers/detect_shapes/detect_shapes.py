"""
Shape Detection Module
---------------------
This module provides functions for detecting and filtering shapes (rectangles, circles) in images.
"""

import cv2
import numpy as np
from typing import Tuple, List, Any
from pathlib import Path
import os

from core.transformers.text.text_processing import put_text_in_contour_center
from .detect_rect import detect_rectangles, DEFAULT_CONFIG

def visualize_concentric_rectangles(img, contours, filtered_contours):
    """
    Visualize the original contours and the filtered contours to show which concentric rectangles were removed.
    
    Args:
        img: Input image
        contours: Original list of contours
        filtered_contours: Filtered list of contours
        
    Returns:
        numpy.ndarray: Visualization image
    """
    # Create a copy of the image for visualization
    vis_img = img.copy()
    
    # Draw all original contours in blue (with transparency)
    all_contours_img = vis_img.copy()
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(all_contours_img, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue
    
    # Draw filtered contours in green
    filtered_img = vis_img.copy()
    for i, cnt in enumerate(filtered_contours):
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(filtered_img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green
        
        # Add enumeration
        cv2.putText(filtered_img, str(i+1), (x + w//2 - 10, y + h//2 + 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    # Create a side-by-side comparison
    h, w = img.shape[:2]
    comparison = np.zeros((h, w*2, 3), dtype=np.uint8)
    comparison[:, :w] = all_contours_img
    comparison[:, w:] = filtered_img
    
    # Add labels
    cv2.putText(comparison, "All Contours", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(comparison, "Filtered Contours", (w + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Display the comparison
    cv2.imwrite("concentric_rectangle_filtering.png", comparison)
    
    return comparison


def analyze_invalid_rectangle(contour_points):
    """
    Analyze contour points to determine if they might form a valid rectangle
    despite not having exactly 4 vertices.
    
    Args:
        contour_points: Array of contour points
        
    Returns:
        tuple: (is_valid, rectangle_points, rect_area) where is_valid is a boolean and 
               rectangle_points is the approximated rectangle points if valid and rect_area is the area of the rectangle    
    """
    # Check if we have enough points
    if len(contour_points) < 4:
        return False, None, None
    
    # Get the bounding rectangle
    x, y, w, h = cv2.boundingRect(contour_points)
    
    # Calculate area of the bounding rectangle
    rect_area = w * h
    
    # Calculate area of the original contour
    contour_area = cv2.contourArea(contour_points)
    
    # If the contour area is close to the rectangle area (>85%), it's likely a rectangle
    area_ratio = contour_area / rect_area if rect_area > 0 else 0
    
    # Check if the shape is approximately rectangular
    is_rectangular = area_ratio > 0.85
    
    # Check if the aspect ratio is reasonable for a form field
    aspect_ratio = float(w) / h if h > 0 else 0
    has_valid_aspect = 0.02 < aspect_ratio < 60.0
    
    # Check if the contour is convex
    is_convex = cv2.isContourConvex(contour_points)
    
    # Try to approximate the contour to see if we can get a rectangle
    epsilon = 0.02 * cv2.arcLength(contour_points, True)
    approx = cv2.approxPolyDP(contour_points, epsilon, True)
    
    # If approximation gives us 4 points, it's likely a rectangle
    is_approx_rect = len(approx) == 4
    
    # Determine if this is a valid rectangle
    is_valid = (is_rectangular and has_valid_aspect) or (is_convex and is_approx_rect)
    
    if is_valid:
        # If the approximation gives us 4 points, use those
        if is_approx_rect:
            rectangle_points = approx
        else:
            # Otherwise, use the bounding rectangle
            rectangle_points = np.array([
                [[x, y]],
                [[x + w, y]],
                [[x + w, y + h]],
                [[x, y + h]]
            ])
        return True, rectangle_points, rect_area
    
    return False, None, None

def filter_concentric_rectangles(contours, overlap_threshold=0.8, center_distance_threshold=20):
    """
    Filter out concentric rectangles by identifying overlapping rectangles with similar centers.
    
    Args:
        contours: List of contours
        overlap_threshold: Minimum overlap ratio to consider rectangles as concentric
        center_distance_threshold: Maximum distance between centers to consider rectangles as concentric
        
    Returns:
        list: Filtered list of contours with concentric rectangles removed
    """
    if len(contours) <= 1:
        return contours
    
    # Get bounding rectangles and centers for all contours
    bounding_rects = []
    centers = []
    areas = []
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        bounding_rects.append((x, y, w, h))
        centers.append((x + w/2, y + h/2))
        areas.append(w * h)
    
    # Create a list to mark contours to keep
    keep = [True] * len(contours)
    
    # Group concentric rectangles
    groups = []
    for i in range(len(contours)):
        if not keep[i]:
            continue
            
        current_group = [i]
        x1, y1, w1, h1 = bounding_rects[i]
        cx1, cy1 = centers[i]
        area1 = areas[i]
        
        for j in range(i+1, len(contours)):
            if not keep[j]:
                continue
                
            x2, y2, w2, h2 = bounding_rects[j]
            cx2, cy2 = centers[j]
            area2 = areas[j]
            
            # Calculate center distance
            center_distance = np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)
            
            # Calculate overlap area
            x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
            y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
            overlap_area = x_overlap * y_overlap
            
            # Calculate overlap ratio relative to the smaller rectangle
            smaller_area = min(area1, area2)
            overlap_ratio = overlap_area / smaller_area if smaller_area > 0 else 0
            
            # If rectangles are concentric
            if center_distance < center_distance_threshold and overlap_ratio > overlap_threshold:
                current_group.append(j)
                keep[j] = False
        
        if len(current_group) > 1:
            groups.append(current_group)
            # Mark the original rectangle as not to keep, we'll add back the best one
            keep[i] = False
    
    # For each group, keep only the rectangle with the median area
    filtered_contours = []
    
    for i in range(len(contours)):
        if keep[i]:
            filtered_contours.append(contours[i])
    
    # For each group, add back the contour with the median area
    for group in groups:
        group_areas = [areas[i] for i in group]
        # Find the index of the median area in the group
        median_area_idx = group[np.argsort(group_areas)[len(group_areas)//2]]
        filtered_contours.append(contours[median_area_idx])
    
    return filtered_contours

def detect_and_filter_rectangles(img):
    """
    Detect and filter rectangles in an image
    
    Args:
        img: Input image
        
    Returns:
        tuple: (contours, mean_area, result_img) where contours is a list of contours,
               mean_area is the mean area of the contours, and result_img is the processed image
    """
    # Use the standalone rectangle detection function
    return detect_rectangles(img, config=DEFAULT_CONFIG)


def detect_and_filter_circles(img, index=0):
    """
    Detect and filter circles in the image
    
    Args:
        img: Input image
        
    Returns:
        tuple: (circles, result_img) where circles is a list of circle contours
               and result_img is the processed image
    """
    # Convert to grayscale
    # # Apply Gaussian blur to reduce sharpness
    
    result_img = img.copy()
    
    result_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
     
    blurred = cv2.GaussianBlur(result_img, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # # # Use morphological closing to close small gaps
    kernel = np.ones((5, 5), np.uint8)
    result_img = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    print("Finding Circles now...")
    circles = cv2.HoughCircles(
        result_img, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=30, maxRadius=50
    )

    #print len only when it is not None
    if circles is not None:
        print("Circles Found", len(circles))

    valid_circles = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        # Filtering criteria for circles can go here
        valid_circles = circles

    # Order circles based on y-coordinate and then x-coordinate
    valid_circles = group_and_sort_circles(valid_circles)
    for circle in valid_circles:
        center = (circle[0], circle[1])
        radius = circle[2]
        print("circle", index, center, radius)
        index += 1

    print("Valid circles count", len(valid_circles))

    return valid_circles, img



def get_largest_rectangle_roi(img):
    """
    Get the largest rectangle ROI in the image
    
    Args:
        img: Input image
        
    Returns:
        list: List of corner points of the largest rectangle
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest contour
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Approximate the contour
        epsilon = 0.02 * cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)
        
        # If it's a rectangle (4 vertices)
        if len(approx) == 4:
            return approx.reshape(-1, 2).tolist()
        else:
            # Use the bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
    
    # If no contours found, use the entire image
    h, w = img.shape[:2]
    return [[0, 0], [w, 0], [w, h], [0, h]]

# HELPER FUNCTIONS
def group_and_sort_circles(circles):
    # First, sort the circles based on y-coordinate
    if not circles:
        return []
    circles_sorted = sorted(circles, key=lambda c: c[1])

    # Now, iterate through the sorted list and group circles with similar y-coordinates
    grouped_circles = []
    current_group = [circles_sorted[0]]
    for i in range(1, len(circles_sorted)):
        if abs(circles_sorted[i][1] - circles_sorted[i - 1][1]) <= 8:
            current_group.append(circles_sorted[i])
        else:
            grouped_circles.extend(sorted(current_group, key=lambda c: c[0]))
            current_group = [circles_sorted[i]]
    grouped_circles.extend(sorted(current_group, key=lambda c: c[0]))

    return grouped_circles

