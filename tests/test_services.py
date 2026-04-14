import json
from unittest.mock import patch

import banking_operations.services as svc


# =========================
# Cashback
# =========================
def test_find_cashback_categories_basic():
    """
    Проверяет корректный расчёт сумм по категориям
    за указанный месяц и год.
    """
    transactions = [
        {"date": "2025-01-10", "category": "food", "amount": 100},
        {"date": "2025-01-15", "category": "food", "amount": 200},
        {"date": "2025-01-20", "category": "taxi", "amount": 50},
        {"date": "2024-01-10", "category": "food", "amount": 999},  # игнор
    ]

    result = svc.find_cashback_categories(2025, 1, transactions)
    data = json.loads(result)

    assert data["year"] == 2025
    assert data["month"] == 1
    assert data["categories"][0]["category"] == "food"
    assert data["categories"][0]["total_spent"] == 300


def test_find_cashback_categories_logging():
    """
    Проверяет, что при некорректной дате вызывается logging.error.
    """
    transactions = [
        {"date": "BAD_DATE", "category": "food", "amount": 100},
    ]

    with patch("banking_operations.services.logging.error") as mock_log:
        svc.find_cashback_categories(2025, 1, transactions)
        mock_log.assert_called()


# =========================
# Piggy bank
# =========================
def test_investment_piggy_bank_basic():
    """
    Проверяет корректную работу округления расходов
    и подсчёт накопленных средств.
    """
    transactions = [
        {"date": "2025-01-10", "amount": -105},
        {"date": "2025-01-11", "amount": -210},
    ]

    result = svc.investment_piggy_bank(1, transactions, 100)
    data = json.loads(result)

    # 105 → 200 (saved 95)
    # 210 → 300 (saved 90)
    assert data["total_saved"] == 185


def test_investment_piggy_bank_logging():
    """
    Проверяет логирование при ошибке в сумме.
    """
    transactions = [
        {"date": "2025-01-10", "amount": "BAD"},
    ]

    with patch("banking_operations.services.logging.error") as mock_log:
        svc.investment_piggy_bank(1, transactions, 100)
        mock_log.assert_called()


# =========================
# Simple search
# =========================
def test_simple_search_found():
    """
    Проверяет, что поиск возвращает найденные транзакции.
    """
    transactions = [
        {"date": "2025-01-10", "category": "food", "amount": 100},
        {"date": "2025-01-11", "category": "taxi", "amount": 200},
    ]

    result = svc.simple_search("food", transactions)
    data = json.loads(result)

    assert data["count"] == 1
    assert data["results"][0]["category"] == "food"


def test_simple_search_empty():
    """
    Проверяет поведение при отсутствии совпадений.
    """
    result = svc.simple_search("xxx", [])
    data = json.loads(result)

    assert data["count"] == 0


# =========================
# Phone search
# =========================
def test_phone_search_found():
    """
    Проверяет, что номера телефонов находятся корректно.
    """
    transactions = [
        {"info": "Позвонить +79991234567"},
        {"info": "без номера"},
    ]

    result = svc.phone_search(transactions)
    data = json.loads(result)

    assert data["count"] == 1


def test_phone_search_regex_used():
    """
    Проверяет, что используется регулярное выражение (re.compile).
    """
    with patch("banking_operations.services.re.compile") as mock_compile:
        svc.phone_search([])
        mock_compile.assert_called()


# =========================
# Transfers to individuals
# =========================
def test_find_transfers_to_individuals_found():
    """
    Проверяет поиск переводов физическим лицам.
    """
    transactions = [
        {"description": "Перевод Иван Иванов"},
        {"description": "Оплата магазина"},
    ]

    result = svc.find_transfers_to_individuals(transactions)
    data = json.loads(result)

    assert data["count"] == 1
    assert data["status"] == "success"


def test_find_transfers_to_individuals_regex_called():
    """
    Проверяет, что используется re.search через patch.
    """
    with patch("banking_operations.services.re.search") as mock_search:
        mock_search.return_value = True

        svc.find_transfers_to_individuals([{"description": "test"}])

        mock_search.assert_called()
