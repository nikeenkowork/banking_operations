import json
import logging
import math
import re
from datetime import datetime
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)


# =========================
# Сервис: Выгодные категории кешбэка
# =========================


def find_cashback_categories(
    year: int, month: int, transactions: List[Dict[str, Any]]
) -> str:
    """
    Формирует отчёт по кешбэку (расходам по категориям) за указанный месяц и год.

    Функция:
    - фильтрует транзакции по дате
    - группирует расходы по категориям
    - сортирует категории по убыванию суммы

    Args:
        year (int): год отчёта
        month (int): месяц отчёта (1-12)
        transactions (list[dict]): список транзакций,
            каждая содержит date, category, amount

    Returns:
        str: JSON-строка с категориями и суммами расходов
    """
    try:
        result: Dict[str, float] = {}

        for transaction in transactions:
            try:
                date_obj = datetime.strptime(transaction["date"], "%Y-%m-%d")
            except (KeyError, ValueError):
                logging.error(f"Некорректная дата: {transaction}")
                continue

            if date_obj.year != year or date_obj.month != month:
                continue

            category = transaction.get("category", "unknown")

            try:
                amount = float(transaction.get("amount", 0))
            except (TypeError, ValueError):
                logging.error(f"Некорректная сумма: {transaction}")
                continue

            result[category] = result.get(category, 0) + amount

        sorted_categories = sorted(result.items(), key=lambda x: x[1], reverse=True)

        response = {
            "year": year,
            "month": month,
            "categories": [
                {"category": c, "total_spent": t} for c, t in sorted_categories
            ],
        }

        logging.info("Cashback OK")
        return json.dumps(response, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.exception("Cashback error")
        return json.dumps({"status": "error", "message": str(e)})


# =========================
# Сервис: Инвесткопилка
# =========================


def investment_piggy_bank(
    month: int, transactions: List[Dict[str, Any]], round_limit: int
) -> str:
    """
    Сервис накоплений (инвесткопилка).

    Функция:
    - берёт расходы за месяц
    - округляет их вверх до заданного лимита
    - считает сумму "сэкономленных" денег

    Args:
        month (int): месяц расчёта
        transactions (list[dict]): список транзакций
        round_limit (int): шаг округления

    Returns:
        str: JSON-строка с результатами накоплений
    """
    try:
        total_saved = 0.0
        detailed = []

        for t in transactions:
            try:
                date_obj = datetime.strptime(t["date"], "%Y-%m-%d")
            except (KeyError, ValueError):
                logging.error(f"Bad date: {t}")
                continue

            if date_obj.month != month:
                continue

            try:
                amount = float(t.get("amount", 0))
            except (TypeError, ValueError):
                logging.error(f"Bad amount: {t}")
                continue

            if amount < 0:
                amount = abs(amount)

                rounded = math.ceil(amount / round_limit) * round_limit
                saved = rounded - amount

                total_saved += saved

                detailed.append(
                    {
                        "date": t["date"],
                        "expense": amount,
                        "rounded": rounded,
                        "saved": saved,
                    }
                )

        response = {
            "month": month,
            "round_limit": round_limit,
            "total_saved": round(total_saved, 2),
            "details": detailed,
        }

        logging.info("Piggy OK")
        return json.dumps(response, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.exception("Piggy error")
        return json.dumps({"status": "error", "message": str(e)})


# =========================
# Сервис: Простой поиск
# =========================


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> str:
    """
    Простой текстовый поиск по транзакциям.

    Ищет совпадения запроса в:
    - дате
    - категории
    - сумме

    Args:
        query (str): поисковый запрос
        transactions (list[dict]): список транзакций

    Returns:
        str: JSON-строка с найденными транзакциями
    """
    try:
        query_lower = query.lower()
        results = []

        for t in transactions:
            text = " ".join(
                [
                    str(t.get("date", "")),
                    str(t.get("category", "")),
                    str(t.get("amount", "")),
                ]
            ).lower()

            if query_lower in text:
                results.append(t)

        response = {"query": query, "count": len(results), "results": results}

        logging.info("Simple search OK")
        return json.dumps(response, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.exception("Simple search error")
        return json.dumps({"status": "error", "message": str(e)})


# =========================
# Сервис: Поиск по телефонным номерам
# =========================


def phone_search(transactions: List[Dict[str, Any]]) -> str:
    """
    Поиск телефонных номеров в транзакциях.

    Поддерживаемые форматы:
    - +79991234567
    - 89991234567
    - +7 999 123 45 67
    - 8-999-123-45-67

    Args:
        transactions (list[dict]): список транзакций

    Returns:
        str: JSON с найденными номерами
    """
    try:
        phone_pattern = re.compile(
            r"(\+7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"
        )

        results = []

        for t in transactions:
            text = str(t)

            matches = phone_pattern.findall(text)

            if matches:
                results.append({"transaction": t, "phones": matches})

        response = {"count": len(results), "results": results}

        logging.info("Phone search OK")
        return json.dumps(response, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.exception("Phone search error")
        return json.dumps({"status": "error", "message": str(e)})


# =========================
# Сервис: Переводы физлицам
# =========================


def find_transfers_to_individuals(transactions):
    """
    Поиск переводов физическим лицам.

    Функция ищет транзакции, содержащие:
    - слова "перевод" или "payment"
    - имя и фамилию (регулярное выражение)

    Args:
        transactions (list[dict]): список транзакций

    Returns:
        str: JSON с найденными переводами физлицам
    """
    try:
        result = []

        for tx in transactions:
            description = tx.get("description", "")

            if re.search(
                r"(перевод|payment).*(\b[А-ЯA-Z][а-яa-z]+\s[А-ЯA-Z][а-яa-z]+)",
                description,
                re.IGNORECASE,
            ):
                result.append(tx)

        response = {"status": "success", "count": len(result), "data": result}

        return json.dumps(response, ensure_ascii=False, indent=4)

    except Exception as e:
        logging.error(f"Search error: {e}")

        return json.dumps(
            {"status": "error", "message": str(e)}, ensure_ascii=False, indent=4
        )
