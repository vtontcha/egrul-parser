# exporter.py
"""
Сохраняет собранные карточки компаний в JSON-файл.
"""

import json
import os
from datetime import datetime


def save_to_json(cards: list[dict], output_dir: str = "output") -> str:
    """
    Сохраняет список карточек в JSON-файл.

    Args:
        cards:      список словарей-карточек организаций
        output_dir: папка для сохранения (будет создана при отсутствии)

    Returns:
        Путь к созданному файлу.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"companies_{timestamp}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

    return filepath