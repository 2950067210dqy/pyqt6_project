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

    @pyqtProperty(str)
    def current_theme(self):
        return self._current_theme

    @current_theme.setter
    def current_theme(self, theme_name):
        if theme_name in self._themes:
            self._current_theme = theme_name
            self.theme_changed.emit()

    @classmethod
    def _init_themes(cls, instance):

        # 定义主题配置
        cls._themes = {
            "dark": {
                "--primary": "rgb(40, 48, 65)",
                "--secondary": "rgb(40, 48, 65)",
                "--text": "rgb(245, 245, 245)",
                "--text_hover": "rgb(215, 215, 215)",
                "--highlight": "rgb(27,36,49)",
                "--selected": "rgb(0, 0, 0)",
                "--border": "#555555"
            },
            "light": {
                "--primary": "#F0F0F0",
                "--secondary": "#FFFFFF",
                "--text": "#333333",
                "--text_hover": "rgb(0, 0, 0)",
                "--highlight": "rgb(225,225,225)",
                "--selected": "rgb(215, 215, 215)",
                "--border": "#CCCCCC"
            }
        }
        instance._current_theme = global_setting.get_setting("style")
        print("ThemeManger:instance._current_theme:", instance._current_theme)

    def get_button_style(self, isSelected=False):
        theme = self._themes[self._current_theme]
        if isSelected:
            return f"""
                QPushButton{{
                    background-color: {theme['--selected']};
                    color:{theme['--text']}
                    padding: 5px 10px;
                    border-radius: 4px;
                }}
                QPushButton:hover{{
                    background:{theme['--highlight']};
                    color:{theme['--text_hover']}
                }}
                QPushButton:pressed {{
                    background:{theme['--selected']};    
                    color:{theme['--text_hover']}
                }}
            """
        else:
            return f"""
                QPushButton{{
                    background-color: {theme['--secondary']};
                    color:{theme['--text']}
                    padding: 5px 10px;
                    border-radius: 4px;
                }}
                QPushButton:hover{{
                    background:{theme['--highlight']};
                    color:{theme['--text_hover']}
                }}
                QPushButton:pressed {{
                    background:{theme['--selected']};  
                    color:{theme['--text_hover']}  
                }}
                    """

    def get_style_sheet(self):
        theme = self._themes[self._current_theme]
        style_sheet = f"""
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
            QLineEdit {{
                background-color: {theme['--secondary']};
                border: 2px solid {theme['--border']};
                padding: 5px;
            }}
        """ + self.get_button_style(isSelected=False)
        print("ThemeManager的get_style_sheet", style_sheet)
        return style_sheet
