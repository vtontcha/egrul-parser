# main.py
"""
Точка входа парсера ЕГРЮЛ через api-fns.ru.

Запуск:
    python main.py
"""

from parser import collect_cards
from exporter import save_to_json
from config import PAGES_TO_PARSE, SEARCH_QUERY


def main():
    print(f"Запуск сбора данных:")
    print(f"  Запрос:  {SEARCH_QUERY}")
    print(f"  Страниц: {PAGES_TO_PARSE}")
    print()

    cards = collect_cards(SEARCH_QUERY, PAGES_TO_PARSE)

    if cards:
        filepath = save_to_json(cards)
        print(f"\n✅ Готово! Сохранено {len(cards)} карточек:\n   {filepath}")
    else:
        print("\n⚠ Карточки не собраны. Проверьте API-ключ и SEARCH_QUERY в config.py.")


if __name__ == "__main__":
    main()