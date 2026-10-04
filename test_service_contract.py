"""Контрактные тесты источника сигналов.

ВАЖНО: тут источник это `simulator.py` (мок из задания).
Тесты проверяют данные и работу TCP слоя. Когда подключаем настоящий
сервис продукта, надо заменить клиент, а проверки останутся те же.

Негативный кейс (сервис недоступен) проверяет обрыв соединения.
"""
import time

import pytest

from config import EXPECTED_SIGNALS, VALUE_ABS_LIMIT
from helpers import find_free_port
from service_client import read_signals


def test_service_returns_ten_signals(signal_service):
    signals = read_signals()
    assert len(signals) == EXPECTED_SIGNALS, (
        f"Ожидали {EXPECTED_SIGNALS} сигналов, получили {len(signals)}"
    )


def test_signal_ids_are_unique(signal_service):
    signals = read_signals()
    ids = [s["id"] for s in signals]
    assert len(set(ids)) == EXPECTED_SIGNALS, f"ID должны быть уникальны: {ids}"


def test_signal_fields_are_valid(signal_service):
    signals = read_signals()
    for s in signals:
        assert s.get("name"), f"Пустое имя: {s}"
        assert isinstance(s.get("value"), (int, float)), f"Значение не число: {s}"
        assert abs(s["value"]) <= VALUE_ABS_LIMIT, f"Значение вне диапазона: {s}"
        assert s.get("quality"), f"Не задано качество: {s}"
        assert s.get("ts"), f"Не задано время: {s}"


def test_signal_values_change_over_time(signal_service):
    """Значения это синусоида, поэтому между двумя кадрами они должны поменяться."""
    first = [s["value"] for s in read_signals()]
    time.sleep(1.2)  # сервис шлёт новый кадр раз в секунду
    second = [s["value"] for s in read_signals()]
    assert first != second, "Значения сигналов не меняются во времени"


def test_connection_refused_when_service_unavailable():
    """Негативный кейс: на свободном порту должна быть понятная ошибка ОС."""
    free_port = find_free_port()
    with pytest.raises(OSError):
        read_signals(port=free_port, timeout=1.0)
