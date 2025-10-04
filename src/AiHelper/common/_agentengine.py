from typing import Any, Dict, List, Optional

from src.AiHelper.common._logger import RobotCustomLogger
from src.AiHelper.common._jsonutils import extract_json_safely
from src.AiHelper.robot._executor import RobotKeywordExecutor
from src.AiHelper.common.platforms._base import UiPlatformAdapter
from src.AiHelper.common.platforms._appium import AppiumPlatformAdapter
from src.AiHelper.providers.llm._factory import LLMClientFactory
from src.AiHelper.providers.llm.agent_prompt import AgentPromptComposer


class AgentEngine:
    """Orchestre les flux Agent.Do et Agent.Check sans dépendre de Robot Framework.

    Cette classe encapsule:
      - la capture du contexte UI
      - la composition des prompts (Do/Check)
      - l'appel LLM (réponse strict JSON)
      - l'exécution/vérification via RobotKeywordExecutor

    Objectif: permettre à `AgentKeywords` de déléguer proprement, pour faciliter
    l'évolution de l'architecture sans casser l'existant.
    """

    def __init__(self, llm_client: str = "openai", llm_model: str = "gpt-4o-mini", platform: Optional[UiPlatformAdapter] = None) -> None:
        self.logger = RobotCustomLogger()
        self.prompt = AgentPromptComposer(locale="fr")
        self.client = LLMClientFactory.create_client(llm_client, model=llm_model)
        self.executor = RobotKeywordExecutor()
        # Default to Appium platform, injectable for web/other in future
        self.platform: UiPlatformAdapter = platform or AppiumPlatformAdapter()

    # ----------------------- Public API -----------------------
    def do(self, instruction: str) -> None:
        self.logger.info(f"🚀 Début Agent.Do avec instruction: '{instruction}'")

        ui_candidates = self._extract_ui_candidates()
        image_url = None

        self.logger.info("📝 Composition du prompt pour l'IA...")
        messages = self.prompt.compose_do_messages(instruction, ui_candidates, image_url)

        system_prompt = messages[0]["content"]
        self.logger.info("🤖 Prompt système envoyé à l'IA:")
        self.logger.info(f"   {system_prompt}")

        user_content = messages[1]["content"]
        user_text = user_content[0]["text"] if isinstance(user_content, list) and user_content else str(user_content)
        self.logger.info("👤 Prompt utilisateur envoyé à l'IA:")
        self.logger.info(f"   {user_text}")

        self.logger.info("⏳ Envoi de l'IA...")
        response = self.client.create_chat_completion(
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = self.client.format_response(response).get("content", "{}")
        self.logger.info("📥 Réponse brute de l'IA reçue:")
        self.logger.info(f"   {content}")

        result = extract_json_safely(content)
        self.logger.info(f"✅ Réponse JSON parsée: {result}")

        self.logger.info("⚡ Exécution de l'action...")
        self._execute_do_result(result, instruction)
        self.logger.success("✅ Agent.Do terminé avec succès")

    def check(self, instruction: str) -> None:
        self.logger.info(f"🔍 Début Agent.Check avec instruction: '{instruction}'")

        ui_candidates = self._extract_ui_candidates()
        image_url = None

        self.logger.info("📝 Composition du prompt pour l'IA...")
        messages = self.prompt.compose_check_messages(instruction, ui_candidates, image_url)

        system_prompt = messages[0]["content"]
        self.logger.info("🤖 Prompt système envoyé à l'IA:")
        self.logger.info(f"   {system_prompt}")

        user_content = messages[1]["content"]
        user_text = user_content[0]["text"] if isinstance(user_content, list) and user_content else str(user_content)
        self.logger.info("👤 Prompt utilisateur envoyé à l'IA:")
        self.logger.info(f"   {user_text}")

        self.logger.info("⏳ Envoi de l'IA...")
        response = self.client.create_chat_completion(
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = self.client.format_response(response).get("content", "{}")
        self.logger.info("📥 Réponse brute de l'IA reçue:")
        self.logger.info(f"   {content}")

        result = extract_json_safely(content)
        self.logger.info(f"✅ Réponse JSON parsée: {result}")

        self.logger.info("⚡ Exécution de la vérification...")
        self._execute_check_result(result)
        self.logger.success("✅ Agent.Check terminé avec succès")

    # ----------------------- Internals -----------------------
    def _extract_ui_candidates(self) -> List[Dict[str, Any]]:
        try:
            self.logger.info("🔍 Extraction du contexte UI en cours...")
            xml = self.platform.get_ui_xml()
            xml_length = len(xml)

            xml_preview = xml[:1000] + "..." if xml_length > 1000 else xml
            self.logger.info(f"📱 XML UI récupéré ({xml_length} caractères)")
            self.logger.debug(f"📋 Aperçu XML (tronqué): {xml_preview}")

            candidates = self.platform.parse_ui(xml)

            self.logger.info(f"🎯 Nombre de candidats UI extraits: {len(candidates)}")
            for i, candidate in enumerate(candidates[:5]):
                self.logger.debug(f"  Candidat {i+1}: {candidate}")

            return candidates
        except Exception as exc:
            self.logger.error(f"❌ Échec extraction UI XML: {exc}")
            return []

    def _execute_do_result(self, result: Dict[str, Any], instruction: str) -> None:
        self.logger.info("🔧 Analyse de la réponse pour exécution...")
        action = result.get("action")
        locator = result.get("locator", {})
        text = result.get("text")
        candidates = result.get("candidates", []) or []

        self.logger.info(f"🎬 Action demandée: {action}")
        self.logger.info(f"📍 Locator fourni: {locator}")
        self.logger.info(f"📝 Texte à saisir: {text}")
        self.logger.info(f"🎯 Candidats alternatifs: {candidates}")

        if action == "open":
            self.logger.info("🚪 Exécution: Open Application")
            try:
                self.executor.run("Open Application")
                self.logger.success("✅ Application ouverte avec succès")
            except Exception as e:
                self.logger.error(f"❌ Échec ouverture application: {e}")
                raise
            return

        if not locator:
            raise AssertionError("Aucun locator disponible pour l'action")

        rf_locator = self.platform.to_rf_locator(locator)
        self.logger.info(f"🎯 Locator Robot Framework converti: {rf_locator}")

        if action == "tap":
            self.logger.info(f"👆 Exécution: Click Element avec locator '{rf_locator}'")
            try:
                self.executor.run("Click Element", rf_locator)
                self.logger.success("✅ Élément cliqué avec succès")
            except Exception as e:
                self.logger.error(f"❌ Échec clic élément: {e}")
                raise
            return

        if action == "type":
            if text is None:
                text = self._extract_text_from_instruction(instruction)
                if text is None:
                    raise AssertionError("Agent.Do 'type' requires 'text'")
                self.logger.info(f"📝 Texte extrait automatiquement de l'instruction: '{text}'")

            self.logger.info(f"⌨️ Exécution: Input Text '{text}' dans locator '{rf_locator}'")
            try:
                self.executor.run("Input Text", rf_locator, text)
                self.logger.success("✅ Texte saisi avec succès")
            except Exception as e:
                self.logger.error(f"❌ Échec saisie texte: {e}")
                raise
            return

        if action == "clear":
            self.logger.info(f"🧹 Exécution: Clear Text pour locator '{rf_locator}'")
            try:
                self.executor.run("Clear Text", rf_locator)
                self.logger.success("✅ Texte effacé avec succès")
            except Exception as e:
                self.logger.error(f"❌ Échec effacement texte: {e}")
                raise
            return

        if action == "swipe":
            self.logger.error("🚫 Action 'swipe' pas encore implémentée")
            raise AssertionError("Swipe not yet implemented in Agent.Do")

        self.logger.error(f"🚫 Action non supportée: {action}")
        raise AssertionError(f"Unsupported action: {action}")

    def _execute_check_result(self, result: Dict[str, Any]) -> None:
        self.logger.info("🔍 Analyse de la réponse pour vérification...")

        assertion = result.get("assertion")
        locator = result.get("locator", {})
        expected = result.get("expected")
        candidates = result.get("candidates", []) or []

        self.logger.info(f"🔍 Assertion demandée: {assertion}")
        self.logger.info(f"📍 Locator fourni: {locator}")
        self.logger.info(f"📋 Valeur attendue: {expected}")
        self.logger.info(f"🎯 Candidats alternatifs: {candidates}")

        if not locator and candidates:
            locator = candidates[0]
            self.logger.info(f"🔄 Aucun locator principal, utilisation du premier candidat: {locator}")

        if not locator:
            raise AssertionError("Aucun locator disponible pour la vérification")

        rf_locator = self.platform.to_rf_locator(locator)
        self.logger.info(f"🎯 Locator Robot Framework converti: {rf_locator}")

        if assertion in ("visible", "exists"):
            self.logger.info(f"👁️ Exécution: Page Should Contain Element avec locator '{rf_locator}'")
            try:
                self.executor.run("Page Should Contain Element", rf_locator)
                self.logger.success("✅ Vérification réussie: élément présent")
            except Exception as e:
                self.logger.error(f"❌ Échec vérification visibilité: {e}")
                raise
            return

        if assertion == "text_contains":
            if expected is None:
                raise AssertionError("Agent.Check 'text_contains' requires 'expected'")
            self.logger.info(f"📝 Exécution: Element Should Contain Text '{expected}' dans locator '{rf_locator}'")
            try:
                self.executor.run("Element Should Contain Text", rf_locator, str(expected))
                self.logger.success("✅ Vérification réussie: texte présent")
            except Exception as e:
                self.logger.error(f"❌ Échec vérification texte: {e}")
                raise
            return

        self.logger.error(f"🚫 Assertion non supportée: {assertion}")
        raise AssertionError(f"Unsupported assertion: {assertion}")

    # Locator conversion is now delegated to the platform adapter

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


