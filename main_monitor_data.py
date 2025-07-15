import multiprocessing
import os
import time

from loguru import logger

from communication.ini_pareser.ini_parser import ini_parser
from config.global_setting import global_setting
from config.yamlParser import YamlParserObject
from dao.SQLite.Monitor_Datas_Handle import Monitor_Datas_Handle


def load_global_setting():
    # 加载监控数据配置
    config_file_path = os.getcwd() + "/monitor_datas_config.ini"
    # 配置数据{"section":{"key1":value1,"key2":value2,....}，...}
    config = ini_parser(config_file_path).read()
    if (len(config) != 0):
        logger.info("监控配置文件读取成功。")
    else:
        logger.error("监控配置文件读取失败。")
    global_setting.set_setting("monitor_data", config)
    # 加载gui配置存储到全局类中
    configer = YamlParserObject.yaml_parser.load_single("./gui_configer.yaml")
    if configer is None:
        logger.error(f"./gui_configer.yaml配置文件读取失败")
    global_setting.set_setting("configer", configer)
    return config


def main(q):
    # logger.remove(0)
    logger.add(
        "./log/monitor_data/monitor_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} |{process.name} | {thread.name} |  {name} : {module}:{line} | {message}"
    )
    logger.info(f"{'-' * 30}monitor_data_start{'-' * 30}")
    # 设置全局变量
    load_global_setting()
    global_setting.set_setting("queue", q)

    # 创建数据库
    handle = Monitor_Datas_Handle()


if __name__ == "__main__":
    q = multiprocessing.Queue()
    main(q)
