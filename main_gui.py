import multiprocessing
import os
import sys
import time
import traceback

from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QApplication
from loguru import logger

from communication.ini_pareser.ini_parser import ini_parser
from config.global_setting import global_setting
from config.yamlParser import YamlParserObject
from entity.MyQThread import MyQThread
from index.all_windows import AllWindows
# Author: Qinyou Deng
# Create Time:2025-03-01
# Update Time:2025-04-07
from theme.ThemeManager import ThemeManager


class read_queue_data_Thread(MyQThread):
    def __init__(self, name):
        super().__init__(name)
        self.queue = None
        self.camera_list = None
        pass

    def dosomething(self):
        if not self.queue.empty():
            print(f"gui_{self.queue.get()}")
        pass


read_queue_data_thread = read_queue_data_Thread(name="main_gui_camera_read_queue_data_thread")


def load_global_setting():
    # 加载相机配置
    config_file_path = os.getcwd() + "/camera_config.ini"

    # 串口配置数据{"section":{"key1":value1,"key2":value2,....}，...}
    config = ini_parser(config_file_path).read()
    if (len(config) != 0):
        logger.info("相机配置文件读取成功。")
    else:
        logger.error("相机配置文件读取失败。")
        quit_qt_application()
    global_setting.set_setting("camera_config", config)

    # 加载串口通讯配置
    config_file_path = global_setting.get_setting("communiation_project_path") + "/communicate_config.ini"

    # 串口配置数据{"section":{"key1":value1,"key2":value2,....}，...}
    serial_config = ini_parser(config_file_path).read()
    if (len(serial_config) != 0):
        logger.info("串口通讯配置文件读取成功。")
    else:
        logger.error("串口通讯配置文件读取失败。")
        quit_qt_application()
    global_setting.set_setting("serial_config", serial_config)
    # 加载gui配置存储到全局类中
    configer = YamlParserObject.yaml_parser.load_single("./gui_configer.yaml")
    if configer is None:
        logger.error(f"./gui_configer.yaml配置文件读取失败")
        quit_qt_application()
    global_setting.set_setting("configer", configer)
    # 当前左侧菜单项id 这里的值1是设个默认值无意义 会在实例化左菜单时根据真正的默认菜单覆盖这个值
    global_setting.set_setting("menu_id_now", 1)
    # 风格默认是dark  light
    global_setting.set_setting("style", configer['theme']['default'])
    # 图标风格 white black
    global_setting.set_setting("icon_style", "white")
    # 主题管理
    theme_manager = ThemeManager()
    global_setting.set_setting("theme_manager", theme_manager)
    # qt线程池
    thread_pool = QThreadPool()
    global_setting.set_setting("thread_pool", thread_pool)
    pass


def quit_qt_application():
    """
    退出QT程序
    :return:
    """
    logger.error(f"{'-' * 40}quit Qt application{'-' * 40}")
    #
    # 等待5秒系统退出
    step = 5
    while step >= 0:
        step -= 1
        time.sleep(1)
    sys.exit(0)


def start_qt_application():
    """
    qt程序开始
    :return: 无
    """
    # 启动qt
    logger.info("start Qt")
    app = QApplication(sys.argv)
    # 绑定突出事件
    app.aboutToQuit.connect(quit_qt_application)
    # 主窗口实例化
    try:
        allWindows = AllWindows()
    except Exception as e:
        logger.error(f"gui程序实例化失败，原因:{e} |  异常堆栈跟踪：{traceback.print_exc()}")
        return
    # 主窗口显示
    logger.info("Appliacation start")
    allWindows.show()
    # 系统退出
    sys.exit(app.exec())
    pass


def get_communiation_project_path():
    """
    获取串口通讯项目的路径  因为之前是通讯开了另一个项目所以需要保存通讯的工作目录到环境变量中，现在集成到一个程序中就不需要了
    :return:
    """
    # value = os.getenv('HOST_COMPUTER_DATA_STORAGE_LOC', 'Default')
    # 放到全局变量当中
    value = os.getcwd()
    global_setting.set_setting("communiation_project_path", value)
    logger.info(f"HOST_COMPUTER_DATA_STORAGE_LOC={value}")


def main(q, send_message_q):
    # 移除默认的控制台处理器（默认id是0）
    # logger.remove(0)
    # 加载日志配置
    logger.add(
        "./log/gui/gui_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 日志文件转存
        retention="30 days",  # 多长时间之后清理
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} |{process.name} | {thread.name} |  {name} : {module}:{line} | {message}"
    )
    logger.info(f"{'-' * 40}gui_start{'-' * 40}")
    logger.info(f"{__name__} | {os.path.basename(__file__)}|{os.getpid()}|{os.getppid()}")
    # 获取串口通讯项目路径
    get_communiation_project_path()

    # 加载全局配置
    logger.info("loading config start")
    load_global_setting()
    # 读取共享信息线程
    global read_queue_data_thread
    read_queue_data_thread.queue = q
    read_queue_data_thread.start()
    global_setting.set_setting("queue", q)
    global_setting.set_setting("send_message_queue", send_message_q)
    logger.info("loading config finish")
    # # 接收串口数据
    # receive_serial_port_data()

    # qt程序开始

    start_qt_application()




if __name__ == "__main__":
    q = multiprocessing.Queue()
    send_message_q = multiprocessing.Queue()
    main(q,send_message_q)
