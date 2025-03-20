from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QColor

from config.global_setting import global_setting


class ThemeManager(QObject):
    _instance = None
    theme_changed = pyqtSignal()

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._init_themes(cls._instance)
        return cls._instance

    @classmethod
    def _init_themes(cls, instance):

        # 定义主题配置
        cls._themes = {
            "dark": {
                "--primary": "rgb(40, 48, 65)",
                "--secondary": "#3C3F41",
                "--text": "rgb(245, 245, 245)",
                "--highlight": "#4B6EAF",
                "--border": "#555555"
            },
            "light": {
                "--primary": "#F0F0F0",
                "--secondary": "#FFFFFF",
                "--text": "#333333",
                "--highlight": "#0078D4",
                "--border": "#CCCCCC"
            }
        }
        # instance._current_theme = global_setting.get_setting("style")
        instance._current_theme = "dark"

    @pyqtProperty(str)
    def current_theme(self):
        return self._current_theme

    @current_theme.setter
    def current_theme(self, theme_name):
        if theme_name in self._themes:
            self._current_theme = theme_name
            self.theme_changed.emit()

    def get_style_sheet(self):
        theme = self._themes[self._current_theme]
        return f"""
            * {{
                qproperty-themePrimary: {theme['--primary']};
                qproperty-themeSecondary: {theme['--secondary']};
                qproperty-themeText: {theme['--text']};
                qproperty-themeHighlight: {theme['--highlight']};
                qproperty-themeBorder: {theme['--border']};
            }}
            QWidget {{
                background-color: {theme['--primary']};
                color: {theme['--text']};
               
            }}
            QPushButton {{
                background-color: {theme['--secondary']};
                padding: 5px 10px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme['--highlight']};
            }}
            QLineEdit {{
                background-color: {theme['--secondary']};
                border: 2px solid {theme['--border']};
                padding: 5px;
            }}
        """
