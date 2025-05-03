from jinja2 import Environment, FileSystemLoader
import logging

logger = logging.getLogger(__name__)

class PromptLoader:
    """Helper class to load prompts from template files"""
    
    def __init__(self, template_path: str, template_dir: str = ".", ):
        """
        Initialize the prompt loader
        
        Args:
            template_path (str): Path to the template file
            template_dir (str): Directory containing templates
        """
        self.template_dir = template_dir
        self.template_path = template_path
        self.template_cache = {}
        
    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Get a rendered prompt from the template
        
        Args:
            prompt_name (str): Name of the prompt in the template
            **kwargs: Variables to pass to the template
            
        Returns:
            str: The rendered prompt
        """
        # Create a cache key based on template path
        cache_key = self.template_path
        
        # Check if template is already in cache
        if cache_key not in self.template_cache:
            try:
                env = Environment(loader=FileSystemLoader(self.template_dir))
                template = env.get_template(self.template_path)
                self.template_cache[cache_key] = template
            except Exception as e:
                logger.error(f"Error loading template {self.template_path}: {str(e)}")
                raise
        
        template = self.template_cache[cache_key]
        
        try:
            # Get the macro from the template
            macro = getattr(template.module, prompt_name, None)
            if not macro:
                logger.error(f"No macro named '{prompt_name}' found in template {self.template_path}")
                raise ValueError(f"No macro named '{prompt_name}' found in the template.")
            
            # Render the prompt using the macro and provided kwargs
            rendered_prompt = macro(**kwargs)
            return rendered_prompt
            
        except Exception as e:
            logger.error(f"Error rendering prompt '{prompt_name}': {str(e)}")
            raise
