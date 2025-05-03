from core.transformers.processors import BaseProcessor
import google.generativeai as genai
import json
import logging
import os
import random
import time
import traceback
import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

# This folder contains the code for the LLM processors. BaseLLMProcessor class
class BaseLLMProcessor(BaseProcessor):
    def __init__(self, model="gemini-2.0-flash-thinking-exp-01-21", log_level=logging.INFO):
        """
        Initialize the LLM processor
        
        Args:
            model (str): The Gemini model to use (default: gemini-2.0-flash-thinking-exp-01-21)
            log_level (int, optional): Logging level (e.g., logging.INFO)
        """
        super().__init__()
        self.model = model
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum time between requests in seconds
        self.template_cache = {}  # Cache for loaded templates
        self.api_keys = []  # Store loaded API keys
        self.exhausted_keys = set()  # Track keys that hit rate limits
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
        # Setup API key tracking file
        self.api_key_stats_file = os.path.join("output", "api_observability/api_key_stats.json")
        os.makedirs(os.path.dirname(self.api_key_stats_file), exist_ok=True)
        self._initialize_api_key_stats()
        
        # Load API keys
        self._load_api_keys()

    def _initialize_api_key_stats(self):
        """Initialize the API key stats tracking file if it doesn't exist."""
        if not os.path.exists(self.api_key_stats_file):
            try:
                with open(self.api_key_stats_file, 'w') as f:
                    json.dump({}, f)
                self.logger.debug(f"Created API key stats file at {self.api_key_stats_file}")
            except Exception as e:
                self.logger.error(f"Error creating API key stats file: {str(e)}")

    def _update_api_key_stats(self, api_key, model, success=True, error=None):
        """Update the API key usage statistics."""
        try:
            # Load existing stats
            stats = {}
            if os.path.exists(self.api_key_stats_file):
                with open(self.api_key_stats_file, 'r') as f:
                    stats = json.load(f)
            
            # Mask the API key for privacy/security (only store first 8 chars)
            masked_key = api_key[:8] + "..." if len(api_key) > 8 else api_key
            
            # Initialize entry for this key if it doesn't exist
            if masked_key not in stats:
                stats[masked_key] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "models_used": {},
                    "last_used": None,
                    "errors": []
                }
            
            # Update stats
            timestamp = datetime.datetime.now().isoformat()
            stats[masked_key]["total_calls"] += 1
            stats[masked_key]["last_used"] = timestamp
            
            if success:
                stats[masked_key]["successful_calls"] += 1
            else:
                stats[masked_key]["failed_calls"] += 1
                if error:
                    # Keep only the last 10 errors
                    stats[masked_key]["errors"] = stats[masked_key]["errors"][-9:] + [{
                        "timestamp": timestamp,
                        "error": str(error)
                    }]
            
            # Update model usage
            if model not in stats[masked_key]["models_used"]:
                stats[masked_key]["models_used"][model] = 0
            stats[masked_key]["models_used"][model] += 1
            
            # Save updated stats
            with open(self.api_key_stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
            self.logger.debug(f"Updated API key stats for key {masked_key}")
            
        except Exception as e:
            self.logger.error(f"Error updating API key stats: {str(e)}")

    def _load_api_keys(self):
        """Load API keys from gemini.keys file but don't set one yet."""
        self.api_keys = []
        
        # Try multiple possible locations for the gemini.keys file
        keys_file_paths = [
            "gemini.keys",  # Current directory
            os.path.join(os.getcwd(), "gemini.keys"),  # Absolute path from current directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "gemini.keys")  # Up from core/transformers/processors/LLM_processors
        ]
        
        # Try each path until we find the file
        keys_file_path = None
        for path in keys_file_paths:
            if os.path.exists(path):
                keys_file_path = path
                break
        
        # Load keys from file if found
        if keys_file_path:
            self.logger.debug(f"Loading API keys from {keys_file_path}")
            try:
                with open(keys_file_path, 'r') as keys_file:
                    for line in keys_file:
                        line = line.strip()
                        if line and not line.startswith('#'):  # Skip empty lines and comments
                            self.api_keys.append(line)
                self.logger.debug(f"Loaded {len(self.api_keys)} API key(s) from file")
            except Exception as e:
                self.logger.error(f"Error reading keys file: {str(e)}")
        
        # If no keys from file, check environment variable
        if not self.api_keys:
            self.logger.warning("No keys found in file, checking environment variable")
            env_key = os.environ.get("GEMINI_API_KEY")
            if env_key:
                self.api_keys.append(env_key)
                self.logger.debug("Added API key from GEMINI_API_KEY environment variable")
            else:
                self.logger.warning("No API keys found in gemini.keys file or environment variables")

    def set_api_key(self, api_key):
        """Set the API key for Gemini."""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def llm_call(self, messages, type_json=False, model=None):
        """
        Make an LLM call with rate limiting and retry logic
        
        Args:
            messages: The messages to send to the LLM
            type_json (bool): Whether to parse the response as JSON
            model (str, optional): The model to use for this call. Defaults to self.model.
        """
        # Use provided model or fall back to default
        used_model = model or self.model
        current_api_key = None
        
        # If all keys are exhausted, wait and reset
        if len(self.exhausted_keys) >= len(self.api_keys) and len(self.api_keys) > 0:
            self.logger.warning("All API keys have hit rate limits. Waiting 60 seconds before retrying...")
            time.sleep(90)  # Wait for 60 seconds
            self.exhausted_keys.clear()  # Reset exhausted keys
            self.logger.info("Resetting all API keys after waiting period")
        
        try:
            # Select an API key that isn't exhausted
            available_keys = [key for key in self.api_keys if key not in self.exhausted_keys]
            
            if available_keys:
                current_api_key = random.choice(available_keys)
                self.set_api_key(current_api_key)
                self.logger.debug(f"Using API key that hasn't hit rate limits ({len(available_keys)}/{len(self.api_keys)} available)")
            elif self.api_keys:
                current_api_key = random.choice(self.api_keys)
                self.set_api_key(current_api_key)
                self.logger.warning("All keys have hit rate limits, using random key")
            else:
                self.logger.warning("No API keys available")
                return "[]" if type_json else ""
            
            # Rate limiting
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last_request)
            
            self.logger.debug("Preparing LLM request...")
            self.logger.debug(f"Sending request to Gemini model: {used_model}")
            
            generate_content_config = genai.GenerationConfig(
                temperature=0,  # Use 0 temperature for more deterministic results
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="text/plain",
            )
            
            genai_model = genai.GenerativeModel(used_model)
            
            self.logger.debug("Sending request to Gemini...")
            try:
                response = genai_model.generate_content(contents=messages, generation_config=generate_content_config)
            except Exception as e:
                if "429" in str(e):  # API quota error
                    self.logger.warning(f"⚠️ API quota exceeded for key. Adding to exhausted keys.")
                    # Add this key to exhausted keys
                    if current_api_key:
                        self.exhausted_keys.add(current_api_key)
                        self._update_api_key_stats(current_api_key, used_model, success=False, error="API quota exceeded")
                    
                    # Try another key if available
                    if len(self.exhausted_keys) < len(self.api_keys):
                        self.logger.info(f"Switching to different API key after rate limit (exhausted {len(self.exhausted_keys)}/{len(self.api_keys)})")
                        # Recursively call the function with the same parameters to try with a different key
                        return self.llm_call(messages, type_json, model)
                    else:
                        # All keys exhausted, will trigger the wait/reset at next call
                        raise
                
                # Update API key stats with failure
                if current_api_key:
                    self._update_api_key_stats(current_api_key, used_model, success=False, error=str(e))
                raise  # Re-raise other exceptions
            
            self.logger.debug("Received response from Gemini")
            
            # Update API key stats with success
            if current_api_key:
                self._update_api_key_stats(current_api_key, used_model, success=True)
            
            if not response.candidates:
                self.logger.warning("⚠️ Warning: Empty response from Gemini")
                return "[]" if type_json else ""
            
            content = response.text
            self.logger.debug(f"Extracted content length: {len(content)}")
            
            if type_json:
                self.logger.debug("Attempting to parse response as JSON...")
                try:
                    # Handle markdown code block formatting if present
                    if content.startswith("```json"):
                        content = content[7:]  # Remove ```json
                    if content.endswith("```"):
                        content = content[:-3]  # Remove ```
                    content = content.strip()  # Remove any extra whitespace
    
                    json_response = json.loads(content)
                    self.logger.debug("Successfully parsed JSON response")
                    return json_response
                except json.JSONDecodeError as e:
                    self.logger.warning(f"❌ Error parsing JSON response: {str(e)}")
                    print(f"content: {content}") # In case of error, print the content
                    return []
            
            return content
                
        except Exception as e:
            error_message = f"""
LLM Call Error:
Type: {type(e).__name__}
Message: {str(e)}
Model: {used_model}
"""
            self.logger.error(error_message)
            self.logger.error(traceback.format_exc())
            raise
        
        finally:
            self.last_request_time = time.time()

    def create_text_message(self, system_prompt='', user_prompt=''):
        """Create properly formatted message for Gemini"""
        return str(system_prompt) + ' ' + str(user_prompt)

    def create_image_message(self, user_prompt, image_base64_list):
        """
        Create message with multiple images for LLM processing
        
        Args:
            user_prompt (str): The prompt text
            image_base64_list (str|list): Single image base64 string or list of base64 strings
        """
        # Convert single image to list for uniform handling
        if isinstance(image_base64_list, str):
            image_base64_list = [image_base64_list]

        # Create list with all images followed by prompt
        image_message = [
            {'mime_type': 'image/jpeg', 'data': img} 
            for img in image_base64_list
        ]
        image_message.append(user_prompt)

        return image_message

    def process_text(self, system_prompt, user_prompt, type_json=False, model=None):
        """
        Process a text request with Gemini
        
        Args:
            system_prompt (str): The system prompt/instructions
            user_prompt (str): The user query
            type_json (bool): Whether to parse response as JSON
            model (str, optional): The model to use for this call. Defaults to self.model.
            
        Returns:
            The processed response (text or JSON)
        """
        messages = self.create_text_message(system_prompt, user_prompt)
        return self.llm_call(messages, type_json=type_json, model=model)

    def process_image(self, user_prompt, image_base64_list, type_json=True, model=None):
        """
        Process multiple images with Gemini
        
        Args:
            user_prompt (str): The prompt text
            image_base64_list (str|list): Single image base64 string or list of base64 strings
            type_json (bool): Whether to parse response as JSON
            model (str, optional): The model to use for this call. Defaults to self.model.
            
        Returns:
            The processed response (text or JSON)
        """
        try:
            self.logger.debug("Preparing image processing request...")
            
            # Log number of images being processed
            if isinstance(image_base64_list, list):
                self.logger.debug(f"Processing {len(image_base64_list)} images...")
            else:
                self.logger.debug("Processing single image...")
            
            messages = self.create_image_message(user_prompt, image_base64_list)
            
            self.logger.debug(f"Sending request to Gemini model: {model or self.model}")
            response = self.llm_call(messages, type_json=type_json, model=model)
            
            self.logger.debug("Successfully received Gemini response")
            return response
            
        except Exception as e:
            error_trace = traceback.format_exc()
            error_msg = f"""
Image Processing Error:
Type: {type(e).__name__}
Message: {str(e)}
Model: {model or self.model}
Number of Images: {len(image_base64_list) if isinstance(image_base64_list, list) else 1}
Stack Trace:
{error_trace}
"""
            self.logger.error(error_msg)
            raise

    def __call__(self, *args, **kwargs):
        return NotImplementedError("LLM processors must implement the __call__ method")
    #  This is written because the BaseProcessor class requires it.
    #  But We will actually implement the __call__ method in the processor that extends this class.