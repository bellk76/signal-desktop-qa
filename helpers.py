"""Мелкие утилиты ожидания, вынес их из conftest (его лучше не импортировать)."""
import socket
import time

from config import CONNECT_TIMEOUT, HOST, PORT


def wait_until(predicate, timeout: float = CONNECT_TIMEOUT, interval: float = 0.2) -> bool:
    """Ждёт пока условие сработает, без всяких там sleep.

    Возвращает True если условие выполнилось за timeout, иначе False.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


def wait_for_port(host: str = HOST, port: int = PORT, timeout: float = 5.0) -> bool:
    """Ждёт пока порт начнёт принимать соединения (готовность сервиса)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def find_free_port(host: str = HOST) -> int:
    """Находит свободный порт, чтобы проверить отказ соединения."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))  # 0 => ОС сама выдаст свободный порт
        return sock.getsockname()[1]
