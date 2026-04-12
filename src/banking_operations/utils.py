import json
import logging
from datetime import datetime
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)

# --- парсинг даты ---
def parse_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logging.error("Неверный формат даты")
        return None


# --- работа с pandas ---
def datetime_to_dataframe(dt):
    data = {
        "date": [dt.date().isoformat()],
        "time": [dt.time().isoformat()]
    }
    df = pd.DataFrame(data)
    return df


# --- API (пример: текущее время) ---
def get_external_data():
    try:
        response = requests.get("https://api.apilayer.com/exchangerates_data/convert")
        return response.json()
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return {}


# --- формирование JSON ---
def make_json_response(data):
    return json.dumps(data, ensure_ascii=False, indent=4)
