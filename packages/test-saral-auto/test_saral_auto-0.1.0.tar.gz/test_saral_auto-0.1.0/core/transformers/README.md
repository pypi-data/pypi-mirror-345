This will contain transformers of Image Processing, used in Saral

transformers/
├── align/
│   ├── auto_align.py                # Perspective transform to deskew and align document edges
│   ├── __init__.py
│   ├── [README.md](./align/README.md)                     # Documentation for the align module
├── binarize/
│   ├── adaptive_threshold.py        # Local adaptive thresholding
│   ├── otsu_threshold.py            # Otsu’s method
│   ├── __init__.py
│   ├── [README.md](./binarize/README.md)                     # Documentation for the binarize module
├── crop/
│   ├── crop_image.py                # General-purpose cropping based on bounding boxes
│   ├── __init__.py
│   ├── [README.md](./crop/README.md)                     # Documentation for the crop module
├── deskew/
│   ├── correct_skew.py              # Correct rotation/skew using Hough Transform or PCA
│   ├── __init__.py
│   ├── [README.md](./deskew/README.md)                     # Documentation for the deskew module
├── detect_lines/
│   ├── detect_horizontal.py         # Detect horizontal lines (e.g., for rows)
│   ├── detect_vertical.py           # Detect vertical lines (e.g., for columns)
│   ├── remove_lines.py              # Remove lines for cleaner OCR
│   ├── merge_lines.py               # Merge broken line segments (via dilation or heuristics)
│   ├── __init__.py
│   ├── [README.md](./detect_lines/README.md)                     # Documentation for the detect_lines module
├── detect_shapes/
│   ├── detect_circles.py            # Circle detection for radio buttons, stamps
│   ├── detect_rectangles.py         # Rectangle detection for form fields or boxes
│   ├── __init__.py
│   ├── [README.md](./detect_shapes/README.md)                     # Documentation for the detect_shapes module
├── enhance/
│   ├── enhance_image.py             # Image enhancement via histogram equalization
│   ├── __init__.py
│   ├── [README.md](./enhance/README.md)                     # Documentation for the enhance module
├── filter/
│   ├── filter_noise.py              # Gaussian filter
│   ├── filter_edges.py              # Canny or Sobel edge detection
│   ├── __init__.py
│   ├── [README.md](./filter/README.md)                     # Documentation for the filter module
├── layout/
│   ├── layout_grid.py               # Analyze spatial relationships between lines and boxes
│   ├── infer_table_structure.py     # Map detected lines to rows and columns
│   ├── merge_text_blocks.py         # Merge nearby text ROIs into logical blocks
│   ├── __init__.py
│   ├── [README.md](./layout/README.md)                     # Documentation for the layout module
├── morphology/
│   ├── dilate_erode.py              # Morph operations to close gaps between lines
│   ├── open_close.py                # For noise removal and line enhancement
│   ├── __init__.py
│   ├── [README.md](./morphology/README.md)                     # Documentation for the morphology module
├── roi/
│   ├── detect_roi.py                # Detect text blocks or tables
│   ├── process_roi.py               # Normalize ROI size/position
│   ├── __init__.py
│   ├── [README.md](./roi/README.md)                     # Documentation for the roi module
├── segment/
│   ├── segment_rows.py              # Use horizontal lines for row segmentation
│   ├── segment_cells.py             # Use grid logic to split into cells
│   ├── __init__.py
│   ├── [README.md](./segment/README.md)                     # Documentation for the segment module
├── text/
│   ├── extract_text.py              # OCR with preprocessed ROIs
│   ├── annotate_text.py             # Annotate OCR output on image
│   ├── __init__.py
│   ├── [README.md](./text/README.md)                     # Documentation for the text module
├── __init__.py
