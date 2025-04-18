import sys

from PyQt6.QtWidgets import QApplication
from loguru import logger

from config.global_setting import global_setting
from config.yamlParser import YamlParserObject
from index.all_windows import AllWindows
from communication.communication_root import communication_root
# Author: Qinyou Deng
# Create Time:2025-03-01
# Update Time:2025-04-07
from theme.ThemeManager import ThemeManager


def load_global_setting():
    # 加载配置存储到全局类中
    configer = YamlParserObject.yaml_parser.load_single("./gui_configer.yaml")
    global_setting.set_setting("configer", configer)
    # 当前左侧菜单项id 这里的值1是设个默认值无意义 会在实例化左菜单时根据真正的默认菜单覆盖这个值
    global_setting.set_setting("menu_id_now", 1)
    # 风格默认是dark  light
    global_setting.set_setting("style", "dark")
    # 图标风格 white black
    global_setting.set_setting("icon_style", "white")
    # 主题管理
    theme_manager = ThemeManager()
    global_setting.set_setting("theme_manager", theme_manager)
    pass


def start_qt_application():
    """
    qt程序开始
    :return: 无
    """
    # 启动qt
    logger.info("start Qt")
    app = QApplication(sys.argv)
    # 主窗口实例化
    allWindows = AllWindows()
    # 主窗口显示
    logger.info("Appliacation start")
    allWindows.show()
    # 系统退出
    sys.exit(app.exec())
    pass


def recieve_serial_port_data():
    """
    接收串口数据
    :return:无
    """
    communication_root_obj = communication_root()
    logger.info("start serial port communication!")
    communication_root_obj.start()


if __name__ == '__main__':
    # 加载日志配置
    logger.add(
        "prod_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} : {module}:{line} | {message}"
    )
    logger.info(f"{'-' * 30}start{'-' * 30}")
    # 加载全局配置
    logger.info("loading config start")
    load_global_setting()
    logger.info("loading config finish")
    # 接收串口数据
    recieve_serial_port_data()
    # qt程序开始
    start_qt_application()
