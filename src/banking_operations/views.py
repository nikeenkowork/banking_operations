from utils import build_main_response, process_events


# =========================
# 🏠 ГЛАВНАЯ СТРАНИЦА
# =========================
def main_page(date_time: str) -> dict:
    """
    Главная страница приложения.

    Принимает дату и время пользователя и формирует основной ответ
    через функцию build_main_response из модуля utils.

    Args:
        date_time (str): дата и время в строковом формате (YYYY-MM-DD HH:MM:SS)

    Returns:
        str: JSON-строка с ответом главной страницы
    """
    return build_main_response(date_time)


# =========================
# 📅 СТРАНИЦА СОБЫТИЙ
# =========================
def events_page(df) -> str:
    """
    Страница событий.

    Обрабатывает входной DataFrame с событиями и формирует ответ
    через функцию process_events из модуля utils.

    Args:
        df (pd.DataFrame): DataFrame с событиями

    Returns:
        str: JSON-строка с результатом обработки событий
    """
    return process_events(df)