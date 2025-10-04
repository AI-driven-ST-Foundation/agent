from typing import Any, Dict, List

from src.AiHelper.common._logger import RobotCustomLogger
from src.AiHelper.common.platforms.appium._uiparser import UiParser
from src.AiHelper.common.platforms.appium._service import AppiumService
from src.AiHelper.common.platforms._base import UiPlatformAdapter


class AppiumPlatformAdapter(UiPlatformAdapter):
    """Appium implementation of UiPlatformAdapter."""

    def __init__(self) -> None:
        self.logger = RobotCustomLogger()
        self.parser = UiParser()
        self.service = AppiumService()

    def get_ui_xml(self) -> str:
        return self.service.get_ui_xml()

    def parse_ui(self, ui_xml: str, max_items: int = 20) -> List[Dict[str, Any]]:
        return self.parser.parse(ui_xml, max_items=max_items)

    def to_rf_locator(self, locator: Dict[str, Any]) -> str:
        strategy = locator.get("strategy")
        value = locator.get("value")

        if not strategy or not value:
            raise AssertionError("Locator doit inclure 'strategy' et 'value'")

        if strategy == "id":
            return f"id={value}"
        if strategy == "accessibility_id":
            return f"accessibility_id={value}"
        if strategy == "xpath":
            return value
        if strategy == "class_name":
            return f"class={value}"
        if strategy == "android_uiautomator":
            return f"android=uiautomator={value}"
        if strategy == "ios_predicate":
            return f"-ios predicate string:{value}"

        self.logger.warning(f"Unknown strategy '{strategy}', returning raw value")
        return value

    def get_locator_strategies(self) -> List[str]:
        return [
            "id",
            "accessibility_id",
            "xpath",
            "class_name",
            "android_uiautomator",
            "ios_predicate",
        ]