import base64
import os
from robot.libraries.BuiltIn import BuiltIn
from PIL import Image
from robot.api import logger
import json
import re
from typing import Any, Dict

class Utilities:
        
    @staticmethod
    def _get_log_dir() -> str:
        variables = BuiltIn().get_variables()
        logfile = variables['${LOG FILE}']
        if logfile != 'NONE':
            return os.path.dirname(logfile)
        return variables['${OUTPUTDIR}']
    
    @staticmethod
    def _get_driver():
        built_in = BuiltIn()
        appium_lib = built_in.get_library_instance('AppiumLibrary')
        return appium_lib._current_application()

    @staticmethod
    def _get_ui_xml():
        return Utilities._get_driver().page_source
    
    @staticmethod
    def _take_screenshot_as_base64():
        return Utilities._get_driver().get_screenshot_as_base64()
    
    @staticmethod
    def _embed_image_to_log(base64_screenshot, width=400, message=None):
        logger.info(f'{message if message else ""}</td></tr><tr><td colspan="3">'
                       '<img src="data:image/png;base64, %s" width="%s">' % (base64_screenshot, width), True, False)

    @staticmethod
    def encode_image_to_base64(file_path: str):
        with open(file_path, "rb") as image_file:
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
        return base64_data

    @staticmethod
    def extract_json_safely(response: str) -> Dict[str, Any]:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    raise ValueError("Extracted content is not valid JSON.")
            else:
                raise ValueError("No JSON content found in the response.")


    @staticmethod
    def _capture_screenshot_and_reduce_size(output_filename="reduced_screenshot.png", resize_factor=2):
        try:
            driver = Utilities._get_driver()
            output_dir = Utilities._get_log_dir()

            screenshot_path = f"{output_dir}/base_screenshot_before_reduction.png"
            reduced_screenshot_path = f"{output_dir}/{output_filename}"

            driver.save_screenshot(screenshot_path)
            image = Image.open(screenshot_path)
            reduced_image = image.resize(
                (image.width // resize_factor, image.height // resize_factor),
                Image.LANCZOS
            )
            reduced_image.save(reduced_screenshot_path)
        except Exception as e:
            raise Exception(f"Error in _take_and_reduce_screenshot: {str(e)}")
