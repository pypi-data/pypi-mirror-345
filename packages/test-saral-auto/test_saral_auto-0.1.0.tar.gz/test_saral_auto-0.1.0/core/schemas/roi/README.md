# ROI (Region of Interest) Schemas

This folder contains the schemas for defining and working with Regions of Interest (ROIs) in documents.

## Overview

These schemas provide structured representations for text regions and cells found in document processing tasks.

## Schemas

### ROI Schema (`roi.py`)

The `ROI` class represents a text region in a document.

**Properties:**
- `left`, `top`, `right`, `bottom`: Coordinates defining the region's boundaries
- `text`: Text content found in the region
- `textSize`: Size of the text in pixels
- `isBold`: Whether the text is bold
- `boldRatio`: Ratio of bold characters to total characters
- `confidence`: Optional confidence score for text recognition
- `type`: Optional type classification (e.g., header, field, label)
- `group_id`: Optional group ID for related ROIs

**Computed Properties:**
- `width`: Width of the ROI (right - left)
- `height`: Height of the ROI (bottom - top)
- `area`: Area of the ROI (width * height)
- `center`: Center coordinates as tuple (x, y)

**Methods:**
- `to_dict()`: Converts ROI to dictionary for serialization

### ROIList Schema (`roi.py`)

The `ROIList` class represents a collection of ROIs in a document.

**Properties:**
- `rois`: List of ROI objects

**Methods:**
- `from_list(roi_list)`: Class method to create ROIList from a list of dictionaries
- `to_dict()`: Converts ROIList to dictionary for serialization
- `filter_by_type(roi_type)`: Returns new ROIList filtered by ROI type
- `filter_by_group(group_id)`: Returns new ROIList filtered by group ID

### Cell Schema (`cell.py`)

The `Cell` class represents a cell containing text in the document.

**Properties:**
- `id`: Cell identifier
- `x`, `y`, `width`, `height`: Raw coordinates and dimensions
- `text`: Cell text content
- `orientation`: Text orientation
- `is_printed`: Whether text is printed (vs handwritten)
- `confidence`: Dictionary of confidence scores
- `normalized`: Normalized cell coordinates (NormalizedCell object)
- `metadata`: Cell metadata (CellMetadata object)

**Methods:**
- `to_dict()`: Converts cell to dictionary for serialization

### NormalizedCell Schema (`cell.py`)

The `NormalizedCell` class represents normalized coordinates for a cell.

**Properties:**
- `x`, `y`, `width`, `height`: Normalized coordinates and dimensions

### CellMetadata Schema (`cell.py`)

The `CellMetadata` class represents metadata for a cell.

**Properties:**
- `is_header`: Whether the cell is a header
- `row_id`: Row identifier
- `group_id`: Group identifier

### CellList Schema (`cell.py`)

The `CellList` class represents a collection of cells in a document.

**Properties:**
- `cells`: List of Cell objects

**Methods:**
- `from_list(cell_list)`: Class method to create CellList from a list of dictionaries
