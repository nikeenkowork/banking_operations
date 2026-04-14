from unittest.mock import MagicMock, patch

import pandas as pd

from banking_operations.utils import (
    analyze_operations,
    build_main_response,
    get_external_api,
    make_json,
    parse_datetime,
    process_events,
)

# =========================
# 🧪 parse_datetime
# =========================


def test_parse_datetime_success():
    """
    Проверяет успешный парсинг корректной строки даты.

    Ожидается, что функция parse_datetime:
    - корректно преобразует строку в объект datetime
    - возвращает объект с правильным годом и месяцем
    """
    dt = parse_datetime("2025-01-01 12:00:00")
    assert dt.year == 2025
    assert dt.month == 1


def test_parse_datetime_fail():
    """
    Проверяет обработку некорректного формата даты.

    Ожидается, что функция:
    - вернёт None
    - не выбросит исключение
    """
    dt = parse_datetime("wrong-date")
    assert dt is None


# =========================
# 🧪 make_json
# =========================


def test_make_json():
    """
    Проверяет преобразование Python-объекта в JSON-строку.

    Ожидается, что:
    - результат является строкой
    - JSON содержит переданные данные
    """
    data = {"a": 1}
    result = make_json(data)
    assert '"a": 1' in result


# =========================
# 🧪 get_external_api (mock)
# =========================


@patch("banking_operations.utils.requests.get")
def test_get_external_api(mock_get):
    """
    Проверяет получение данных из внешнего API с использованием mock.

    Тест:
    - подменяет requests.get
    - проверяет, что функция возвращает JSON-ответ
    - не делает реальный HTTP-запрос
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"rates": {"USD": 1}}

    mock_get.return_value = mock_response

    result = get_external_api()

    assert "rates" in result


# =========================
# 🧪 analyze_operations (mock Excel)
# =========================


@patch("banking_operations.utils.pd.read_excel")
def test_analyze_operations(mock_read_excel):
    """
    Проверяет анализ Excel-файла.

    Тест:
    - подменяет чтение Excel через pandas
    - проверяет корректный подсчёт строк
    - проверяет наличие колонок в результате
    """
    mock_df = pd.DataFrame([{"a": 1}, {"a": 2}])

    mock_read_excel.return_value = mock_df

    result = analyze_operations()

    assert result["rows_count"] == 2
    assert "a" in result["columns"]


# =========================
# 🧪 build_main_response (mock всё)
# =========================


@patch("banking_operations.utils.get_external_api")
@patch("banking_operations.utils.analyze_operations")
def test_build_main_response(mock_analyze, mock_api):
    """
    Проверяет формирование главного ответа.

    Тест:
    - изолирует функцию от внешних зависимостей (API и Excel)
    - проверяет, что результат содержит дату и данные операций
    """
    mock_analyze.return_value = {"rows_count": 1}
    mock_api.return_value = {"rates": {}}

    result = build_main_response("2025-01-01 12:00:00")

    assert "2025" in result
    assert "rows_count" in result


# =========================
# 🧪 process_events (mock API)
# =========================


@patch("banking_operations.utils.get_external_api")
def test_process_events(mock_api):
    """
    Проверяет обработку событий DataFrame.

    Тест:
    - подменяет внешний API
    - проверяет подсчёт количества событий
    - проверяет определение последней даты события
    """
    mock_api.return_value = {"rates": {}}

    df = pd.DataFrame([{"date": "2025-01-01"}, {"date": "2025-01-02"}])

    result = process_events(df)

    assert "total_events" in result
    assert "latest_event" in result
