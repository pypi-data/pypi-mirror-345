from core.schemas.document import BlockTypes
from core.schemas.document.blocks import Block
from PIL import Image
import base64
from io import BytesIO
from typing import Optional, Tuple, Sequence


class Picture(Block):
    block_type: BlockTypes = BlockTypes.Picture
    description: str | None = None
    block_description: str = "An image block that represents a picture."
    highres_image: Image.Image | str | None = None
    image_path: str | None = None

    def assemble_html(self, document, child_blocks, parent_structure):
        child_ref_blocks = [block for block in child_blocks if block.id.block_type == BlockTypes.Reference]
        html = super().assemble_html(document, child_ref_blocks, parent_structure)
        if self.description:
            return html + f"<p role='img' data-original-image-id='{self.id}'>Image {self.id} description: {self.description}</p>"
        return html

    def get_image(self, document=None, highres: bool = False, expansion: Optional[Tuple[float, float]] = None, remove_blocks: Optional[Sequence[BlockTypes]] = None) -> Optional[Image.Image]:
        """Get the image for this Picture block."""
        if self.highres_image is not None:
            if isinstance(self.highres_image, str):
                try:
                    # If it's a base64 string, convert to PIL Image
                    if "base64," in self.highres_image:
                        self.highres_image = self.highres_image.split("base64,")[1]
                    image_bytes = base64.b64decode(self.highres_image)
                    return Image.open(BytesIO(image_bytes))
                except Exception:
                    pass
            elif isinstance(self.highres_image, Image.Image):
                return self.highres_image

        if self.image_path and document:
            try:
                return Image.open(self.image_path)
            except Exception:
                pass

        return super().get_image(document, highres, expansion, remove_blocks)

    def model_dump(self, **kwargs):
        """Override model_dump to make highres_image serializable"""
        data = super().model_dump(**kwargs)
        
        if 'highres_image' in data and data['highres_image'] is not None:
            if isinstance(data['highres_image'], Image.Image):
                buffer = BytesIO()
                data['highres_image'].save(buffer, format="JPEG") 
                img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
                data['highres_image'] = img_str
            elif isinstance(data['highres_image'], str):
                # Ensure base64 string is properly formatted
                if "base64," not in data['highres_image']:
                    data['highres_image'] = f"data:image/jpeg;base64,{data['highres_image']}"
        
        return data