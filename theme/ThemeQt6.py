from PyQt6.QtWidgets import QPushButton, QWidget

from config.global_setting import global_setting
from config.logo_config import logger_diy
from theme.ThemeManager import ThemeManager


class ThemedWidget(QWidget):
    """混入类实现主题响应"""

    def __init__(self):
        super().__init__()
  
        global_setting.get_setting("theme_manager").theme_changed.connect(self._update_theme)
        self._init_style_sheet()

    # 加载qss样式
    def _init_style_sheet(self):
        if hasattr(self, ("frame")) and self.frame != None:
            self.frame.setStyleSheet(global_setting.get_setting("theme_manager").get_style_sheet())

    def _update_theme(self):
        self._init_style_sheet()
        self.setStyleSheet(global_setting.get_setting("theme_manager").get_style_sheet())


class ThemedButton(QPushButton, ThemedWidget):
    def __init__(self):
        super().__init__()
        self._update_theme()
