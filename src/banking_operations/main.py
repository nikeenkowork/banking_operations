from datetime import datetime

def main_page(date_time_str: str):
    try:
        dt = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

        return {
            "date": dt.date().isoformat(),
            "time": dt.time().isoformat()
        }

    except ValueError:
        return "Ошибка: неверный формат даты. Используй YYYY-MM-DD HH:MM:SS"


# --- пример запуска ---
if __name__ == "__main__":
    user_input = input("Введите дату и время: ")

    result = main_page(user_input)

    print(result)
