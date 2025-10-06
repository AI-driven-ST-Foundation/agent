from typing import Any, Dict, List, Optional

from src.AiHelper.utilities._logger import RobotCustomLogger
from src.AiHelper.agent.llm.facade import UnifiedLLMFacade
from src.AiHelper.agent._promptcomposer import AgentPromptComposer
from src.AiHelper.utilities.imguploader.imghandler import ImageUploader


class AiConnector:
    """AI connector only: accepts prepared messages, returns parsed JSON result."""

    def __init__(self, provider: str = "openai", model: Optional[str] = "gpt-4o-mini") -> None:
        self.logger = RobotCustomLogger()
        self.llm = UnifiedLLMFacade(provider=provider, model=model)
        self.prompt = AgentPromptComposer(locale="fr")
        # Image uploader never crashes; fallbacks to base64 if no provider configured
        self.image_uploader = ImageUploader(service="auto")

    # ----------------------- Public API -----------------------
    def ask_ai_do(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:

        messages = self.prompt.compose_do_messages(
            instruction=instruction,
            ui_elements=ui_elements,
        )
        return self._run(messages, temperature=temperature)


    def ask_ai_visual_check(
        self,
        instruction: str,
        image_base_or_url: Optional[str] = None,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        messages = self.prompt.compose_visual_check_messages(
            instruction=instruction,
            image_url=image_base_or_url,
        )
        return self._run(messages, temperature=temperature)

    # ----------------------- Internals -----------------------
    def _run(self, messages: List[Dict[str, Any]], temperature: float = 0.0) -> Dict[str, Any]:
        self.logger.info("⏳ Sending prepared messages to AI...")
        result = self.llm.send_ai_request_and_return_response(messages, temperature=temperature)
        self.logger.info(f"📦 AI response parsed: {result}")
        return result



