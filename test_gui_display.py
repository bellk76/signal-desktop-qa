"""Критичный сценарий: поключение и отображение 10 сигналов в таблице.

UI-тесты требуют APP_PATH (путь к приложению) и подходящей технологии
доступа к GUI (см. ui_adapter.py). Без APP_PATH они пропускаются.
"""
import pytest

from config import EXPECTED_SIGNALS, VALUE_ABS_LIMIT
from helpers import wait_until
from service_client import read_signals


def _connect_and_wait(ui):
    ui.click_connect()
    assert wait_until(lambda: len(ui.rows()) == EXPECTED_SIGNALS), (
        f"Ожидали {EXPECTED_SIGNALS} сигналов, получили {len(ui.rows())}"
    )


def test_after_connect_ten_signals_displayed(ui):
    # 1) До подключения таблица пуста
    assert ui.rows() == [], "До подключения таблица должна быть пустой"

    # 2) Подключаемся и ждём 10 строк
    _connect_and_wait(ui)

    # 3) Проверяем корректность отображаемых данных
    rows = ui.rows()
    seen_ids = set()
    for i, row in enumerate(rows):
        assert len(row) >= 5, f"Строка {i}: ожидали 5 столбцов, получили {row}"
        signal_id, name, value, quality, timestamp = row[:5]
        assert signal_id and signal_id not in seen_ids, f"Строка {i}: пустой/дублирующийся ID"
        seen_ids.add(signal_id)
        assert name, f"Строка {i}: пустое имя"
        assert timestamp, f"Строка {i}: не указано время"
        assert quality, f"Строка {i}: не указано качество"
        # значение должно быть числом в ожидаемом диапазоне
        try:
            numeric = float(value.replace(",", "."))
        except ValueError:
            pytest.fail(f"Строка {i}: значение не число: {value!r}")
        assert abs(numeric) <= VALUE_ABS_LIMIT, f"Строка {i}: значение вне диапазона"


def test_displayed_ids_match_service(ui, signal_service):
    """Кросс проверка: набор ID в таблице совпадает с данными сервиса."""
    _connect_and_wait(ui)
    displayed = {row[0] for row in ui.rows()}
    from_service = {str(s["id"]) for s in read_signals()}
    assert displayed == from_service, (
        f"ID в интерфейсе {displayed} не совпадают с сервисом {from_service}"
    )


def test_refresh_updates_data(ui):
    _connect_and_wait(ui)
    before = ui.rows()

    ui.click_refresh()

    # ждём пока данные реально обновятся, без всяких sleep
    assert wait_until(lambda: ui.rows() != before), (
        "После нажатия «Обновить» данные не изменились"
    )
