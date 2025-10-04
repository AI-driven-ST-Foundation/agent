from typing import Any, Dict, List

import xml.etree.ElementTree as ET

from src.AiHelper.common._logger import RobotCustomLogger


class UiParser:
    """Parse le XML UI pour extraire des éléments interactifs et générer des xpaths."""

    def __init__(self) -> None:
        self.logger = RobotCustomLogger()

    def parse(self, xml_content: str, max_items: int = 20) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = []
        try:
            root = ET.fromstring(xml_content)

            def walk(node, depth: int = 0, max_depth: int = 12):
                if depth > max_depth:
                    return

                attrs = {
                    'text': node.get('text', ''),
                    'resource_id': node.get('resource-id', ''),
                    'class_name': node.get('class', ''),
                    'content_desc': node.get('content-desc', ''),
                    'package': node.get('package', ''),
                    'clickable': node.get('clickable', 'false').lower() == 'true',
                    'enabled': node.get('enabled', 'false').lower() == 'true',
                    'bounds': node.get('bounds', ''),
                    'index': node.get('index', ''),
                }

                if attrs['clickable'] and attrs['enabled']:
                    # Ne pas construire d'xpath ici. L'IA décidera de la stratégie/valeur.
                    candidates.append({**attrs})

                for child in list(node):
                    walk(child, depth + 1, max_depth)

            walk(root)

            def sort_key(item: Dict[str, Any]) -> int:
                score = 0
                if item.get('text'): score += 3
                if item.get('content_desc'): score += 2
                if item.get('resource_id'): score += 1
                return score

            candidates.sort(key=sort_key, reverse=True)
            return candidates[:max_items]
        except ET.ParseError as e:
            self.logger.warning(f"⚠️ Erreur parsing XML: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du parsing UI: {e}")
            return []

    # Intentionnellement pas d'utilitaire xpath: l'IA doit décider seule.



