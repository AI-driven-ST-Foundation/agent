from typing import Any

from robot.api import logger as rf_logger
from robot.libraries.BuiltIn import BuiltIn

from src.AiHelper.common._logger import RobotCustomLogger

class RobotKeywordExecutor:
    """Centralise l'exécution des keywords Robot Framework via BuiltIn.run_keyword
    avec un logging structuré côté Robot et côté logger fichier.
    """

    def __init__(self) -> None:
        self.logger = RobotCustomLogger()

    def run(self, keyword_name: str, *args: Any) -> Any:
        """Exécute un keyword Robot Framework avec des arguments positionnels.

        - Log côté Robot: EXECUTING / SUCCESS / FAILED
        - Log fichier via RobotCustomLogger
        """
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


