from PyQt6.QtWidgets import QPushButton

from config.global_setting import global_setting
from theme.ThemeManager import ThemeManager


class ThemedWidget:
    """混入类实现主题响应"""

    def __init__(self):
        self.theme_manager = global_setting.get_setting("theme_manager")

        self.theme_manager.theme_changed.connect(self._update_theme)

    def _update_theme(self):
        self.setStyleSheet(self.theme_manager.get_style_sheet())


class ThemedButton(QPushButton, ThemedWidget):
    def __init__(self):
        super().__init__()
        self._update_theme()
