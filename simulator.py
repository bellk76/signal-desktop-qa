"""Сервис симулятор из задания.

Шлёт 10 сигналов с меняющимися значениями (сенусоида) по TCP.
Кадр это по одному JSON на строку:
    {"id": 1, "name": "Signal_1", "value": 12.34, "quality": "Good", "ts": "..."}

В тестах используется как источник правды про данные.
Запуск руками:  python simulator.py
"""
import json
import math
import socket
import threading
import time

from config import HOST, PORT, EXPECTED_SIGNALS

SIGNAL_NAMES = [f"Signal_{i + 1}" for i in range(EXPECTED_SIGNALS)]


def _signal(index: int, seconds: float) -> dict:
    """Делает один сигнал: значение это синусоида со сдвигом по индексу."""
    return {
        "id": index + 1,
        "name": SIGNAL_NAMES[index],
        "value": round(math.sin(seconds + index) * 100, 3),
        "quality": "Good",
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def _handle_client(conn: socket.socket, start_time: float, stop_event: threading.Event) -> None:
    """Периодически шлёт клиенту пакет из 10 обновляемых сигналов.

    Завершается по stop_event или при отключении клиента.
    """
    try:
        while not stop_event.is_set():
            seconds = time.time() - start_time
            payload = "".join(
                json.dumps(_signal(i, seconds), ensure_ascii=False) + "\n"
                for i in range(EXPECTED_SIGNALS)
            )
            conn.sendall(payload.encode("utf-8"))
            # спим короткими шагами, чтобы быстро реагировать на stop_event
            stop_event.wait(1.0)
    except (ConnectionError, OSError):
        pass  # клиент отключился — это нормально
    finally:
        conn.close()


def serve(stop_event: threading.Event) -> None:
    """Поднимает TCP-сервер на HOST:PORT до установки stop_event."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(5)
    srv.settimeout(0.5)
    start_time = time.time()
    try:
        while not stop_event.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue  # проверяем stop_event
            threading.Thread(
                target=_handle_client, args=(conn, start_time, stop_event), daemon=True
            ).start()
    finally:
        srv.close()


if __name__ == "__main__":
    stop = threading.Event()
    print(f"Симулятор слушает {HOST}:{PORT} (Ctrl+C для остановки)")
    try:
        serve(stop)
    except KeyboardInterrupt:
        stop.set()
        print("\nОстановлено.")
