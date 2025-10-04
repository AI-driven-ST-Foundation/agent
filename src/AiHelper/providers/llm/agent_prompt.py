from typing import List, Dict, Optional, Any

from src.AiHelper.common._logger import RobotCustomLogger


class AgentKeywordCatalog:
    """
    Provides a curated list of allowed high-level agent actions mapped to
    Robot Framework AppiumLibrary keywords. This catalog is embedded into the
    LLM prompt so the model deterministically picks one.
    """

    def __init__(self) -> None:
        self.logger = RobotCustomLogger()

    def get_locator_strategies(self) -> List[str]:
        return [
            "id",
            "accessibility_id",
            "xpath",
            "class_name",
            "android_uiautomator",
            "ios_predicate",
        ]

    def get_do_keywords(self) -> List[Dict[str, Any]]:
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

    def get_check_keywords(self) -> List[Dict[str, Any]]:
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
        ]

    def render_catalog_text(self, for_action: str = "do") -> str:
        if for_action == "do":
            items = self.get_do_keywords()
            header = "Actions autorisées (mapping vers AppiumLibrary):"
            key = "action"
        else:
            items = self.get_check_keywords()
            header = "Assertions autorisées (mapping vers AppiumLibrary):"
            key = "assertion"

        lines: List[str] = [header]
        for item in items:
            human = item.get(key)
            rf = item.get("rf_keyword")
            desc = item.get("description")
            lines.append(f"- {human} → {rf}: {desc}")
        strategies = ", ".join(self.get_locator_strategies())
        lines.append(f"Stratégies de locator permises: {strategies}")
        return "\n".join(lines)


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

    def get_do_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["action", "locator"],
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [k["action"] for k in self.catalog.get_do_keywords()],
                },
                "locator": {
                    "type": "object",
                    "required": ["strategy", "value"],
                    "properties": {
                        "strategy": {
                            "type": "string",
                            "enum": self.catalog.get_locator_strategies(),
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

    def get_check_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["assertion", "locator"],
            "properties": {
                "assertion": {
                    "type": "string",
                    "enum": [k["assertion"] for k in self.catalog.get_check_keywords()],
                },
                "locator": {
                    "type": "object",
                    "required": ["strategy", "value"],
                    "properties": {
                        "strategy": {
                            "type": "string",
                            "enum": self.catalog.get_locator_strategies(),
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

    def build_system_prompt_do(self) -> str:
        catalog_text = self.catalog.render_catalog_text(for_action="do")
        return (
            "Vous êtes un moteur d'exécution de tests mobiles. "
            "Votre tâche est de sélectionner une seule action valide et un locator, "
            "en respectant strictement le schéma JSON de sortie. "
            "Aucun raisonnement étape-par-étape, seulement la réponse JSON.\n\n"
            f"{catalog_text}\n\n"
            "INSTRUCTIONS CRITIQUES:\n"
            "- PRIORISEZ TOUJOURS la stratégie 'xpath' quand elle est disponible dans le contexte UI\n"
            "- Utilisez 'xpath' pour une localisation précise et fiable\n"
            "- Évitez 'class_name' générique comme 'button' qui ne trouve rien\n"
            "- Choisissez le premier élément qui correspond à l'instruction\n\n"
            "Contraintes: une seule action, pas de tentative multiple. "
            "Si l'écran ne permet pas l'action demandée, choisissez le meilleur locator selon le contexte UI."
        )

    def build_system_prompt_check(self) -> str:
        catalog_text = self.catalog.render_catalog_text(for_action="check")
        return (
            "Vous êtes un moteur de vérification de tests mobiles. "
            "Votre tâche est de sélectionner une seule assertion valide et un locator, "
            "en respectant strictement le schéma JSON de sortie. "
            "Aucun raisonnement étape-par-étape, seulement la réponse JSON.\n\n"
            f"{catalog_text}\n\n"
            "INSTRUCTIONS CRITIQUES:\n"
            "- PRIORISEZ TOUJOURS la stratégie 'xpath' quand elle est disponible dans le contexte UI\n"
            "- Utilisez 'xpath' pour une localisation précise et fiable\n"
            "- Évitez les stratégies génériques qui ne trouvent rien\n"
            "- Choisissez le premier élément qui correspond à l'instruction\n\n"
            "Contraintes: une seule assertion. "
            "Si l'information n'est pas certaine, choisissez l'assertion la plus précise possible."
        )

    def build_user_prompt_do(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        ui_text = self._render_ui_candidates(ui_elements)
        schema = self.get_do_output_schema()
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

    def build_user_prompt_check(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        ui_text = self._render_ui_candidates(ui_elements)
        schema = self.get_check_output_schema()
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

    def compose_do_messages(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        system_message = {"role": "system", "content": self.build_system_prompt_do()}
        user_message = self.build_user_prompt_do(instruction, ui_elements, image_url)
        self.logger.info("Composed DO prompt with keyword catalog and schema")
        return [system_message, user_message]

    def compose_check_messages(
        self,
        instruction: str,
        ui_elements: Optional[List[Dict[str, Any]]] = None,
        image_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        system_message = {"role": "system", "content": self.build_system_prompt_check()}
        user_message = self.build_user_prompt_check(instruction, ui_elements, image_url)
        self.logger.info("Composed CHECK prompt with keyword catalog and schema")
        return [system_message, user_message]


