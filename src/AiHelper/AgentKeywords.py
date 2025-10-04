from typing import Any, Dict, List, Optional

from src.AiHelper.common._agentengine import AgentEngine
from src.AiHelper.common._logger import RobotCustomLogger


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
        self.engine = AgentEngine(llm_client=llm_client, llm_model=llm_model)

    # ----------------------- Public RF Keywords -----------------------
    def agent_do(self, instruction: str):
        """Agent.Do <instruction>
        Example: Agent.Do    accepte les cookies
        """
        self.engine.do(instruction)

    def agent_check(self, instruction: str):
        """Agent.Check <instruction>
        Example: Agent.Check    l'écran affiche bien la carte
        """
        self.engine.check(instruction)


