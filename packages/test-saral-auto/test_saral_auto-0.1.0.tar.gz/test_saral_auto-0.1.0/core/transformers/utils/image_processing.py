from PIL import Image
import cv2
import numpy as np
import os

def preprocess_img_for_ocr(img: Image.Image, **kwargs) -> Image.Image:
    """
    Preprocess an image for better OCR results with pyTesseract.
    
    Parameters:
    - img (PIL.Image.Image): Input image.
    - kwargs: Keyword arguments to control different preprocessing steps.
        - grayscale (bool): Convert to grayscale. Default is True.
        - contrast (bool): Increase contrast. Default is True.
        - threshold (bool): Apply adaptive thresholding. Default is True.
        - denoise (bool): Remove noise. Default is True.
        - deskew (bool): Correct skew. Default is False.
        - rescale (bool): Upscale image if too small. Default is True.
        - morph (bool): Apply morphological transformations. Default is True.
    
    Returns:
    - PIL.Image.Image: Preprocessed image.
    """
    # Default flags
    flags = {
        'grayscale': True,
        'contrast': True,
        'threshold': True,
        'denoise': True,
        'deskew': False,
        'rescale': True,
        'morph': True
    }
    # Override defaults with kwargs
    flags.update(kwargs)

    # Convert PIL image to OpenCV format
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # 1. Grayscale Conversion
    if flags['grayscale']:
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # 2. Increase Contrast
    if flags['contrast']:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img_cv = clahe.apply(img_cv)

    # 3. Thresholding (Binarization)
    if flags['threshold']:
        # Ensure image is in grayscale before thresholding
        if len(img_cv.shape) == 3:  # If image is RGB/BGR
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        # Apply adaptive thresholding to create a binary image
        img_cv = cv2.adaptiveThreshold(img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # 4. Denoising
    if flags['denoise']:
        img_cv = cv2.fastNlMeansDenoising(img_cv, h=30)

    # 5. Deskewing
    if flags['deskew']:
        coords = np.column_stack(np.where(img_cv > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = img_cv.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        img_cv = cv2.warpAffine(img_cv, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # 6. Rescaling
    if flags['rescale']:
        height, width = img_cv.shape[:2]
        if height < 1000 or width < 1000:
            scale_percent = 150  # Increase size by 150%
            new_width = int(width * scale_percent / 100)
            new_height = int(height * scale_percent / 100)
            img_cv = cv2.resize(img_cv, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

    # 7. Morphological Transformations
    if flags['morph']:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        img_cv = cv2.dilate(img_cv, kernel, iterations=1)

    # Convert back to PIL format
    preprocessed_img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB) if len(img_cv.shape) == 3 else img_cv)
    return preprocessed_img
