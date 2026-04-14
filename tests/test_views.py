from unittest.mock import patch

import pandas as pd

from banking_operations.views import events_page, main_page

# =========================
# 🧪 main_page
# =========================


@patch("banking_operations.views.build_main_response")
def test_main_page_success(mock_build):
    """
    Проверяет, что main_page корректно вызывает build_main_response
    и возвращает результат без изменений.

    Тест:
    - подменяет build_main_response через mock
    - проверяет вызов с правильным аргументом
    - проверяет возврат значения
    """
    mock_build.return_value = '{"status": "ok"}'

    result = main_page("2025-01-01 12:00:00")

    mock_build.assert_called_once_with("2025-01-01 12:00:00")
    assert result == '{"status": "ok"}'


# =========================
# 🧪 main_page (ошибка)
# =========================


@patch("banking_operations.views.build_main_response")
def test_main_page_handles_invalid_date(mock_build):
    """
    Проверяет поведение main_page при некорректной дате.

    Тест:
    - имитирует ответ функции build_main_response
    - проверяет, что функция всё равно возвращает результат
    """
    mock_build.return_value = '{"error": "invalid date"}'

    result = main_page("wrong-date")

    mock_build.assert_called_once_with("wrong-date")
    assert "error" in result


# =========================
# 🧪 events_page
# =========================


@patch("banking_operations.views.process_events")
def test_events_page_success(mock_process):
    """
    Проверяет, что events_page корректно вызывает process_events
    и возвращает результат.

    Тест:
    - подменяет process_events
    - проверяет передачу DataFrame
    - проверяет возврат результата
    """
    df = pd.DataFrame([{"date": "2025-01-01"}, {"date": "2025-01-02"}])

    mock_process.return_value = '{"events": 2}'

    result = events_page(df)

    mock_process.assert_called_once_with(df)
    assert result == '{"events": 2}'


# =========================
# 🧪 events_page (пустой DataFrame)
# =========================


@patch("banking_operations.views.process_events")
def test_events_page_empty_df(mock_process):
    """
    Проверяет обработку пустого DataFrame.

    Тест:
    - передаёт пустой DataFrame
    - проверяет, что функция всё равно вызывает process_events
    """
    df = pd.DataFrame()

    mock_process.return_value = '{"events": 0}'

    result = events_page(df)

    mock_process.assert_called_once_with(df)
    assert "0" in result
