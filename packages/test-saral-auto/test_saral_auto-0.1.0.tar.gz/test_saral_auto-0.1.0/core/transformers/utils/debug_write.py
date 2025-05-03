import json
import os
import base64
from pathlib import Path
from uuid import uuid4
from typing import Any, Union

import cv2
import numpy as np
from core.schemas.document.document import BaseModel


def dump_document_with_images(
    model: BaseModel,
    file_path: Union[str, Path] = "output/debug.json",
    *,
    indent: int = 2,
    image_folder_name: str = "images",
    image_key_names: tuple[str, ...] = ("highres_image", "lowres_image"),
    debug: bool = False,
    write: bool = True
) -> None:
    """
    Dumps a Pydantic model to JSON and saves base64-encoded images to disk using OpenCV.

    Args:
        model:              Any Pydantic BaseModel.
        file_path:          Output JSON path.
        indent:             JSON indentation.
        image_folder_name:  Folder to store extracted images.
        image_key_names:    Keys expected to contain base64-encoded image strings.
        debug:              Enable detailed debug logging.
        write:              Whether to write files to disk.

    Returns:
        dict: The cleaned JSON data structure.

    Raises:
        ValueError: If the model is not a Pydantic BaseModel.
        OSError: If there are file system related errors.
        Exception: For other unexpected errors.
    """
    try:
        if not isinstance(model, BaseModel):
            raise ValueError("Input model must be a Pydantic BaseModel")

        file_path = Path(file_path)
        img_dir = file_path.parent / image_folder_name
        
        try:
            img_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create image directory {img_dir}: {str(e)}")

        try:
            data = model.dict()
        except Exception as e:
            raise ValueError(f"Failed to convert model to dictionary: {str(e)}")

        img_count = 0

        def _walk(o: Any) -> Any:
            nonlocal img_count
            if isinstance(o, dict):
                new_dict: dict[str, Any] = {}
                for k, v in o.items():
                    if k in image_key_names and v and write:
                        try:
                            if isinstance(v, str):
                                try:
                                    # Handle "data:image" format (data URL)
                                    if v.startswith("data:image"):
                                        b64_data = v.split(",", 1)[1]
                                    # Handle raw base64 format - check for common image signatures
                                    elif v.startswith("/9j/"):  # JPEG base64 signature
                                        b64_data = v
                                    elif v.startswith("iVBOR"):  # PNG base64 signature
                                        b64_data = v
                                    else:
                                        # Try to decode it anyway - might be base64 without recognized prefix
                                        b64_data = v
                                    
                                    try:
                                        img_bytes = base64.b64decode(b64_data)
                                        np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
                                        img = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)
                                    except Exception as e:
                                        if debug:
                                            print(f"⚠️ Error decoding image data: {e}")
                                        new_dict[k] = f"[image decode error: {e}]"
                                        continue
                                    
                                    if img is None:
                                        if debug:
                                            print(f"⚠️ Warning: Invalid image data for {k}")
                                        new_dict[k] = "[invalid image data]"
                                        continue

                                    # construct filename
                                    page_id = o.get("page_id", "unknownpage")
                                    block_id = o.get("block_id", uuid4().hex[:6])
                                    img_filename = f"page_{page_id}_{block_id}_{k}.jpg"
                                    img_path = img_dir / img_filename

                                    # save using OpenCV
                                    try:
                                        success = cv2.imwrite(str(img_path), img)
                                        if not success:
                                            if debug:
                                                print(f"⚠️ Warning: Failed to save image to {img_path}")
                                            new_dict[k] = "[image save failed]"
                                            continue
                                        
                                        img_count += 1
                                        new_dict["image_path"] = str(img_path)
                                    except Exception as e:
                                        if debug:
                                            print(f"⚠️ Error saving image to {img_path}: {e}")
                                        new_dict[k] = f"[image save error: {e}]"
                                except Exception as e:
                                    if debug:
                                        print(f"⚠️ Error processing image data: {e}")
                                    new_dict[k] = f"[image processing error: {e}]"
                            else:
                                new_dict[k] = v
                        except Exception as e:
                            if debug:
                                print(f"⚠️ Error handling image key '{k}': {e}")
                            new_dict[k] = f"[image handling error: {e}]"
                    else:
                        new_dict[k] = _walk(v)
                return new_dict

            elif isinstance(o, list):
                return [_walk(item) for item in o]

            else:
                return o

        cleaned = _walk(data)

        if write:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(cleaned, f, ensure_ascii=False, indent=indent)
            except Exception as e:
                raise OSError(f"Failed to write JSON file {file_path}: {str(e)}")

        print(f"✅ JSON written to: {file_path.resolve()}")
        print(f"✅ Images saved: {img_count} in: {img_dir.resolve()}")
        return cleaned

    except Exception as e:
        if debug:
            print(f"❌ Critical error in dump_document_with_images: {str(e)}")
        raise
