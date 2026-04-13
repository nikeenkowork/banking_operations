import json
import logging
from datetime import datetime
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)


# =========================
# 🔹 ОБЩИЕ ФУНКЦИИ
# =========================

def parse_datetime(date_str):
    """
    Парсит строку с датой и временем в объект datetime.

    Args:
        date_str (str): дата и время в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
        datetime | None: объект datetime или None при ошибке формата
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logging.error("Неверный формат даты")
        return None


def make_json(data):
    """
    Преобразует Python-объект в JSON-строку.

    Args:
        data (Any): любые сериализуемые данные (dict, list и т.д.)

    Returns:
        str: JSON-строка с форматированием
    """
    return json.dumps(data, ensure_ascii=False, indent=4)


def get_external_api():
    """
    Получает данные из внешнего API (курсы валют).

    Returns:
        dict: ответ API или пустой словарь при ошибке
    """
    try:
        response = requests.get("https://api.exchangerate.host/latest")
        return response.json()
    except Exception as e:
        logging.error(f"API error: {e}")
        return {}


# =========================
# 🔹 ГЛАВНАЯ (Excel анализ)
# =========================

def analyze_operations():
    """
    Анализирует Excel-файл operations.xlsx.

    Читает файл и возвращает:
    - количество строк
    - список колонок
    - данные в виде списка словарей

    Returns:
        dict: структура с данными Excel
    """
    try:
        df = pd.read_excel("operations.xlsx")

        return {
            "rows_count": len(df),
            "columns": list(df.columns),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        logging.error(f"Excel error: {e}")
        return {}


def build_main_response(date_str):
    """
    Формирует ответ для главной страницы.

    Выполняет:
    - парсинг даты
    - анализ Excel операций
    - запрос к внешнему API

    Args:
        date_str (str): дата и время пользователя
            формат: YYYY-MM-DD HH:MM:SS

    Returns:
        dict: итоговый JSON-объект ответа
    """
    dt = parse_datetime(date_str)

    result = {
        "input_date": date_str,
        "year": dt.year if dt else None,
        "month": dt.month if dt else None,
        "operations": analyze_operations(),
        "api": get_external_api()
    }

    return make_json(result)


# =========================
# 🔹 СОБЫТИЯ (DataFrame)
# =========================

def process_events(df: pd.DataFrame):
    """
    Обрабатывает события из DataFrame.

    Считает:
    - общее количество событий
    - дату последнего события
    - добавляет данные из внешнего API

    Args:
        df (pd.DataFrame): таблица событий
            ожидается колонка 'date' (опционально)

    Returns:
        str: JSON-строка с результатом обработки
    """
    try:
        total_events = len(df)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            latest = df["date"].max()
        else:
            latest = None

        result = {
            "total_events": total_events,
            "latest_event": str(latest),
            "api": get_external_api()
        }

        return make_json(result)

    except Exception as e:
        logging.error(f"Events error: {e}")
        return make_json({"error": str(e)})