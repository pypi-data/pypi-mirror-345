import inspect
import os
from typing import Optional, List, Type, Dict, Any

import cv2
import numpy as np
from pydantic import BaseModel

from core.transformers.processors import BaseProcessor
from core.pipelines.utils.assign_config import assign_config
from core.schemas.document.document import Document
from core.schemas.document.groups.page import PageGroup
from core.schemas.document.polygon import PolygonBox
import logging

# Configure logger
logger = logging.getLogger(__name__)

class BasePipeline:
    def __init__(self, config: Optional[BaseModel | dict] = None, image_path: str = None):
        assign_config(self, config)
        self.config = config
        self.artifact_dict: Dict[str, Any] = {}  # Initialize empty artifact dictionary
        
        # Store image path
        self.image_path = image_path
        
        # Create output directory for debug output
        self.output_dir = self.config.get("output_dir", "output/pipeline") if self.config else "output/pipeline"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize image storage
        self._images = {}

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def resolve_dependencies(self, cls):
        init_signature = inspect.signature(cls.__init__)
        parameters = init_signature.parameters

        resolved_kwargs = {}
        for param_name, param in parameters.items():
            if param_name == 'self':
                continue
            elif param_name == 'config':
                resolved_kwargs[param_name] = self.config
            elif param.name in self.artifact_dict:
                resolved_kwargs[param_name] = self.artifact_dict[param.name]
            elif param.default != inspect.Parameter.empty:
                resolved_kwargs[param_name] = param.default
            else:
                raise ValueError(f"Cannot resolve dependency for parameter: {param_name}")

        return cls(**resolved_kwargs)

    def initialize_processors(self, processor_cls_lst: List[Type[BaseProcessor]]) -> List[BaseProcessor]:
        processors = []
        for processor_cls in processor_cls_lst:
            processors.append(self.resolve_dependencies(processor_cls))
        
        return processors
        
    def _initialize_document(self) -> Document:
        """
        Initialize a document from the image path.
        
        Returns:
            Document: The initialized document
        """
        logger.info(f"Initializing document from image: {self.image_path}")
        
        if not self.image_path or not os.path.exists(self.image_path):
            raise ValueError(f"Invalid image path: {self.image_path}")
        
        # Read the input image
        img = cv2.imread(self.image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {self.image_path}")
        
        # Create page polygon for the image dimensions
        height, width = img.shape[:2]
        page_polygon = PolygonBox.from_bbox([0, 0, width, height])
        
        # Create a page with initial metadata
        page = PageGroup(
            polygon=page_polygon,
            page_id=0,
            block_id=0,
            children=[],
            structure=[],
            block_description="Page 0"
        )
        
        # Create a new document with the page
        document = Document(
            filepath=self.image_path,
            pages=[page],
            debug_data_path=self.output_dir
        )
        
        # Initialize page metadata using __dict__ to bypass BlockMetadata's restrictions
        page.__dict__['metadata'] = {
            "original_image": img,
            "processed_image": img.copy(),
            "image_size": (width, height)
        }
        
        # Store the image for later use
        self._set_page_image(img, page_id=0, processed=False)
        self._set_page_image(img.copy(), page_id=0, processed=True)
        
        logger.info(f"Document initialized with image size: {width}x{height}")
        
        return document
    
    def _get_page_image(self, page_id: int = 0, processed: bool = True) -> Optional[np.ndarray]:
        """
        Get the image for a specific page.
        
        Args:
            page_id: The page ID
            processed: Whether to get the processed or original image
            
        Returns:
            np.ndarray: The image
        """
        key = f"page_{page_id}_{'processed' if processed else 'original'}"
        return self._images.get(key)
    
    def _set_page_image(self, image: np.ndarray, page_id: int = 0, processed: bool = True) -> None:
        """
        Set the image for a specific page.
        
        Args:
            image: The image to set
            page_id: The page ID
            processed: Whether to set the processed or original image
        """
        key = f"page_{page_id}_{'processed' if processed else 'original'}"
        self._images[key] = image