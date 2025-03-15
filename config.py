import os
import json

TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise ValueError("Переменная окружения 'TOKEN' не установлена.")

ADMIN_ID = int(os.getenv('ADMIN_ID', 0))


FIREBASE_CREDENTIALS_JSON = os.getenv('FIREBASE_CREDENTIALS')
if not FIREBASE_CREDENTIALS_JSON:
    raise ValueError("Переменная окружения 'FIREBASE_CREDENTIALS' не установлена.")

try:
    FIREBASE_CREDENTIALS = json.loads(FIREBASE_CREDENTIALS_JSON)
except json.JSONDecodeError as e:
    raise ValueError(f"Ошибка при преобразовании FIREBASE_CREDENTIALS в JSON: {e}")