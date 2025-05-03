# Contour Processing Utilities

A collection of utility functions for processing and manipulating contours in computer vision applications using OpenCV.

## Overview

This module provides functionality for:
- Grouping contours based on proximity of their bounding rectangles
- Selecting leftmost shapes (circles or rectangles) from groups of contours
- Creating contours from region of interest (ROI) coordinates

## Dependencies

- OpenCV (`cv2`)
- NumPy (`numpy`)

## Functions

### `group_contours(contours, threshold=6)`

Groups contours based on their bounding rectangles.

**Parameters:**
- `contours`: List of contours to be grouped
- `threshold`: Maximum distance between contours to be considered part of the same group (default: 6)

**Returns:**
- List of grouped contours represented as arrays

### `get_leftmost_shapes(contours, shape_type="circle")`

Gets the leftmost shapes for groups with y-coordinates within a range of 8 pixels.

**Parameters:**
- `contours`: List of contours
- `shape_type`: Either "circle" or "rectangle" (default: "circle")

**Returns:**
- List of leftmost contours for each y-coordinate group

### `create_contour_from_roi(roi_left, roi_top, roi_right, roi_bottom)`

Creates a contour from the specified region of interest (ROI) coordinates.

**Parameters:**
- `roi_left`: The left x-coordinate of the ROI
- `roi_top`: The top y-coordinate of the ROI
- `roi_right`: The right x-coordinate of the ROI
- `roi_bottom`: The bottom y-coordinate of the ROI

**Returns:**
- A contour represented as a numpy array

## Usage Example

```python
import cv2
import numpy as np
from transformers.contour import group_contours, get_leftmost_shapes, create_contour_from_roi

# Example: Grouping contours
image = cv2.imread('image.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Group the contours
grouped_contours = group_contours(contours)

# Get leftmost circles
leftmost_circles = get_leftmost_shapes(contours, "circle")

# Create a contour from ROI
roi_contour = create_contour_from_roi(100, 100, 200, 200)
```
