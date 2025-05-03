from typing import Any, Optional

from pydantic import BaseModel

def assign_config(obj: Any, config: Optional[BaseModel | dict] = None):
    """
    Assigns config values to the object if provided.
    """
    if config is None:
        return
    
    if isinstance(config, dict):
        for key, value in config.items():
            setattr(obj, key, value)
    else:
        # If it's a BaseModel, convert to dict then assign
        config_dict = config.dict() if hasattr(config, "dict") else config.__dict__
        for key, value in config_dict.items():
            setattr(obj, key, value)