"""Общие фикстуры для тестов."""
import threading

import pytest

import simulator
from config import APP_PATH, WIN_TITLE_RE
from helpers import wait_for_port


@pytest.fixture(scope="session")
def signal_service():
    """Поднимает сервис-симулятор и ждёт чтобы порт поднялся, без всяких sleep."""
    stop = threading.Event()
    thread = threading.Thread(target=simulator.serve, args=(stop,), daemon=True)
    thread.start()
    if not wait_for_port():
        stop.set()
        pytest.fail("Сервис-симулятор не поднялся на порту")
    yield
    stop.set()
    thread.join(timeout=3)


@pytest.fixture
def ui():
    """Фикстура GUI: запускает приложение, отдаёт адаптер, закрывает после теста.

    Если APP_PATH не задан, то UI-тесты пропускаются. Если GUI-адаптер
    недоступен в этой ОС (например pywinauto на Linux), тоже пропускаем.
    """
    if not APP_PATH:
        pytest.skip("APP_PATH не задан — UI-тесты пропущены")
    try:
        from ui_adapter import UiAdapter

        adapter = UiAdapter(APP_PATH, WIN_TITLE_RE)
    except ImportError as e:
        pytest.skip(f"GUI-адаптер недоступен в этой ОС: {e}")
    yield adapter
    adapter.close()
