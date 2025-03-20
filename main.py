import sys

from PyQt6.QtWidgets import QApplication

from config.global_setting import global_setting
from config.yamlParser import YamlParserObject
from index.all_windows import AllWindows

# Author: Qinyou Deng
# Create Time:2025-03-01
# Update Time:2025-03-19
from theme.ThemeManager import ThemeManager


def load_global_setting():
    # 加载配置存储到全局类中
    configer = YamlParserObject.yaml_parser.load_single("./config/configer.yaml")
    global_setting.set_setting("configer", configer)
    # 风格默认是dark  light
    global_setting.set_setting("style", "light")
    # 图标风格 white black
    global_setting.set_setting("icon_style", "white")
    # style_sheet = {}
    # style_sheet['dark'] = """
    # *{
    #     color:white;
    #     background:rgb(27,36,49);
    #     border:none;
    #   }
    # """
    # style_sheet['light'] = """
    #    *{
    #        color:black;
    #        background:rgb(237,246,249);
    #        border:none;
    #      }
    #    """
    # global_setting.set_setting("style_sheet", style_sheet)
    theme_manager = ThemeManager()
    global_setting.set_setting("theme_manager", theme_manager)
    pass


if __name__ == '__main__':
    # 加载配置
    load_global_setting()

    # 启动qt
    app = QApplication(sys.argv)
    # 主窗口实例化
    allWindows = AllWindows()
    # 主窗口显示
    allWindows.show()
    # 系统退出
    sys.exit(app.exec())
