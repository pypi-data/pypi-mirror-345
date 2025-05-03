"""
Math utility functions for document processing.
These functions are separated to avoid circular imports.
"""

import numpy as np
from typing import List


def matrix_intersection_area(bboxes1, bboxes2):
    """
    Compute the intersection areas between two sets of bounding boxes.

    Args:
        bboxes1: List of bounding boxes [x1, y1, x2, y2]
        bboxes2: List of bounding boxes [x1, y1, x2, y2]

    Returns:
        numpy.ndarray: Matrix of intersection areas, shape (len(bboxes1), len(bboxes2))
    """
    if not bboxes1 or not bboxes2:
        return np.zeros((len(bboxes1), len(bboxes2)))

    # Convert to arrays for vectorization
    bboxes1 = np.array(bboxes1)
    bboxes2 = np.array(bboxes2)

    # Reshape to allow broadcasting
    # Shape becomes (n, 1, 4) and (1, m, 4)
    bboxes1 = bboxes1[:, np.newaxis, :]
    bboxes2 = bboxes2[np.newaxis, :, :]

    # Compute coordinates of intersections
    x_min = np.maximum(bboxes1[..., 0], bboxes2[..., 0])
    y_min = np.maximum(bboxes1[..., 1], bboxes2[..., 1])
    x_max = np.minimum(bboxes1[..., 2], bboxes2[..., 2])
    y_max = np.minimum(bboxes1[..., 3], bboxes2[..., 3])

    # Compute areas (max with 0 to avoid negative areas)
    width = np.maximum(0, x_max - x_min)
    height = np.maximum(0, y_max - y_min)
    intersection_area = width * height

    return intersection_area


def matrix_distance(boxes1: List[List[float]], boxes2: List[List[float]]) -> np.ndarray:
    """
    Compute the distance matrix between two sets of bounding boxes.
    
    Args:
        boxes1: List of bounding boxes [x1, y1, x2, y2]
        boxes2: List of bounding boxes [x1, y1, x2, y2]
        
    Returns:
        numpy.ndarray: Matrix of distances, shape (len(boxes1), len(boxes2))
    """
    if len(boxes2) == 0:
        return np.zeros((len(boxes1), 0))
    if len(boxes1) == 0:
        return np.zeros((0, len(boxes2)))

    boxes1 = np.array(boxes1)  # Shape: (N, 4)
    boxes2 = np.array(boxes2)  # Shape: (M, 4)

    boxes1_centers = (boxes1[:, :2] + boxes1[:, 2:]) / 2 # Shape: (M, 2)
    boxes2_centers = (boxes2[:, :2] + boxes2[:, 2:]) / 2  # Shape: (M, 2)

    boxes1_centers = boxes1_centers[:, np.newaxis, :]  # Shape: (N, 1, 2)
    boxes2_centers = boxes2_centers[np.newaxis, :, :]  # Shape: (1, M, 2)

    distances = np.linalg.norm(boxes1_centers - boxes2_centers, axis=2)  # Shape: (N, M)
    return distances


def sort_text_lines(lines, tolerance=1.25):
    """
    Sort text lines in reading order.
    
    Args:
        lines: List of objects with a bbox property [x1, y1, x2, y2]
        tolerance: Vertical grouping tolerance
        
    Returns:
        List of lines sorted in reading order
    """
    # Sorts in reading order. Not 100% accurate, this should only
    # be used as a starting point for more advanced sorting.
    vertical_groups = {}
    for line in lines:
        group_key = round(line.bbox[1] / tolerance) * tolerance
        if group_key not in vertical_groups:
            vertical_groups[group_key] = []
        vertical_groups[group_key].append(line)

    # Sort each group horizontally and flatten the groups into a single list
    sorted_lines = []
    for _, group in sorted(vertical_groups.items()):
        sorted_group = sorted(group, key=lambda x: x.bbox[0])
        sorted_lines.extend(sorted_group)

    return sorted_lines 