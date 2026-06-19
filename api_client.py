# api_client.py
"""
Клиент для api-fns.ru.

Один метод:
  search_page(query, page) — возвращает список компаний со страницы поиска.
  Все нужные поля уже содержатся в ответе метода search,
  поэтому дополнительный запрос egr по каждому ИНН не нужен.
"""

import os
import time
import httpx
from dotenv import load_dotenv
from config import HTTP_TIMEOUT, RETRY_COUNT, RETRY_DELAY, REQUEST_DELAY

load_dotenv()

API_KEY = os.getenv("API_FNS_KEY", "")
BASE_URL = "https://api-fns.ru/api"


def _get(endpoint: str, params: dict) -> dict | None:
    """
    Выполняет GET-запрос к api-fns.ru с повторными попытками.

    Args:
        endpoint: путь метода, например "search"
        params:   параметры запроса (без key — добавляется автоматически)

    Returns:
        Распарсенный JSON-ответ или None при ошибке.
    """
    params["key"] = API_KEY
    url = f"{BASE_URL}/{endpoint}"

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            with httpx.Client(timeout=HTTP_TIMEOUT) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            print(f"  [HTTP ошибка] {e.response.status_code} — {url}")
            if 400 <= e.response.status_code < 500:
                return None

        except httpx.TimeoutException:
            print(f"  [Таймаут] попытка {attempt}/{RETRY_COUNT}")

        except httpx.RequestError as e:
            print(f"  [Ошибка соединения] попытка {attempt}/{RETRY_COUNT}: {e}")

        if attempt < RETRY_COUNT:
            print(f"  Повтор через {RETRY_DELAY} сек...")
            time.sleep(RETRY_DELAY)

    print(f"  [Отказ] все {RETRY_COUNT} попытки исчерпаны — {endpoint}")
    return None


def search_page(query: str, page: int) -> list[dict]:
    """
    Возвращает список компаний со страницы поиска.

    Args:
        query: поисковая строка (например "ООО" или "Газпром")
        page:  номер страницы (начиная с 1)

    Returns:
        Список сырых словарей компаний из поля items.
    """
    time.sleep(REQUEST_DELAY)
    data = _get("search", {"q": query, "page": page})
    if data is None:
        return []
    return data.get("items") or []