from typing import Any, Dict, List, Optional

from src.AiHelper.utilities._logger import RobotCustomLogger
from src.AiHelper.platforms import DeviceConnector
from src.AiHelper.agent._aiconnector import AiConnector


class AgentStepRunner:
    """Orchestrates the Agent.Do and Agent.Check flows without relying on Robot Framework.

    This class encapsulates:
      - capturing the UI context
      - composing prompts (Do/Check)
      - calling the LLM (strict JSON response)
      - executing/verifying via RobotKeywordExecutor

    Objective: allow `AgentKeywords` to delegate cleanly, to facilitate
    architectural evolution without breaking existing functionality.
    """

    def __init__(self, llm_client: str = "openai", llm_model: str = "gpt-4o-mini", platform: Optional[DeviceConnector] = None) -> None:
        self.logger = RobotCustomLogger()
        # Platform
        self.platform: DeviceConnector = platform or DeviceConnector()
        # Agent component
        self.agent = AiConnector(provider=llm_client, model=llm_model)

    # ----------------------- Public API -----------------------
    def do(self, instruction: str) -> None:
        self.logger.info(f"🚀 Starting Agent.Do with instruction: '{instruction}'")

        ui_candidates = self.platform.collect_ui_candidates()

        image_url = None
        result = self.agent.run_do(
            instruction=instruction,
            ui_elements=ui_candidates,
            image_url=image_url,
            image_base64=None,
            temperature=0,
        )

        self.logger.info("⚡ Executing action...")
        self._execute_do(result, instruction)
        self.logger.success("✅ Agent.Do completed successfully")

    def check(self, instruction: str) -> None:
        self.logger.info(f"🔍 Starting Agent.Check with instruction: '{instruction}'")

        ui_candidates = self.platform.collect_ui_candidates()
        image_url = None
        result = self.agent.run_check(
            instruction=instruction,
            ui_elements=ui_candidates,
            image_url=image_url,
            image_base64=None,
            temperature=0,
        )

        self.logger.info("⚡ Executing verification...")
        self._execute_check(result)
        self.logger.success("✅ Agent.Check completed successfully")

    # ----------------------- Internals -----------------------
    def _run_rf_keyword(self, keyword_name: str, *args: Any) -> Any:
        from robot.api import logger as rf_logger
        from robot.libraries.BuiltIn import BuiltIn
        try:
            args_str = " ".join([str(a) for a in args]) if args else ""
            rf_logger.info(f"EXECUTING: {keyword_name} {args_str}".strip())
            self.logger.info(f"▶️ RF: {keyword_name} {args_str}")

            result = BuiltIn().run_keyword(keyword_name, *args)

            rf_logger.info(f"SUCCESS: {keyword_name} executed successfully")
            self.logger.success(f"✅ RF success: {keyword_name}")
            return result
        except Exception as exc:
            rf_logger.error(f"FAILED: {keyword_name} - {exc}")
            self.logger.error(f"❌ RF failed: {keyword_name} - {exc}")
            raise

    def _extract_text_from_instruction(self, instruction: str) -> Optional[str]:
        import re

        patterns = [
            r'input this text[^:]*:\s*(.+)$',
            r'type this text[^:]*:\s*(.+)$',
            r'enter this text[^:]*:\s*(.+)$',
            r'write this text[^:]*:\s*(.+)$',
            r'input\s*:\s*(.+)$',
            r'type\s*:\s*(.+)$',
            r'enter\s*:\s*(.+)$',
            r'with text\s*["\']([^"\']+)["\']',
            r'["\']([^"\']+)["\']',
        ]

        instruction_lower = instruction.lower()
        for pattern in patterns:
            match = re.search(pattern, instruction_lower, re.IGNORECASE)
            if match:
                text = match.group(1).strip().strip('\"\'')
                if text:
                    return text
        return None

    def _execute_do(self, result: Dict[str, Any], instruction: str) -> None:
        action = result.get("action")
        locator = result.get("locator", {})
        text = result.get("text")
        candidates = result.get("candidates", []) or []

        self.logger.info(f"🎬 Requested action: {action}")
        self.logger.info(f"📍 Provided locator: {locator}")
        self.logger.info(f"📝 Text to input: {text}")
        self.logger.info(f"🎯 Alternative candidates: {candidates}")

        if action == "open":
            self.logger.info("🚪 Executing: Open Application")
            self._run_rf_keyword("Open Application")
            self.logger.success("✅ Application opened successfully")
            return

        if not locator:
            raise AssertionError("No locator available for the action")

        rf_locator = self.platform.to_rf_locator(locator)
        self.logger.info(f"🎯 Converted Robot Framework locator: {rf_locator}")

        if action == "tap":
            self.logger.info(f"👆 Executing: Click Element with locator '{rf_locator}'")
            self._run_rf_keyword("Click Element", rf_locator)
            self.logger.success("✅ Element clicked successfully")
            return

        if action == "type":
            if text is None:
                text = self._extract_text_from_instruction(instruction)
                if text is None:
                    raise AssertionError("Agent.Do 'type' requires 'text'")
                self.logger.info(f"📝 Text automatically extracted from instruction: '{text}'")
            self.logger.info(f"⌨️ Executing: Input Text '{text}' into locator '{rf_locator}'")
            self._run_rf_keyword("Input Text", rf_locator, text)
            self.logger.success("✅ Text entered successfully")
            return

        if action == "clear":
            self.logger.info(f"🧹 Executing: Clear Text for locator '{rf_locator}'")
            self._run_rf_keyword("Clear Text", rf_locator)
            self.logger.success("✅ Text cleared successfully")
            return

        if action == "swipe":
            self.logger.error("🚫 Action 'swipe' not yet implemented")
            raise AssertionError("Swipe not yet implemented in Agent.Do")

        self.logger.error(f"🚫 Unsupported action: {action}")
        raise AssertionError(f"Unsupported action: {action}")

    def _execute_check(self, result: Dict[str, Any]) -> None:
        assertion = result.get("assertion")
        locator = result.get("locator", {})
        expected = result.get("expected")
        candidates = result.get("candidates", []) or []

        self.logger.info(f"🔍 Requested assertion: {assertion}")
        self.logger.info(f"📍 Provided locator: {locator}")
        self.logger.info(f"📋 Expected value: {expected}")
        self.logger.info(f"🎯 Alternative candidates: {candidates}")

        if not locator and candidates:
            locator = candidates[0]
            self.logger.info(f"🔄 No primary locator, using first candidate: {locator}")

        if not locator:
            raise AssertionError("No locator available for verification")

        rf_locator = self.platform.to_rf_locator(locator)
        self.logger.info(f"🎯 Converted Robot Framework locator: {rf_locator}")

        if assertion in ("visible", "exists"):
            self.logger.info(f"👁️ Executing: Page Should Contain Element with locator '{rf_locator}'")
            self._run_rf_keyword("Page Should Contain Element", rf_locator)
            self.logger.success("✅ Verification succeeded: element present")
            return

        if assertion == "text_contains":
            if expected is None:
                raise AssertionError("Agent.Check 'text_contains' requires 'expected'")
            self.logger.info(f"📝 Executing: Element Should Contain Text '{expected}' in locator '{rf_locator}'")
            self._run_rf_keyword("Element Should Contain Text", rf_locator, str(expected))
            self.logger.success("✅ Verification succeeded: text present")
            return

        self.logger.error(f"🚫 Unsupported assertion: {assertion}")
        raise AssertionError(f"Unsupported assertion: {assertion}")
