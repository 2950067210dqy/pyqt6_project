from PyQt6.QtWidgets import QPushButton

from theme.ThemeManager import ThemeManager


class ThemedWidget:
    """混入类实现主题响应"""

    def __init__(self):
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self._update_theme)
        self._update_theme()

    def _update_theme(self):
        self.setStyleSheet(self.theme_manager.get_style_sheet())


class ThemedButton(ThemedWidget, QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self._update_theme()
