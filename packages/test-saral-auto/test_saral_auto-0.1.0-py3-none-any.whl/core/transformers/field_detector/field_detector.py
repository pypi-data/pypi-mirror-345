"""
Field detector module for detecting and extracting fields from documents.
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Tuple, Optional, Any, Union

from core.transformers.document_processor.document_processor import FieldType


class FieldDetector:
    """
    Class for detecting and extracting fields from documents.
    """
    
    @staticmethod
    def detect_field_type(roi: Dict[str, Any], image: np.ndarray = None) -> FieldType:
        """
        Detect the type of field based on the ROI and image content.
        
        Args:
            roi: ROI dictionary
            image: Image containing the ROI (optional)
            
        Returns:
            FieldType enum value
        """
        text = roi.get("text", "").lower()
        
        # Check for specific field types based on text content
        if any(keyword in text for keyword in ["date", "dob", "birth", "day", "month", "year"]):
            return FieldType.DATE
        elif any(keyword in text for keyword in ["number", "phone", "mobile", "contact", "amount", "fee", "cost", "price"]):
            return FieldType.NUMBER
        elif any(keyword in text for keyword in ["sign", "signature"]):
            return FieldType.SIGNATURE
        elif any(keyword in text for keyword in ["check", "tick", "select"]):
            return FieldType.CHECKBOX
        elif any(keyword in text for keyword in ["radio", "choose one", "select one"]):
            return FieldType.RADIO_BUTTON
        elif any(keyword in text for keyword in ["image", "photo", "picture", "upload"]):
            return FieldType.IMAGE
        
        # If image is provided, try to detect boxed text
        if image is not None:
            if FieldDetector._is_boxed_text(roi, image):
                return FieldType.BOXED_TEXT
        
        # Default to text
        return FieldType.TEXT
    
    @staticmethod
    def _is_boxed_text(roi: Dict[str, Any], image: np.ndarray) -> bool:
        """
        Check if the ROI contains boxed text.
        
        Args:
            roi: ROI dictionary
            image: Image containing the ROI
            
        Returns:
            True if the ROI contains boxed text, False otherwise
        """
        # Extract the ROI from the image
        roi_image = image[roi["top"]:roi["bottom"], roi["left"]:roi["right"]]
        
        # Convert to grayscale
        gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count the number of small, square-like contours
        box_count = 0
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            
            # Check if the contour is square-like
            if 0.8 <= aspect_ratio <= 1.2 and 10 <= w <= 50 and 10 <= h <= 50:
                box_count += 1
        
        # If there are multiple boxes, it's likely boxed text
        return box_count >= 3
    
    @staticmethod
    def extract_field_value(roi: Dict[str, Any], image: np.ndarray, field_type: FieldType) -> str:
        """
        Extract the value of a field from the image.
        
        Args:
            roi: ROI dictionary
            image: Image containing the ROI
            field_type: Type of the field
            
        Returns:
            Extracted field value as a string
        """
        # Extract the ROI from the image
        roi_image = image[roi["top"]:roi["bottom"], roi["left"]:roi["right"]]
        
        if field_type == FieldType.TEXT or field_type == FieldType.NUMBER or field_type == FieldType.DATE:
            # Use OCR to extract text
            text = pytesseract.image_to_string(roi_image)
            return text.strip()
            
        elif field_type == FieldType.BOXED_TEXT:
            # Extract boxed text
            return FieldDetector._extract_boxed_text(roi_image)
            
        elif field_type == FieldType.CHECKBOX:
            # Check if the checkbox is checked
            is_checked = FieldDetector._is_checkbox_checked(roi_image)
            return "checked" if is_checked else "unchecked"
            
        elif field_type == FieldType.RADIO_BUTTON:
            # Check if the radio button is selected
            is_selected = FieldDetector._is_radio_button_selected(roi_image)
            return "selected" if is_selected else "unselected"
            
        elif field_type == FieldType.SIGNATURE:
            # Check if there's a signature
            has_signature = FieldDetector._has_signature(roi_image)
            return "signed" if has_signature else "unsigned"
            
        else:
            # Default to OCR
            text = pytesseract.image_to_string(roi_image)
            return text.strip()
    
    @staticmethod
    def _extract_boxed_text(image: np.ndarray) -> str:
        """
        Extract text from boxed text fields.
        
        Args:
            image: Image containing the boxed text
            
        Returns:
            Extracted text
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours from left to right
        contours = sorted(contours, key=lambda cnt: cv2.boundingRect(cnt)[0])
        
        # Extract text from each box
        text = ""
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Check if the contour is square-like
            aspect_ratio = float(w) / h
            if 0.8 <= aspect_ratio <= 1.2 and 10 <= w <= 50 and 10 <= h <= 50:
                # Extract the box
                box_image = gray[y:y+h, x:x+w]
                
                # Use OCR to extract the character
                char = pytesseract.image_to_string(box_image, config='--psm 10')
                
                # Add the character to the text
                text += char.strip()
        
        return text
    
    @staticmethod
    def _is_checkbox_checked(image: np.ndarray) -> bool:
        """
        Check if a checkbox is checked.
        
        Args:
            image: Image containing the checkbox
            
        Returns:
            True if the checkbox is checked, False otherwise
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Calculate the percentage of black pixels
        black_pixel_percentage = np.sum(thresh == 255) / (thresh.shape[0] * thresh.shape[1])
        
        # If the percentage is above a threshold, the checkbox is checked
        return black_pixel_percentage > 0.1
    
    @staticmethod
    def _is_radio_button_selected(image: np.ndarray) -> bool:
        """
        Check if a radio button is selected.
        
        Args:
            image: Image containing the radio button
            
        Returns:
            True if the radio button is selected, False otherwise
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if there's a filled circle
        for cnt in contours:
            # Calculate circularity
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # If the contour is circular and filled, the radio button is selected
                if circularity > 0.7 and area > 100:
                    return True
        
        return False
    
    @staticmethod
    def _has_signature(image: np.ndarray) -> bool:
        """
        Check if there's a signature in the image.
        
        Args:
            image: Image containing the signature field
            
        Returns:
            True if there's a signature, False otherwise
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Calculate the percentage of black pixels
        black_pixel_percentage = np.sum(thresh == 255) / (thresh.shape[0] * thresh.shape[1])
        
        # If the percentage is above a threshold, there's a signature
        return black_pixel_percentage > 0.05 