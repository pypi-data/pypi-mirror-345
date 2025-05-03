"""
Base processor class for document processing pipeline with enhanced checkpointing.

This module provides a BaseProcessor abstract class that serves as the foundation
for all processor classes in the document processing pipeline, with support for
checkpointing, caching, and resuming execution.
"""

import os
import json
import hashlib
import pickle
from typing import Dict, Any, Optional, Tuple, Union
from pydantic import BaseModel
from core.schemas.document.document import Document
from core.schemas.document import BlockTypes
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def assign_config(obj, config):
    """Assign configuration values to object attributes."""
    if config is None:
        return
    
    if isinstance(config, dict):
        for key, value in config.items():
            setattr(obj, key, value)
    else:
        # For BaseModel or other config objects
        for key, value in config.dict().items():
            setattr(obj, key, value)

class BaseProcessor:
    """
    Abstract base class for document processors with checkpointing support.
    
    This class defines the interface that all processor classes should implement,
    including methods for checkpointing, caching, and resuming execution.
    """
    
    # Default block types this processor can handle (should be overridden by subclasses)
    block_types: Tuple[BlockTypes, ...] | None = None
    
    def __init__(self, config: Optional[Union[BaseModel, dict]] = None, 
                 checkpoint_dir: Optional[str] = None):
        """
        Initialize the base processor.
        
        Args:
            config: Configuration dictionary or BaseModel with processing parameters
            checkpoint_dir: Directory to store checkpoint data
        """
        # Assign configuration
        self.config = config or {}
        assign_config(self, config)
        
        # Set up checkpointing
        self._checkpoint_data = {}
        self._checkpoint_dir = checkpoint_dir or os.environ.get('CHECKPOINT_DIR', '.checkpoints')
        self._processor_name = self.__class__.__name__
        
        # Create checkpoint directory if it doesn't exist
        if self._checkpoint_dir:
            os.makedirs(self._checkpoint_dir, exist_ok=True)
        
        # Caching settings
        self._enable_caching = self.config.get('enable_caching', True) if isinstance(self.config, dict) else getattr(self, 'enable_caching', True)
        self._cache = {}
        
        # Generate a unique processor ID based on class name and config
        self._processor_id = self._generate_processor_id()
        
        # Load checkpoint if exists
        self._load_checkpoint()
    
    def _generate_processor_id(self) -> str:
        """
        Generate a unique ID for this processor instance based on class name and config.
        
        Returns:
            str: A unique identifier for this processor instance
        """
        try:
            config_str = str(self.config) if hasattr(self, 'config') else ""
            processor_info = f"{self.__class__.__name__}:{config_str}"
            return hashlib.md5(processor_info.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating processor ID: {str(e)}")
            return hashlib.md5(self.__class__.__name__.encode()).hexdigest()
    
    def __call__(self, document: Document, *args, **kwargs) -> Document:
        """
        Process the document, with optional resumption from checkpoint.
        
        Args:
            document: The document to process
            
        Returns:
            Document: The processed document
        """
        try:
            # Try to get cached result first
            if self._enable_caching:
                cached_doc = self._get_cache(document)
                if cached_doc is not None:
                    logger.info(f"{self.__class__.__name__}: Using cached result")
                    return cached_doc
        except Exception as e:
            logger.warning(f"Error accessing cache: {str(e)}. Continuing with processing.")
        
        # Check if there's a complete checkpoint to resume from
        if 'completed' in self._checkpoint_data and self._checkpoint_data['completed']:
            logger.info(f"{self.__class__.__name__}: Resuming from completed checkpoint")
            try:
                # Apply the checkpoint data to the document if we have a way to do so
                document = self._apply_checkpoint_to_document(document)
                return document
            except Exception as e:
                logger.warning(f"Error applying checkpoint: {str(e)}. Continuing with fresh processing.")
        
        # Otherwise, process should be implemented by subclass
        raise NotImplementedError
    
    def _checkpoint(self, stage_name: str, data: Dict[str, Any] = None) -> None:
        """
        Store checkpoint data for a processing stage.
        
        Args:
            stage_name: Name of the processing stage
            data: Data to store in the checkpoint
        """
        try:
            if data is None:
                data = {}
                
            self._checkpoint_data[stage_name] = data
            logger.debug(f"Checkpoint: {stage_name} completed")
            
            # Save checkpoint to file
            self._save_checkpoint()
        except Exception as e:
            logger.error(f"Error creating checkpoint for {stage_name}: {str(e)}")
    
    def _mark_completed(self, result_data: Dict[str, Any] = None) -> None:
        """
        Mark the processing as completed and store the result data.
        
        Args:
            result_data: Final result data to store
        """
        try:
            self._checkpoint_data['completed'] = True
            if result_data:
                self._checkpoint_data['result'] = result_data
            
            # Save checkpoint to file
            self._save_checkpoint()
            logger.info(f"{self.__class__.__name__}: Processing completed and checkpointed")
        except Exception as e:
            logger.error(f"Error marking completion: {str(e)}")
    
    def get_checkpoint(self, stage_name: str) -> Dict[str, Any]:
        """
        Get checkpoint data for a processing stage.
        
        Args:
            stage_name: Name of the processing stage
            
        Returns:
            Dict[str, Any]: The checkpoint data
        """
        return self._checkpoint_data.get(stage_name, {})
    
    def _checkpoint_filename(self) -> str:
        """
        Get the filename for saving checkpoint data.
        
        Returns:
            str: The checkpoint filename
        """
        return os.path.join(self._checkpoint_dir, f"{self._processor_name}_{self._processor_id}.pickle")
    
    def _save_checkpoint(self) -> None:
        """Save checkpoint data to file."""
        if not self._checkpoint_dir:
            return
        
        try:
            filename = self._checkpoint_filename()
            with open(filename, 'wb') as f:
                pickle.dump(self._checkpoint_data, f)
            logger.debug(f"Checkpoint saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {str(e)}")
    
    def _load_checkpoint(self) -> None:
        """Load checkpoint data from file if it exists."""
        if not self._checkpoint_dir:
            return
        
        filename = self._checkpoint_filename()
        if os.path.exists(filename):
            try:
                with open(filename, 'rb') as f:
                    self._checkpoint_data = pickle.load(f)
                logger.info(f"Loaded checkpoint from {filename}")
            except Exception as e:
                logger.error(f"Failed to load checkpoint: {str(e)}")
                self._checkpoint_data = {}
    
    def _apply_checkpoint_to_document(self, document: Document) -> Document:
        """
        Apply checkpoint data to document if resuming from a checkpoint.
        This should be implemented by subclasses that need custom checkpoint application.
        
        Args:
            document: The document to apply checkpoint data to
            
        Returns:
            Document: The document with checkpoint data applied
        """
        # Default implementation just returns the document unchanged
        return document
    
    def _cache_key(self, document: Document) -> str:
        """
        Generate a cache key for the document.
        
        Args:
            document: The document to generate a cache key for
            
        Returns:
            str: A cache key for the document
        """
        try:
            # Generate a hash of the document ID and page IDs to use as cache key
            doc_id = str(getattr(document, 'id', id(document)))
            
            # Safely convert page IDs to strings
            page_ids = []
            for page in document.pages:
                try:
                    page_id = getattr(page, 'id', id(page))
                    page_ids.append(str(page_id))
                except Exception:
                    # If we can't get the page ID, use the object ID
                    page_ids.append(str(id(page)))
            
            key_data = f"{doc_id}:{','.join(page_ids)}:{self._processor_id}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception as e:
            # Fall back to using a simple hash of the document object ID
            logger.warning(f"Error generating cache key: {str(e)}. Using fallback.")
            return hashlib.md5(str(id(document)).encode()).hexdigest()
    
    def _set_cache(self, document: Document, result: Document) -> None:
        """
        Cache the result of processing a document.
        
        Args:
            document: The input document
            result: The processed document
        """
        if not self._enable_caching:
            return
        
        try:
            key = self._cache_key(document)
            self._cache[key] = result
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
    
    def _get_cache(self, document: Document) -> Optional[Document]:
        """
        Get the cached result for a document if available.
        
        Args:
            document: The document to get cached result for
            
        Returns:
            Optional[Document]: The cached result document or None
        """
        if not self._enable_caching:
            return None
        
        try:
            key = self._cache_key(document)
            return self._cache.get(key)
        except Exception as e:
            logger.error(f"Error getting cache: {str(e)}")
            return None
    
    def clear_checkpoint(self) -> None:
        """Clear checkpoint data."""
        try:
            self._checkpoint_data = {}
            
            # Remove checkpoint file if it exists
            if self._checkpoint_dir:
                filename = self._checkpoint_filename()
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                        logger.info(f"Removed checkpoint file {filename}")
                    except Exception as e:
                        logger.error(f"Failed to remove checkpoint file: {str(e)}")
        except Exception as e:
            logger.error(f"Error clearing checkpoint: {str(e)}")
    
    def clear_cache(self) -> None:
        """Clear cached results."""
        try:
            self._cache = {}
            logger.debug("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")