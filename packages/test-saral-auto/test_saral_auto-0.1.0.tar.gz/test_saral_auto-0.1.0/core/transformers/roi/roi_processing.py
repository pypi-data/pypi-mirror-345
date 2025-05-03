"""
ROI Processing Module
--------------------
This module provides functions for processing and analyzing Regions of Interest (ROIs) in images.
"""

from typing import List, Dict, Tuple, Any

import numpy as np

def merge_rois_if_no_text(rois, min_text_length=1):
    """
    Merge ROIs if they don't contain text
    
    Args:
        rois: List of ROIs
        min_text_length: Minimum text length to consider an ROI as having text
        
    Returns:
        list: List of merged ROIs
    """
    i = 0
    while i < len(rois) - 1:  # Check until the second last ROI
        if not rois[i + 1]["text"]:  # If the next ROI has no text
            # Merge the next ROI into the current one
            rois[i]["right"] = max(rois[i]["right"], rois[i + 1]["right"])
            rois[i]["bottom"] = max(rois[i]["bottom"], rois[i + 1]["bottom"])
            # Remove the next ROI
            del rois[i + 1]
        else:
            i += 1  # Move to the next ROI
    return rois

def find_missed_strips(img, rois, page_roi_coords, strip_height=50):
    """
    Find missed strips in the image
    
    Args:
        img: Input image
        rois: List of ROI dictionaries
        page_roi_coords: Page ROI coordinates
        strip_height: Height of each strip
        
    Returns:
        list: List of missed strips as (top, bottom) tuples
    """
    # Get the page height
    page_height = page_roi_coords[2][1] - page_roi_coords[0][1]
    
    # Create a mask for the existing ROIs
    mask = np.zeros((img.shape[0], 1), dtype=np.uint8)
    
    for roi in rois:
        top = roi["top"]
        bottom = roi["bottom"]
        mask[top:bottom] = 255
    
    # Find gaps in the mask
    gaps = []
    in_gap = False
    gap_start = 0
    
    for y in range(page_roi_coords[0][1], page_roi_coords[2][1]):
        if mask[y, 0] == 0:
            if not in_gap:
                in_gap = True
                gap_start = y
        else:
            if in_gap:
                in_gap = False
                gap_end = y
                
                # Only consider gaps larger than the strip height
                if gap_end - gap_start > strip_height:
                    gaps.append((gap_start, gap_end))
    
    # If still in a gap at the end
    if in_gap:
        gaps.append((gap_start, page_roi_coords[2][1]))
    
    return gaps