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
        # Image uploader is optional; if not configured, we'll gracefully skip image embedding
        try:
            self.image_uploader = ImageUploader(service="auto")
        except Exception as e:
            self.logger.warning(f"Image uploader not configured: {e}")
            self.image_uploader = None

    # ----------------------- Public API -----------------------
    def run_do(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        resolved_image_url = self._resolve_image_url(image_url, image_base64)
        messages = self.prompt.compose_do_messages(
            instruction=instruction,
            ui_elements=ui_elements,
            image_url=resolved_image_url,
        )
        return self._run(messages, temperature=temperature)


    def run_check(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        resolved_image_url = self._resolve_image_url(image_url, image_base64)
        messages = self.prompt.compose_check_messages(
            instruction=instruction,
            ui_elements=ui_elements,
            image_url=resolved_image_url,
        )
        return self._run(messages, temperature=temperature)

    # ----------------------- Internals -----------------------
    def _run(self, messages: List[Dict[str, Any]], temperature: float = 0.0) -> Dict[str, Any]:
        self.logger.info("⏳ Sending prepared messages to AI...")
        result = self.llm.send_ai_request_and_return_response(messages, temperature=temperature)
        self.logger.info(f"📦 AI response parsed: {result}")
        return result


    def _resolve_image_url(self, image_url: Optional[str], image_base64: Optional[str]) -> Optional[str]:
        if image_url:
            return image_url
        if image_base64 and self.image_uploader is not None:
            try:
                uploaded_url = self.image_uploader.upload_from_base64(image_base64)
                if uploaded_url:
                    self.logger.info("🖼️ Image uploaded successfully; using URL in prompt")
                    return uploaded_url
            except Exception as e:
                self.logger.warning(f"Skipping image upload (error): {e}")
        return None



