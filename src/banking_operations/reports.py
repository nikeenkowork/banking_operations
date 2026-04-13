import json
import logging
from datetime import datetime, timedelta
import pandas as pd

logging.basicConfig(level=logging.INFO)


# =========================
# 1. Траты по категории (за 3 месяца)
# =========================
def spending_by_category(df: pd.DataFrame, category: str, date_to: str) -> str:
    """
    Отчёт: траты по заданной категории за период последних 3 месяцев.

    Функция фильтрует транзакции по категории и временному диапазону,
    рассчитывает сумму расходов и возвращает результат в формате JSON.

    Args:
        df (pd.DataFrame): DataFrame с транзакциями
            Ожидаемые колонки: date, category, amount
        category (str): категория расходов для фильтрации
        date_to (str): дата окончания периода в формате YYYY-MM-DD

    Returns:
        str: JSON-строка с результатом отчёта
    """
    try:
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
        date_from = date_to_dt - timedelta(days=90)

        df["date"] = pd.to_datetime(df["date"])

        filtered = df[
            (df["category"] == category) &
            (df["date"] >= date_from) &
            (df["date"] <= date_to_dt)
        ]

        total = float(filtered["amount"].sum())

        result = {
            "category": category,
            "date_from": date_from.date().isoformat(),
            "date_to": date_to_dt.date().isoformat(),
            "total_spent": round(total, 2)
        }

        logging.info("Report by category OK")

        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.exception("Error in spending_by_category")

        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False, indent=4)


# =========================
# 2. Траты по дням недели
# =========================
def spending_by_weekday(df: pd.DataFrame, date_to: str = None) -> str:
    """
    Отчёт: распределение расходов по дням недели.

    Функция группирует транзакции по дням недели и считает сумму расходов
    для каждого дня.

    Args:
        df (pd.DataFrame): DataFrame с транзакциями
            Ожидаемые колонки: date, amount
        date_to (str, optional): дата отсечения данных (YYYY-MM-DD).
            Если не указана, используются все данные.

    Returns:
        str: JSON-строка с суммами по дням недели
    """
    try:
        df["date"] = pd.to_datetime(df["date"])

        if date_to:
            date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
            df = df[df["date"] <= date_to_dt]

        df["weekday"] = df["date"].dt.day_name()

        grouped = df.groupby("weekday")["amount"].sum()

        result = grouped.to_dict()

        logging.info("Report by weekday OK")

        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.exception("Error in spending_by_weekday")

        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False, indent=4)


# =========================
# 3. Траты рабочие / выходные дни
# =========================
def spending_weekday_vs_weekend(df: pd.DataFrame, date_to: str) -> str:
    """
    Отчёт: сравнение расходов в рабочие и выходные дни.

    Функция разделяет транзакции на будние и выходные дни
    и считает общую сумму расходов в каждой группе.

    Args:
        df (pd.DataFrame): DataFrame с транзакциями
            Ожидаемые колонки: date, amount
        date_to (str): дата окончания периода в формате YYYY-MM-DD

    Returns:
        str: JSON-строка с суммами расходов по типу дня
            (рабочие / выходные)
    """
    try:
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
        date_from = date_to_dt - timedelta(days=90)

        df["date"] = pd.to_datetime(df["date"])

        df = df[(df["date"] >= date_from) & (df["date"] <= date_to_dt)]

        df["is_weekend"] = df["date"].dt.weekday >= 5

        weekday_total = float(df[df["is_weekend"] == False]["amount"].sum())
        weekend_total = float(df[df["is_weekend"] == True]["amount"].sum())

        result = {
            "date_from": date_from.date().isoformat(),
            "date_to": date_to_dt.date().isoformat(),
            "weekday_total": round(weekday_total, 2),
            "weekend_total": round(weekend_total, 2)
        }

        logging.info("Report weekday vs weekend OK")

        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.exception("Error in spending_weekday_vs_weekend")

        return json.dumps({
            "status": "error",
            "message": str(e)
        }, ensure_ascii=False, indent=4)
