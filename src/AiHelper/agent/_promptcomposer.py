from typing import List, Dict, Optional, Any

from src.AiHelper.utilities._logger import RobotCustomLogger
from src.AiHelper.platforms import DeviceConnector




class AgentPromptComposer:
    """
    Builds strict, deterministic prompts for the agent `do` and `check` flows.
    Includes the allowed keyword catalog and a JSON schema for the expected
    response so the LLM outputs a single actionable result.
    """

    def __init__(self, locale: str = "fr") -> None:
        self.locale = locale
        self.logger = RobotCustomLogger()
        self.catalog = AgentKeywordCatalog()

    # ---- Simple public wrappers for clarity ----
    def compose_do_messages(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Clear alias for building DO messages.

        Preferred entrypoint for action prompts.
        """
        return self._compose_do_messages(instruction, ui_elements, image_url)

    def compose_check_messages(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Clear alias for building CHECK messages.

        Preferred entrypoint for assertion prompts.
        """
        return self._compose_check_messages(instruction, ui_elements, image_url)

    # ----------------------- Internals -----------------------
    def _render_ui_candidates(self, ui_elements: Optional[List[Dict[str, Any]]]) -> str:
        if not ui_elements or len(ui_elements) == 0:
            return "(aucun élément UI interactif trouvé - vérifiez que l'app est bien ouverte)"
        rendered: List[str] = []
        for i, element in enumerate(ui_elements[:30], 1):
            text = element.get("text") or ""
            res_id = element.get("resource_id") or ""
            desc = element.get("content_desc") or ""
            clazz = element.get("class_name") or ""
            bounds = element.get("bounds") or ""

            # Construire une description complète de l'élément
            parts = []
            if text: parts.append(f"text='{text}'")
            if res_id: parts.append(f"id='{res_id}'")
            if desc: parts.append(f"desc='{desc}'")
            if clazz: parts.append(f"class='{clazz}'")

            description = " | ".join(parts) if parts else f"class='{clazz}'"
            rendered.append(f"{i}. {description}")
        return "\n".join(rendered)

    def _get_do_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["action", "locator"],
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [k["action"] for k in self.catalog._get_do_keywords()],
                },
                "locator": {
                    "type": "object",
                    "required": ["strategy", "value"],
                    "properties": {
                        "strategy": {
                            "type": "string",
                            "enum": self.catalog._get_locator_strategies(),
                        },
                        "value": {"type": "string"},
                    },
                },
                "text": {"type": ["string", "null"]},
                "options": {"type": ["object", "null"]},
                "candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["strategy", "value"],
                        "properties": {
                            "strategy": {"type": "string"},
                            "value": {"type": "string"},
                        },
                    },
                },
            },
            "additionalProperties": False,
        }

    def _get_check_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["assertion", "locator"],
            "properties": {
                "assertion": {
                    "type": "string",
                    "enum": [k["assertion"] for k in self.catalog._get_check_keywords()],
                },
                "locator": {
                    "type": "object",
                    "required": ["strategy", "value"],
                    "properties": {
                        "strategy": {
                            "type": "string",
                            "enum": self.catalog._get_locator_strategies(),
                        },
                        "value": {"type": "string"},
                    },
                },
                "expected": {"type": ["string", "number", "null"]},
                "candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["strategy", "value"],
                        "properties": {
                            "strategy": {"type": "string"},
                            "value": {"type": "string"},
                        },
                    },
                },
            },
            "additionalProperties": False,
        }

    def _build_system_prompt_do(self) -> str:
        catalog_text = self.catalog._render_catalog_text(for_action="do")
        return (
            "You are a mobile test execution engine. "
            "Your task is to select a single valid action and a locator, "
            "strictly adhering to the JSON output schema. "
            "No step-by-step reasoning, only the JSON response.\n\n"
            f"{catalog_text}\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "- ALWAYS PRIORITIZE the 'xpath' strategy when it is available in the UI context\n"
            "- Use 'xpath' for precise and reliable localization\n"
            "- Avoid generic 'class_name' like 'button' that finds nothing\n"
            "- Choose the first element that matches the instruction\n\n"
            "Constraints: one action only, no multiple attempts. "
            "If the screen does not allow the requested action, choose the best locator according to the UI context."
        )

    def _build_system_prompt_check(self) -> str:
        catalog_text = self.catalog._render_catalog_text(for_action="check")
        return (
            "You are a mobile test verification engine. "
            "Your task is to select a single valid assertion and a locator, "
            "strictly adhering to the JSON output schema. "
            "No step-by-step reasoning, only the JSON response.\n\n"
            f"{catalog_text}\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "- ALWAYS PRIORITIZE the 'xpath' strategy when it is available in the UI context\n"
            "- Use 'xpath' for precise and reliable localization\n"
            "- Avoid generic strategies that find nothing\n"
            "- Choose the first element that matches the instruction\n\n"
            "Constraints: one assertion only. "
            "If the information is uncertain, choose the most precise assertion possible."
        )

    def _build_user_prompt_do(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        ui_text = self._render_ui_candidates(ui_elements)
        schema = self._get_do_output_schema()
        text_parts: List[str] = [
            f"Instruction: {instruction}",
            "Contexte UI (top éléments):",
            ui_text,
            "Répondez en JSON strict (une ligne), schéma:",
            str(schema),
        ]
        content: List[Dict[str, Any]] = [{"type": "text", "text": "\n\n".join(text_parts)}]
        if image_url:
            content.append({"type": "image_url", "image_url": {"url": image_url}})
        return {"role": "user", "content": content}

    def _build_user_prompt_check(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        ui_text = self._render_ui_candidates(ui_elements)
        schema = self._get_check_output_schema()
        text_parts: List[str] = [
            f"Instruction: {instruction}",
            "Contexte UI (top éléments):",
            ui_text,
            "Répondez en JSON strict (une ligne), schéma:",
            str(schema),
        ]
        content: List[Dict[str, Any]] = [{"type": "text", "text": "\n\n".join(text_parts)}]
        if image_url:
            content.append({"type": "image_url", "image_url": {"url": image_url}})
        return {"role": "user", "content": content}

    def _compose_do_messages(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        system_message = {"role": "system", "content": self._build_system_prompt_do()}
        user_message = self._build_user_prompt_do(instruction, ui_elements, image_url)
        self.logger.info("Composed DO prompt with keyword catalog and schema")
        return [system_message, user_message]

    def _compose_check_messages(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        system_message = {"role": "system", "content": self._build_system_prompt_check()}
        user_message = self._build_user_prompt_check(instruction, ui_elements, image_url)
        self.logger.info("Composed CHECK prompt with keyword catalog and schema")
        return [system_message, user_message]





class AgentKeywordCatalog:
    """
    Provides a curated list of allowed high-level agent actions mapped to
    Robot Framework AppiumLibrary keywords. This catalog is embedded into the
    LLM prompt so the model deterministically picks one.
    """

    def __init__(self) -> None:
        self.logger = RobotCustomLogger()
        self._platform = DeviceConnector()

    def _get_locator_strategies(self) -> List[str]:
        return self._platform.get_locator_strategies()

    def _get_do_keywords(self) -> List[Dict[str, Any]]:
        return [
            {
                "action": "open",
                "rf_keyword": "Open Application",
                "requires_locator": False,
                "arguments": [
                    {"name": "remote_url", "required": False},
                ],
                "description": "Open the application session (use test caps).",
            },

            {
                "action": "tap",
                "rf_keyword": "Click Element",
                "requires_locator": True,
                "arguments": [
                    {"name": "locator", "required": True},
                ],
                "description": "Tap a single element identified by a locator.",
            },

            {
                "action": "type",
                "rf_keyword": "Input Text",
                "requires_locator": True,
                "arguments": [
                    {"name": "locator", "required": True},
                    {"name": "text", "required": True},
                ],
                "description": "Type text into a focused input element.",
            },
            {
                "action": "clear",
                "rf_keyword": "Clear Text",
                "requires_locator": True,
                "arguments": [
                    {"name": "locator", "required": True},
                ],
                "description": "Clear the text from an input element.",
            },
            {
                "action": "swipe",
                "rf_keyword": "Swipe By Percent",
                "requires_locator": False,
                "arguments": [
                    {"name": "start_x_pct", "required": True},
                    {"name": "start_y_pct", "required": True},
                    {"name": "end_x_pct", "required": True},
                    {"name": "end_y_pct", "required": True},
                    {"name": "duration", "required": False},
                ],
                "description": "Swipe by screen percentages.",
            },
        ]

    def _get_check_keywords(self) -> List[Dict[str, Any]]:
        return [
            {
                "assertion": "visible",
                "rf_keyword": "Page Should Contain Element",
                "requires_locator": True,
                "arguments": [
                    {"name": "locator", "required": True},
                ],
                "description": "Assert element is present/visible on screen.",
            },
            {
                "assertion": "exists",
                "rf_keyword": "Page Should Contain Element",
                "requires_locator": True,
                "arguments": [
                    {"name": "locator", "required": True},
                ],
                "description": "Alias of visible for presence check.",
            },
            {
                "assertion": "text_contains",
                "rf_keyword": "Element Should Contain Text",
                "requires_locator": True,
                "arguments": [
                    {"name": "locator", "required": True},
                    {"name": "expected", "required": True},
                ],
                "description": "Assert element text contains expected substring.",
            },

            {
                "assertion": "page_text_contains",
                "rf_keyword": "Page Should Contain Text",
                "requires_locator": False,
                "arguments": [
                    {"name": "expected", "required": True},
                ],
                "description": "Le contenu de la page contient le texte attendu.",
            },
            {
                "assertion": "enabled",
                "rf_keyword": "Element Should Be Enabled",
                "requires_locator": True,
                "arguments": [
                    {"name": "locator", "required": True},
                ],
                "description": "L'élément est activé.",
            },
            {
                "assertion": "disabled",
                "rf_keyword": "Element Should Be Disabled",
                "requires_locator": True,
                "arguments": [
                    {"name": "locator", "required": True},
                ],
                "description": "L'élément est désactivé.",
            },
        ]


    def _render_catalog_text(self, for_action: str = "do") -> str:
        if for_action == "do":
            items = self._get_do_keywords()
            header = "Actions autorisées (mapping vers AppiumLibrary):"
            key = "action"
        else:
            items = self._get_check_keywords()
            header = "Assertions autorisées (mapping vers AppiumLibrary):"
            key = "assertion"

        lines: List[str] = [header]
        for item in items:
            human = item.get(key)
            rf = item.get("rf_keyword")
            desc = item.get("description")
            lines.append(f"- {human} → {rf}: {desc}")
        strategies = ", ".join(self._get_locator_strategies())
        lines.append(f"Stratégies de locator permises: {strategies}")
        return "\n".join(lines)
