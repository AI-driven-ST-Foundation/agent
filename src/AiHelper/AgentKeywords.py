from typing import Any, Dict, List, Optional

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from src.AiHelper.common._logger import RobotCustomLogger
from src.AiHelper.common._utils import Utilities
from src.AiHelper.providers.llm._factory import LLMClientFactory
from src.AiHelper.providers.llm.agent_prompt import AgentPromptComposer


class AgentKeywords:
    """
    Robot Framework library exposing two high-level keywords:
    - Agent.Do <instruction>
    - Agent.Check <instruction>

    Each keyword captures current UI context, composes a strict JSON prompt,
    calls the LLM with temperature=0, and executes the mapped AppiumLibrary action.
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, llm_client: str = "openai", llm_model: str = "gpt-4o-mini"):
        self.logger = RobotCustomLogger()
        self.prompt = AgentPromptComposer(locale="fr")
        self.client = LLMClientFactory.create_client(llm_client, model=llm_model)

    # ----------------------- Public RF Keywords -----------------------
    def agent_do(self, instruction: str):
        """Agent.Do <instruction>
        Example: Agent.Do    accepte les cookies
        """
        ui_candidates = self._extract_ui_candidates()
        image_url = None  # optional: externalize screenshot if desired
        messages = self.prompt.compose_do_messages(instruction, ui_candidates, image_url)

        response = self.client.create_chat_completion(
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = self.client.format_response(response).get("content", "{}")
        result = Utilities.extract_json_safely(content)
        self.logger.info(f"Agent.Do response: {result}")

        self._execute_do_result(result)

    def agent_check(self, instruction: str):
        """Agent.Check <instruction>
        Example: Agent.Check    l'écran affiche bien la carte
        """
        ui_candidates = self._extract_ui_candidates()
        image_url = None
        messages = self.prompt.compose_check_messages(instruction, ui_candidates, image_url)

        response = self.client.create_chat_completion(
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = self.client.format_response(response).get("content", "{}")
        result = Utilities.extract_json_safely(content)
        self.logger.info(f"Agent.Check response: {result}")

        self._execute_check_result(result)

    # ----------------------- Helpers -----------------------
    def _extract_ui_candidates(self) -> List[Dict[str, Any]]:
        """Extracts a compact list of UI elements from page_source.
        MVP heuristic: rely on raw XML text and simple patterns later; for now, return empty list.
        """
        try:
            xml = Utilities._get_ui_xml()
            # Future: parse XML to top-K candidates (text, id, content-desc, class)
            return []
        except Exception as e:
            self.logger.warning(f"Failed to extract UI XML: {e}")
            return []

    def _execute_do_result(self, result: Dict[str, Any]):
        action = result.get("action")
        locator = result.get("locator", {})
        text = result.get("text")
        candidates = result.get("candidates", []) or []

        if action == "open":
            self._rf().open_application()
            return

        if not locator and candidates:
            # try first candidate if locator missing
            locator = candidates[0]

        rf_locator = self._to_rf_locator(locator)

        if action == "tap":
            self._rf().click_element(rf_locator)
            return
        if action == "type":
            if text is None:
                raise AssertionError("Agent.Do 'type' requires 'text'")
            self._rf().input_text(rf_locator, text)
            return
        if action == "clear":
            self._rf().clear_text(rf_locator)
            return
        if action == "swipe":
            # For MVP, skip detailed swipe options; can be extended later
            raise AssertionError("Swipe not yet implemented in Agent.Do")

        raise AssertionError(f"Unsupported action: {action}")

    def _execute_check_result(self, result: Dict[str, Any]):
        assertion = result.get("assertion")
        locator = result.get("locator", {})
        expected = result.get("expected")
        candidates = result.get("candidates", []) or []

        if not locator and candidates:
            locator = candidates[0]

        rf_locator = self._to_rf_locator(locator)

        if assertion in ("visible", "exists"):
            self._rf().page_should_contain_element(rf_locator)
            return
        if assertion == "text_contains":
            if expected is None:
                raise AssertionError("Agent.Check 'text_contains' requires 'expected'")
            self._rf().element_should_contain_text(rf_locator, str(expected))
            return

        raise AssertionError(f"Unsupported assertion: {assertion}")

    def _to_rf_locator(self, locator: Dict[str, Any]) -> str:
        strategy = locator.get("strategy")
        value = locator.get("value")
        if not strategy or not value:
            raise AssertionError("Locator must include 'strategy' and 'value'")

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
        return value

    def _rf(self):
        return BuiltIn().get_library_instance('AppiumLibrary')



