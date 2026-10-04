"""TCP клиент к сервису сигналов.

Читает `count` сигналов по сети. Нужен для контрактных тестов, чтобы
независимо от GUI проверить что сервис отдаёт корректные данные.
"""
import json
import socket
import time

from config import HOST, PORT, EXPECTED_SIGNALS


def read_signals(
    count: int = EXPECTED_SIGNALS,
    timeout: float = 5.0,
    host: str = HOST,
    port: int = PORT,
) -> list[dict]:
    """Подключается к сервису и читает `count` сигналов (строки JSON).

    Возвращает список словарей. Если за `timeout` пришло меньше сигналов,
    поднимает TimeoutError с понятным текстом.
    """
    signals: list[dict] = []
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        buffer = b""
        deadline = time.time() + timeout
        while len(signals) < count and time.time() < deadline:
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            buffer += chunk
            # разбираем только целые строки (кадр может прийти частями)
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.strip()
                if line:
                    signals.append(json.loads(line.decode("utf-8")))
    if len(signals) < count:
        raise TimeoutError(
            f"Получено {len(signals)} из {count} сигналов за {timeout} c"
        )
    return signals[:count]
