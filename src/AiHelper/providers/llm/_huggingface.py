import base64
import os
from typing import Dict, List, Optional, Any, Union
from PIL import Image
import io
from gradio_client import Client, handle_file
from robot.libraries.BuiltIn import BuiltIn
from Libraries.AiHelper.common._logger import RobotCustomLogger
class OmniParser:
    """Client for Microsoft's OmniParser v2 model on Hugging Face."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OmniParser client.
        
        Args:
            api_key: Optional Hugging Face API key for private spaces
        """
        self.client = Client(
            "microsoft/OmniParser-v2",
            hf_token=api_key
        )
        self.logger = RobotCustomLogger()

    def parse_screenshot(
        self, 
        image: Union[str, Image.Image, bytes],
        box_threshold: float = 0.05,
        iou_threshold: float = 0.1,
        use_paddleocr: bool = True,
        imgsz: int = 640
    ) -> List[Dict[str, Any]]:
        """Parse a screenshot using OmniParser.
        
        Args:
            image: Path to image file, PIL Image, or bytes of image
            box_threshold: Confidence threshold for bounding boxes
            iou_threshold: IOU threshold for NMS
            use_paddleocr: Whether to use PaddleOCR for text detection
            imgsz: Image size for icon detection
            
        Returns:
            List of detected elements with their properties
        """
        # Handle different image input types
        if isinstance(image, str):
            # Path to image file - use handle_file directly
            image_input = handle_file(image)
        elif isinstance(image, Image.Image):
            # PIL Image - save to temporary file and use handle_file
            temp_path = "temp_image.png"
            image.save(temp_path)
            image_input = handle_file(temp_path)
            os.remove(temp_path)  # Clean up temp file
        elif isinstance(image, bytes):
            # Raw bytes - save to temporary file and use handle_file
            temp_path = "temp_image.png"
            with open(temp_path, "wb") as f:
                f.write(image)
            image_input = handle_file(temp_path)
            os.remove(temp_path)  # Clean up temp file
        else:
            raise ValueError("Image must be a file path, PIL Image, or bytes")
        
        
        try:
            _, result_text = self.client.predict(
                image_input=image_input,
                box_threshold=box_threshold,
                iou_threshold=iou_threshold,
                use_paddleocr=use_paddleocr,
                imgsz=imgsz,
                api_name="/process"
            )
        except Exception as e:
            print(f"Erreur lors de l'appel à OmniParser: {e}")
            return []
        
        parsed_elements = self._parse_response(result_text)
        return parsed_elements
    
    def _parse_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the text response from OmniParser into structured data.
        
        Args:
            response_text: Raw text response from OmniParser
            
        Returns:
            List of parsed elements
        """
        elements = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            if not line.startswith('icon '):
                continue
                
            try:
                # icon index and content
                icon_idx, content = line.split(':', 1)
                icon_idx = int(icon_idx.replace('icon ', ''))
                
                # parsing dictionary-like string
                element_dict = eval(content.strip())
                element_dict['id'] = icon_idx
                elements.append(element_dict)
            except Exception as e:
                print(f"Error parsing line: {line}, Error: {e}")
                continue
                
        return elements


    def analyze_screenshot_with_omniparser(self, screenshot_base64=None, embed_to_log=True):
        """Analyze screenshot with OmniParser.
        
        Args:
            screenshot_base64: Base64 encoded screenshot. If None, captures current screen.
            embed_to_log: Whether to embed the screenshot in the log
            
        Returns:
            List of detected UI elements with their properties
        """
        # If no screenshot provided, capture one
        built_in = BuiltIn()
        driver = built_in.get_library_instance("AppiumLibrary")._current_application()

        if screenshot_base64 is None:
            screenshot_base64 = self._capture_page_screenshot(embed_to_log=embed_to_log)
        
        # Convert base64 to bytes
        screenshot_bytes = base64.b64decode(screenshot_base64)
        
        # Initialize OmniParser
        # Try to get API key from environment variable
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        parser = OmniParser(api_key=api_key)
        
        # Send screenshot to OmniParser and get results
        try:
            elements = parser.parse_screenshot(
                image=screenshot_bytes,
                box_threshold=0.05,
                iou_threshold=0.1
            )
            
            # Log the detected elements
            self.logger.info(f"Detected {len(elements)} UI elements on screen")
            
            return elements
            
        except Exception as e:
            self.logger.error(f"Error analyzing screen with OmniParser: {e}")
            return []
    
    def find_ui_element(self, 
                        text=None, 
                        element_type=None, 
                        interactive_only=False, 
                        partial_match=True,
                        screenshot_base64=None):
        """Find UI element based on criteria using OmniParser.
        
        Args:
            text: Text content to search for
            element_type: Type of element to search for ('text', 'icon', etc.)
            interactive_only: Whether to only return interactive elements
            partial_match: Whether to allow partial text matches
            screenshot_base64: Base64 encoded screenshot. If None, captures current screen.
            
        Returns:
            List of matching elements
        """
        elements = self.analyze_screenshot_with_omniparser(
            screenshot_base64=screenshot_base64, 
            embed_to_log=False
        )
        
        matching_elements = []
        
        for element in elements:
            # Check if element matches criteria
            matches = True
            
            if text is not None:
                content = element.get('content', '')
                if partial_match:
                    matches = matches and (text.lower() in content.lower())
                else:
                    matches = matches and (text.lower() == content.lower())
            
            if element_type is not None:
                matches = matches and (element.get('type') == element_type)
            
            if interactive_only:
                matches = matches and element.get('interactivity', False)
            
            if matches:
                matching_elements.append(element)
        
        self.logger.info(f"Found {len(matching_elements)} matching elements")
        return matching_elements
    

#quick test
if __name__ == "__main__":
    parser = OmniParser()
    image_path = "/Users/abdelkaderhassine/Documents/IDFM-PRIM-VGM-SOURCE/Libraries/atest/img/screenshots/s5.jpeg"
    elements = parser.parse_screenshot(image_path)
    print(elements)