import json
from unittest.mock import patch

import pandas as pd
import pytest

from banking_operations import reports as m


# =========================
# FIXTURE
# =========================
@pytest.fixture
def df():
    """
    Фиктивные транзакции для тестов
    """
    return pd.DataFrame(
        [
            {"date": "2026-01-10", "category": "food", "amount": 100},
            {"date": "2026-01-15", "category": "food", "amount": 200},
            {"date": "2026-01-20", "category": "shop", "amount": 300},
            {"date": "2026-01-21", "category": "food", "amount": 50},
        ]
    )


# =========================
# 1. CATEGORY
# =========================
def test_spending_by_category(df):
    """
    Проверка расчёта трат по категории
    """
    result = m.spending_by_category(df, "food", "2026-01-31")
    data = json.loads(result)

    assert data["category"] == "food"
    assert data["total_spent"] == 350.0


# =========================
# 2. WEEKDAY
# =========================
def test_spending_by_weekday(df):
    """
    Проверка группировки по дням недели
    """
    result = m.spending_by_weekday(df)
    data = json.loads(result)

    assert isinstance(data, dict)
    assert len(data) > 0


# =========================
# 3. WEEKDAY VS WEEKEND
# =========================
def test_weekday_vs_weekend(df):
    """
    Проверка разделения будни/выходные
    """
    result = m.spending_weekday_vs_weekend(df, "2026-01-31")
    data = json.loads(result)

    assert "weekday_total" in data
    assert "weekend_total" in data


# =========================
# 4. PATCH DATETIME
# =========================
@patch("banking_operations.reports.datetime")
def test_patch_datetime(mock_datetime, df):
    """
    Проверка функции с patch datetime
    """
    import datetime as real_datetime

    mock_datetime.strptime.side_effect = real_datetime.datetime.strptime
    mock_datetime.timedelta = real_datetime.timedelta

    result = m.spending_by_category(df, "food", "2026-01-31")
    data = json.loads(result)

    assert data["category"] == "food"


# =========================
# 5. ERROR CASE
# =========================
def test_error_case():
    """
    Проверка обработки ошибки
    """
    result = m.spending_by_category(None, "food", "2026-01-31")  # type: ignore
    data = json.loads(result)

    assert data["status"] == "error"
    assert "message" in data
