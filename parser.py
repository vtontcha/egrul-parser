# parser.py
"""
Формирует карточки организаций из ответов метода search api-fns.ru.

Ответ search содержит список items, каждый элемент — словарь с одним ключом:
  'ЮЛ'  — российское юридическое лицо
  'НР'  — иностранное представительство/филиал
  'ИП'  — индивидуальный предприниматель (если встретится)

Внутри каждого — плоский словарь с реквизитами.
КПП в методе search не передаётся — оставляем поле пустым.
"""

from api_client import search_page


def _extract_entity(item: dict) -> dict:
    """
    Извлекает данные организации из элемента списка items.
    Определяет тип записи (ЮЛ / НР / ИП) и возвращает вложенный словарь.
    """
    for key in ("ЮЛ", "НР", "ИП"):
        if key in item:
            return item[key]
    return {}


def build_card(item: dict) -> dict | None:
    """
    Формирует карточку организации из одного элемента ответа search.

    Args:
        item: элемент из списка items ответа API

    Returns:
        Словарь-карточка или None если данных нет.
    """
    data = _extract_entity(item)
    if not data:
        return None

    inn  = str(data.get("ИНН") or data.get("ИННЮЛ") or data.get("ИННФЛ") or "").strip()
    ogrn = str(data.get("ОГРН") or "").strip()

    # Полное название — для ЮЛ это НаимПолнЮЛ, для НР — НаимПолнЮЛ или НаимПредПолн
    full_name = (
        str(data.get("НаимПолнЮЛ") or "")
        or str(data.get("НаимПредПолн") or "")
    ).strip()

    short_name = (
        str(data.get("НаимСокрЮЛ") or "")
        or str(data.get("НаимПредСокр") or "")
    ).strip()

    # Правовая форма — извлекаем из полного названия (первое слово/аббревиатура)
    # В методе search отдельного поля ОПФ нет
    legal_form = _extract_legal_form(full_name)

    # ОКВЭД — в search называется ОснВидДеят
    okved = str(data.get("ОснВидДеят") or "").strip()

    # Адрес
    address = str(data.get("АдресПолн") or "").strip()
    contacts = f"Юридический адрес: {address}" if address else ""

    return {
        "Полное название компании":      full_name,
        "Сокращённое название компании": short_name,
        "Правовая форма":                legal_form,
        "ИНН":                           inn,
        "КПП":                           "",   # недоступно в методе search
        "ОГРН":                          ogrn,
        "ОКВЭД (основной)":              okved,
        "Контакты":                      contacts,
    }


def _extract_legal_form(full_name: str) -> str:
    """
    Пытается извлечь правовую форму из полного названия организации.
    Например: 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ПРИМЕР"' -> 'ООО'
    """
    mapping = {
        "ПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО": "ПАО",
        "НЕПУБЛИЧНОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО": "НАО",
        "АКЦИОНЕРНОЕ ОБЩЕСТВО": "АО",
        "ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ": "ООО",
        "ОБЩЕСТВО С ДОПОЛНИТЕЛЬНОЙ ОТВЕТСТВЕННОСТЬЮ": "ОДО",
        "ОТКРЫТОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО": "ОАО",
        "ЗАКРЫТОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО": "ЗАО",
        "ГОСУДАРСТВЕННОЕ УНИТАРНОЕ ПРЕДПРИЯТИЕ": "ГУП",
        "МУНИЦИПАЛЬНОЕ УНИТАРНОЕ ПРЕДПРИЯТИЕ": "МУП",
        "ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ УНИТАРНОЕ ПРЕДПРИЯТИЕ": "ФГУП",
        "ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ": "ИП",
        "НЕКОММЕРЧЕСКОЕ ПАРТНЕРСТВО": "НП",
        "ТОВАРИЩЕСТВО СОБСТВЕННИКОВ ЖИЛЬЯ": "ТСЖ",
        "ПРОИЗВОДСТВЕННЫЙ КООПЕРАТИВ": "ПК",
        "ПОТРЕБИТЕЛЬСКИЙ КООПЕРАТИВ": "ПК",
        "АВТОНОМНАЯ НЕКОММЕРЧЕСКАЯ ОРГАНИЗАЦИЯ": "АНО",
        "ФОНД": "ФОНД",
    }
    name_upper = full_name.upper()
    for long_form, short_form in mapping.items():
        if long_form in name_upper:
            return short_form
    return ""


def collect_cards(query: str, pages: int) -> list[dict]:
    """
    Собирает карточки компаний с указанного числа страниц поиска.

    Args:
        query: поисковая строка
        pages: число страниц для обхода

    Returns:
        Список карточек организаций.
    """
    cards = []

    for page_num in range(1, pages + 1):
        print(f"\nСтраница {page_num}/{pages}...")
        items = search_page(query, page_num)

        if not items:
            print(f"  Страница {page_num} — нет данных, пропускаем.")
            continue

        print(f"  Получено записей: {len(items)}")

        for item in items:
            card = build_card(item)
            if card is None:
                continue
            cards.append(card)

        print(f"  Итого карточек собрано: {len(cards)}")

    return cards