"""Тут общие настройки для тестов и симулятора.

Все параметры можно поменять через переменные окружения,
поэтому код запускается из коробки без правок.
"""
import os

# --- Настройки сети для симулятора ---
HOST = os.getenv("SIGNAL_HOST", "127.0.0.1")
PORT = int(os.getenv("SIGNAL_PORT", "2001"))

# --- Что ждём от данных ---
EXPECTED_SIGNALS = int(os.getenv("EXPECTED_SIGNALS", "10"))
# Значение синусоиды: sin(x) * 100, тоесть от -100 до 100.
VALUE_ABS_LIMIT = float(os.getenv("VALUE_ABS_LIMIT", "100"))
CONNECT_TIMEOUT = float(os.getenv("CONNECT_TIMEOUT", "10"))

# --- Параметры GUI, нужны только UI тестам ---
# Если APP_PATH пустой, то UI-тесты пропускаются, а контрактные всё равно идут.
APP_PATH = os.getenv("APP_PATH", "")
WIN_TITLE_RE = os.getenv("WIN_TITLE_RE", r".*(Signal|Сигнал).*")
