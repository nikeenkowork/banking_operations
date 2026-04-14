from datetime import datetime


def main_page(date_time_str: str):
    """
    Обрабатывает строку с датой и временем и возвращает раздельные значения даты и времени.

    Функция парсит входную строку в формате YYYY-MM-DD HH:MM:SS
    и преобразует её в словарь с датой и временем.

    Args:
        date_time_str (str): дата и время в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
        dict | str: словарь с ключами:
            - date (str): дата в формате YYYY-MM-DD
            - time (str): время в формате HH:MM:SS

        либо строка с ошибкой, если формат неверный
    """
    try:
        dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

        return {"date": dt.date().isoformat(), "time": dt.time().isoformat()}

    except ValueError:
        return "Ошибка: неверный формат даты. Используй YYYY-MM-DD HH:MM:SS"


# --- пример запуска ---
if __name__ == "__main__":
    user_input = input("Введите дату и время: ")

    result = main_page(user_input)

    print(result)
