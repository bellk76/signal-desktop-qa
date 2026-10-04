"""Адаптер доступа к GUI тестируемого приложенеи.

Специально вынес всю работу с GUI в один класс: чтобы поменять
технологию или платформу, надо переписать только этот файл.

Сейчас реализовано под Windows (pywinauto, backend="uia").
Для Linux (C++/Qt) надо переписать на dogtail/AT-SPI, оставив методы:
    rows(), click_connect(), click_refresh(), close()
"""


class UiAdapter:
    def __init__(self, app_path: str, title_re: str):
        # импорт внутри, чтобы контрактные тесты запускались без pywinauto
        from pywinauto.application import Application

        self.app = Application(backend="uia").start(app_path)
        self.window = self.app.window(title_re=title_re)
        self.window.wait("ready", timeout=15)

    def rows(self) -> list[tuple]:
        """Возвращает строки таблицы как кортежи ячеек (ID, имя, значение, качество, время)."""
        table = self.window.child_window(auto_id="signalsTable", control_type="Table")
        result = []
        for row in table.descendants(control_type="DataItem"):
            cells = [c.window_text().strip() for c in row.descendants(control_type="Text")]
            result.append(tuple(cells))
        return result

    def click_connect(self) -> None:
        self.window.child_window(
            auto_id="connectButton", control_type="Button"
        ).click_input()

    def click_refresh(self) -> None:
        self.window.child_window(
            auto_id="refreshButton", control_type="Button"
        ).click_input()

    def close(self) -> None:
        self.app.kill()
