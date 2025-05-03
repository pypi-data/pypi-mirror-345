# Test to validate the ROI schema of a JSON file

import json
import os
import tempfile
import unittest
from pathlib import Path
import copy

from pydantic import ValidationError

from core.schemas.roi.roi import ROI, ROIList
from core.schemas.roi.cell import Cell, CellList, NormalizedCell, CellMetadata
from core.schemas.roi.utils import (
    load_roi_json, 
    save_roi_json, 
    validate_roi_json,
    load_cell_json,
    save_cell_json,
    convert_cells_to_rois
)

# Sample ROI data for testing
SAMPLE_ROI_DATA = [
    {
        "left": 300,
        "top": 586,
        "right": 1143,
        "bottom": 692,
        "text": "Praveshaank",
        "textSize": 46,
        "isBold": False,
        "boldRatio": 0.316622691292876
    },
    {
        "left": 300,
        "top": 718,
        "right": 1143,
        "bottom": 955,
        "text": "Student Aadhar No.",
        "textSize": 45,
        "isBold": False,
        "boldRatio": 0.3148222133439872
    }
]

# Sample Cell data for testing
SAMPLE_CELL_DATA = [
    {
        "id": 1,
        "x": 300,
        "y": 586,
        "width": 843,
        "height": 106,
        "text": "Praveshaank",
        "orientation": "horizontal",
        "is_printed": True,
        "confidence": {"text": 0.98},
        "normalized": {
            "x": 300,
            "y": 586,
            "width": 843,
            "height": 106
        },
        "metadata": {
            "is_header": False,
            "row_id": 1,
            "group_id": 0
        }
    },
    {
        "id": 2,
        "x": 300,
        "y": 718,
        "width": 843,
        "height": 237,
        "text": "Student Aadhar No.",
        "orientation": "horizontal",
        "is_printed": True,
        "confidence": {"text": 0.96},
        "normalized": {
            "x": 300,
            "y": 718,
            "width": 843,
            "height": 237
        },
        "metadata": {
            "is_header": True,
            "row_id": 2,
            "group_id": 1
        }
    }
]

class TestROISchema(unittest.TestCase):
    """Test cases for the ROI schema."""
    
    def setUp(self):
        """Set up for tests - create temp files with sample data."""
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create ROI test file - use a deep copy to avoid issues with modified data
        self.temp_roi_path = Path(self.temp_dir.name) / "test_rois.json"
        with open(self.temp_roi_path, 'w') as f:
            json.dump(copy.deepcopy(SAMPLE_ROI_DATA), f, indent=4)
            
        # Create Cell test file - use a deep copy to avoid issues with modified data
        self.temp_cell_path = Path(self.temp_dir.name) / "test_cells.json"
        with open(self.temp_cell_path, 'w') as f:
            json.dump(copy.deepcopy(SAMPLE_CELL_DATA), f, indent=4)
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_roi_model_valid(self):
        """Test that a valid ROI model can be created."""
        roi = ROI(**SAMPLE_ROI_DATA[0])
        self.assertEqual(roi.left, 300)
        self.assertEqual(roi.text, "Praveshaank")
        self.assertEqual(roi.textSize, 46)
        self.assertFalse(roi.isBold)
        
        # Test the new properties
        self.assertEqual(roi.width, 843)
        self.assertEqual(roi.height, 106)
        self.assertEqual(roi.area, 89358)
        self.assertEqual(roi.center, (721, 639))
    
    def test_roi_model_invalid(self):
        """Test that invalid ROI data raises validation error."""
        # Create invalid data with a missing required field
        invalid_data = {
            "left": 300,
            "top": 586,
            "right": 1143,
            # "bottom" is missing
            "text": "Praveshaank",
            "textSize": 46,
            "isBold": False,
            "boldRatio": 0.316622691292876
        }
        
        with self.assertRaises(ValidationError):
            ROI(**invalid_data)
    
    def test_roi_list_from_list(self):
        """Test creating ROIList from a list of dictionaries."""
        roi_list = ROIList.from_list(SAMPLE_ROI_DATA)
        self.assertEqual(len(roi_list.rois), 2)
        self.assertEqual(roi_list.rois[0].text, "Praveshaank")
        self.assertEqual(roi_list.rois[1].text, "Student Aadhar No.")
    
    def test_load_roi_json_list(self):
        """Test loading ROIs from a JSON file with a list."""
        roi_list = load_roi_json(self.temp_roi_path)
        self.assertEqual(len(roi_list.rois), 2)
        self.assertEqual(roi_list.rois[0].text, "Praveshaank")
    
    def test_load_roi_json_dict(self):
        """Test loading ROIs from a JSON file with a dict containing 'rois' key."""
        dict_data = {"rois": copy.deepcopy(SAMPLE_ROI_DATA)}
        dict_file_path = Path(self.temp_dir.name) / "test_dict_rois.json"
        
        with open(dict_file_path, 'w') as f:
            json.dump(dict_data, f, indent=4)
        
        roi_list = load_roi_json(dict_file_path)
        self.assertEqual(len(roi_list.rois), 2)
    
    def test_save_roi_json(self):
        """Test saving ROIs to a JSON file."""
        roi_list = ROIList.from_list(SAMPLE_ROI_DATA)
        save_path = Path(self.temp_dir.name) / "saved_rois.json"
        
        save_roi_json(roi_list, save_path)
        
        # Check that the file exists
        self.assertTrue(save_path.exists())
        
        # Load the file and check content
        with open(save_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["text"], "Praveshaank")
    
    def test_validate_roi_json_valid(self):
        """Test validating a valid ROI JSON file."""
        self.assertTrue(validate_roi_json(self.temp_roi_path))
    
    def test_validate_roi_json_invalid(self):
        """Test validating an invalid ROI JSON file."""
        invalid_file_path = Path(self.temp_dir.name) / "invalid_rois.json"
        
        # Create invalid JSON - missing required fields
        invalid_data = [{"left": 300, "top": 586}]  # Missing required fields
        
        with open(invalid_file_path, 'w') as f:
            json.dump(invalid_data, f, indent=4)
        
        with self.assertRaises(ValueError):
            validate_roi_json(invalid_file_path)
    
    def test_roi_to_dict(self):
        """Test the to_dict method for ROI model."""
        roi = ROI(**SAMPLE_ROI_DATA[0])
        roi_dict = roi.to_dict()
        
        self.assertEqual(roi_dict["left"], 300)
        self.assertEqual(roi_dict["text"], "Praveshaank")
        self.assertEqual(roi_dict["textSize"], 46)
        self.assertFalse(roi_dict["isBold"])
        self.assertIsNone(roi_dict["confidence"])
        self.assertIsNone(roi_dict["type"])
        self.assertIsNone(roi_dict["group_id"])
    
    def test_cell_model_valid(self):
        """Test that a valid Cell model can be created."""
        # Use a fresh copy of the data to avoid issues with modified global
        cell_data = copy.deepcopy(SAMPLE_CELL_DATA[0])
        cell = Cell(**cell_data)
        self.assertEqual(cell.id, 1)
        self.assertEqual(cell.x, 300)
        self.assertEqual(cell.y, 586)
        self.assertEqual(cell.text, "Praveshaank")
        self.assertEqual(cell.normalized.width, 843)
        self.assertEqual(cell.metadata.is_header, False)
    
    def test_cell_list_from_list(self):
        """Test creating CellList from a list of dictionaries."""
        # Use a fresh copy of the data to avoid issues with modified global
        cell_data = copy.deepcopy(SAMPLE_CELL_DATA)
        cell_list = CellList.from_list(cell_data)
        self.assertEqual(len(cell_list.cells), 2)
        self.assertEqual(cell_list.cells[0].text, "Praveshaank")
        self.assertEqual(cell_list.cells[1].text, "Student Aadhar No.")
    
    def test_load_cell_json(self):
        """Test loading cells from a JSON file."""
        cell_list = load_cell_json(self.temp_cell_path)
        self.assertEqual(len(cell_list.cells), 2)
        self.assertEqual(cell_list.cells[0].text, "Praveshaank")
        self.assertEqual(cell_list.cells[1].metadata.is_header, True)
    
    def test_save_cell_json(self):
        """Test saving cells to a JSON file."""
        # Use a fresh copy of the data to avoid issues with modified global
        cell_data = copy.deepcopy(SAMPLE_CELL_DATA)
        cell_list = CellList.from_list(cell_data)
        save_path = Path(self.temp_dir.name) / "saved_cells.json"
        
        save_cell_json(cell_list, save_path)
        
        # Check that the file exists
        self.assertTrue(save_path.exists())
        
        # Load the file and check content
        with open(save_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["Cell"], 1)  # Special field from to_dict conversion
        self.assertEqual(loaded_data[0]["Text"], "Praveshaank")
    
    def test_convert_cells_to_rois(self):
        """Test converting Cell models to ROI models."""
        # Use a fresh copy of the data to avoid issues with modified global
        cell_data = copy.deepcopy(SAMPLE_CELL_DATA)
        cell_list = CellList.from_list(cell_data)
        roi_list = convert_cells_to_rois(cell_list)
        
        self.assertEqual(len(roi_list.rois), 2)
        self.assertEqual(roi_list.rois[0].left, 300)
        self.assertEqual(roi_list.rois[0].right, 300 + 843)
        self.assertEqual(roi_list.rois[0].text, "Praveshaank")
        self.assertEqual(roi_list.rois[1].type, "header")
        self.assertEqual(roi_list.rois[1].group_id, 1)


if __name__ == "__main__":
    unittest.main()
    # python -m core.schemas.roi.test.test_roi_schema


