from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QColor
from loguru import logger

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
                "--secondary": "#F0F0F0",
                "--text": "#333333",
                "--text_hover": "rgb(0, 0, 0)",
                "--highlight": "rgb(225,225,225)",
                "--selected": "rgb(215, 215, 215)",
                "--border": "#CCCCCC"
            }
        }
        instance._current_theme = global_setting.get_setting("style")
        logger.info("ThemeManger:instance._current_theme:  " + instance._current_theme)

    def get_button_style(self, isSelected=False):
        theme = self._themes[self._current_theme]
        if isSelected:
            return f"""
                QPushButton{{
                    background-color: {theme['--selected']};
                    color:{theme['--text']};
                   padding: 25px;
                    border-radius: 4px;
                    font-size:13px;
                }}
                QPushButton:hover{{
                    background:{theme['--highlight']};
                    color:{theme['--text_hover']};
                }}
                QPushButton:pressed {{
                    background:{theme['--selected']};    
                    color:{theme['--text_hover']};
                }}
            """
        else:
            return f"""
                QPushButton{{
                    background-color: {theme['--secondary']};
                    color:{theme['--text']};
                    padding: 25px;
                    border-radius: 4px;
                    font-size:13px;
                }}
                QPushButton:hover{{
                    background:{theme['--highlight']};
                    color:{theme['--text_hover']};
                }}
                QPushButton:pressed {{
                    background:{theme['--selected']};  
                    color:{theme['--text_hover']}  ;
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
        # logger_diy.log.info("ThemeManager的get_style_sheet：" + style_sheet)
        return style_sheet

    # 返回相应主题的颜色值 并都转成16进制颜色
    def get_themes_color(self, mode=0):
        # mode=0是直接返回颜色rgb字符串 mode=1 返回rgb数值的列表[r,g,b]
        if mode == 0:
            return self._themes[self._current_theme]
        else:
            themes = self._themes[self._current_theme]
            for key in themes:
                old_values = themes[key]
                new_values = self.from_rgb_to_16x(old_values)
                themes[key] = new_values
                pass
            return themes

    def get_rgb_numbers(self, rgb_str: str = "rgb(0,0,0)"):

        rgb_str_new = rgb_str.replace(" ", "")
        # 如果是16进制颜色str值则不处理
        if rgb_str_new[0] == "#":
            return rgb_str
        # 提取核心部分：去掉前4字符（rgb(）和末尾的 )
        content = rgb_str_new[4:-1]
        # 分割并转换
        r, g, b = map(int, content.split(','))
        return [r, g, b]

    # 将rgb转换成16进制
    def from_rgb_to_16x(self, rgb_str: str = "rgb(0,0,0)"):
        rgb_str_new = rgb_str.replace(" ", "")
        # 如果是16进制颜色str值则不处理
        if rgb_str_new[0] == "#":
            return rgb_str
        rgb_list = self.get_rgb_numbers(rgb_str_new)
        # 确保 RGB 值在 0-255 范围内
        r = max(0, min(rgb_list[0], 255))
        g = max(0, min(rgb_list[1], 255))
        b = max(0, min(rgb_list[2], 255))
        # 转换为两位十六进制并拼接（参考网页1[1](@ref)、网页6[6](@ref)）
        return "#{:02X}{:02X}{:02X}".format(r, g, b)
