import cv2
import numpy as np


def group_contours(contours, tolerance=10):
    """
    Group similar contours together
    
    Args:
        contours: List of contours
        tolerance: Distance tolerance for grouping
        
    Returns:
        list: List of grouped contours
    """
    if not contours:
        return []
    
    # Convert contours to bounding rectangles
    bounding_rects = [cv2.boundingRect(cnt) for cnt in contours]
    
    # Group similar rectangles
    grouped_indices = []
    used_indices = set()
    
    for i, (x1, y1, w1, h1) in enumerate(bounding_rects):
        if i in used_indices:
            continue
        
        current_group = [i]
        used_indices.add(i)
        
        for j, (x2, y2, w2, h2) in enumerate(bounding_rects):
            if j in used_indices:
                continue
            
            # Check if rectangles are similar
            if (abs(x1 - x2) < tolerance and 
                abs(y1 - y2) < tolerance and 
                abs(w1 - w2) < tolerance and 
                abs(h1 - h2) < tolerance):
                current_group.append(j)
                used_indices.add(j)
        
        grouped_indices.append(current_group)
    
    # For each group, use the first contour
    result = [contours[group[0]] for group in grouped_indices]
    
    return result



def get_leftmost_shapes(contours, shape_type="rectangle"):
    if not contours:
        return []
    """
    Get the leftmost shapes from a list of contours
    
    Args:
        contours: List of contours
        shape_type: Type of shape ("rectangle" or "circle")
        
    Returns:
        list: List of leftmost contours
    """
        # Extract the center of each shape based on its type
    if shape_type == "circle":
        centers = [
            (int(x), int(y))
            for cnt in contours
            for (x, y), radius in [cv2.minEnclosingCircle(cnt)]
        ]
    else:  # shape_type == "rectangle"
        centers = [
            (x + w // 2, y + h // 2)
            for cnt in contours
            for x, y, w, h in [cv2.boundingRect(cnt)]
        ]

    # Sort the centers based on y-coordinate
    sorted_indices = sorted(range(len(centers)), key=lambda k: centers[k][1])

    # Group centers with similar y-coordinates
    groups = []
    current_group = [sorted_indices[0]]
    for i in range(1, len(sorted_indices)):
        if abs(centers[sorted_indices[i]][1] - centers[sorted_indices[i - 1]][1]) <= 8:
            current_group.append(sorted_indices[i])
        else:
            groups.append(current_group)
            current_group = [sorted_indices[i]]
    if current_group:
        groups.append(current_group)

    # Find the leftmost contour in each group
    leftmost_contours = [
        contours[group[min(range(len(group)), key=lambda k: centers[group[k]][0])]]
        for group in groups
    ]

    return leftmost_contours


def create_contour_from_roi(left, top, right, bottom):
    """
    Create a contour from ROI coordinates
    
    Args:
        left: Left coordinate
        top: Top coordinate
        right: Right coordinate
        bottom: Bottom coordinate
        
    Returns:
        numpy.ndarray: Contour points
    """
    # Create a rectangle contour from the ROI coordinates
    points = np.array([
        [left, top],
        [right, top],
        [right, bottom],
        [left, bottom]
    ], dtype=np.int32)
    
    # Reshape to the format expected by OpenCV functions
    return points.reshape((-1, 1, 2))