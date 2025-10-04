from typing import Any, Optional

import os
from PIL import Image
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from src.AiHelper.common._logger import RobotCustomLogger


class AppiumService:
    """Façade centralisant les interactions avec Appium côté mobile.

    Objectif: un point d'entrée unique pour récupérer le driver, le XML,
    les screenshots, et tout autre utilitaire mobile.
    """

    def __init__(self) -> None:
        self.logger = RobotCustomLogger()

    # ---- Driver & session ----
    def get_driver(self) -> Any:
        appium_lib = BuiltIn().get_library_instance('AppiumLibrary')
        return appium_lib._current_application()

    def get_appium_library(self) -> Any:
        return BuiltIn().get_library_instance('AppiumLibrary')

    # ---- UI & screenshots ----
    def get_ui_xml(self) -> str:
        return self.get_driver().page_source

    def get_screenshot_base64(self) -> str:
        return self.get_driver().get_screenshot_as_base64()

    def embed_image_to_log(self, base64_screenshot: str, width: int = 400, message: Optional[str] = None) -> None:
        msg = f"{message if message else ''}</td></tr><tr><td colspan=\"3\"><img src=\"data:image/png;base64, {base64_screenshot}\" width=\"{width}\"></td></tr>"
        logger.info(msg, html=True, also_console=False)

    # ---- Convenience ----
    def save_reduced_screenshot(self, output_filename: str = "reduced_screenshot.png", resize_factor: int = 2) -> None:
        driver = self.get_driver()
        output_dir = self._get_log_dir()

        screenshot_path = f"{output_dir}/base_screenshot_before_reduction.png"
        reduced_screenshot_path = f"{output_dir}/{output_filename}"

        driver.save_screenshot(screenshot_path)
        image = Image.open(screenshot_path)
        reduced_image = image.resize(
            (image.width // resize_factor, image.height // resize_factor),
            Image.LANCZOS,
        )
        reduced_image.save(reduced_screenshot_path)

    # ---- Internals ----
    def _get_log_dir(self) -> str:
        variables = BuiltIn().get_variables()
        logfile = variables.get('${LOG FILE}', 'NONE')
        if logfile != 'NONE':
            return os.path.dirname(logfile)
        return variables.get('${OUTPUTDIR}', '.')


