from abc import ABC, abstractmethod
from typing import Any, Dict, List


class UiPlatformAdapter(ABC):
    """Abstract adapter for UI platform specifics (Appium, Web, etc.).

    Responsibilities:
      - Acquire current UI structure/context
      - Extract UI candidate elements from context
      - Convert model-proposed locator objects to Robot Framework locators
      - Expose supported locator strategies for prompting/schema (future)
    """

    @abstractmethod
    def get_ui_xml(self) -> str:
        """Return a string representation of the current UI (XML/HTML)."""
        raise NotImplementedError

    @abstractmethod
    def parse_ui(self, ui_xml: str, max_items: int = 20) -> List[Dict[str, Any]]:
        """Extract candidate elements from the UI context."""
        raise NotImplementedError

    @abstractmethod
    def to_rf_locator(self, locator: Dict[str, Any]) -> str:
        """Convert a locator dict {strategy, value} to an RF-compatible locator string."""
        raise NotImplementedError

    def get_locator_strategies(self) -> List[str]:
        """Return supported strategies. Implement as needed per platform."""
        return []


