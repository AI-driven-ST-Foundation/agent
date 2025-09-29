from Libraries.AiHelper.common._logger import RobotCustomLogger
from Libraries.AiHelper.common._utils import Utilities
from Libraries.AiHelper.providers.imguploader.imghandler import ImageUploader

class ChatPromptFactory:

    def __init__(self):
        self.logger = RobotCustomLogger()
        self.img_uploader = ImageUploader()

    def create_system_prompt(self,system_prompt: str) -> dict:
        self.logger.info(f"From ChatPromptFactory: Creating system prompt: {system_prompt}")
        return {
            "role": "system",
            "content": system_prompt
        }

    def create_user_prompt(self,text: str, image_url: str = None) -> dict:
        text_item = {
            "type": "text",
            "text": text
        }
        
        content = [text_item]
        
        if image_url is not None:
            image_item = {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
            content.append(image_item)
        self.logger.info(f"From ChatPromptFactory: User prompt created: {content}")
        return {
            "role": "user",
            "content": content
        }
    
    def create_user_prompt_sending_current_screenshot(self,text: str, log_image: bool = False, width: int = 200) -> dict:
        self.logger.info(f"From ChatPromptFactory: Creating current screenshot prompt: {text}")
        screenshot_base64 = Utilities._take_screenshot_as_base64()
        screenshot_url = self.img_uploader.upload_from_base64(screenshot_base64)
        if log_image:
            Utilities._embed_image_to_log(screenshot_base64, width=width, message="Actual app screenshot")
        return self.create_user_prompt(text, screenshot_url)
    
    def create_user_prompt_sending_current_UI_XML(self,text: str) -> dict:
        self.logger.info(f"From ChatPromptFactory: Sending current UI XML prompt: {text}")
        current_ui_xml = Utilities._get_ui_xml()
        text= text + "\n\n" + current_ui_xml
        return self.create_user_prompt(text)
    
    def create_user_prompt_sending_reference_screenshot(self,text: str, image_path: str, log_image: bool = False, width: int = 200) -> dict:
        self.logger.info(f"From ChatPromptFactory: Creating reference screenshot prompt: {text}")
        image_url = self.img_uploader.upload_from_file(image_path)
        self.logger.info(f" From ChatPromptFactory: Reference image path : {image_path} - \n"+
                             f" Reference screenshot uploaded: {image_url}")

        if log_image:
            Utilities._embed_image_to_log(Utilities.encode_image_to_base64(image_path), width=width, message="Reference screenshot")
        return self.create_user_prompt(text, image_url)
