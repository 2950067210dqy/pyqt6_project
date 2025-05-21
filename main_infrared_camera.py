# 加载日志配置
import os
import time

from loguru import logger

from communication.ini_pareser.ini_parser import ini_parser
from config.global_setting import global_setting
from util.time_util import time_util


def load_global_setting():
    # 加载相机配置
    config_file_path = os.getcwd() + "/camera_config.ini"

    # 串口配置数据{"section":{"key1":value1,"key2":value2,....}，...}
    config = ini_parser(config_file_path).read()
    if (len(config) != 0):
        logger.info("相机配置文件读取成功。")
    else:
        logger.error("相机配置文件读取失败。")
    global_setting.set_setting("camera_config", config)
    # 记录运行时间的开始时间
    start_time = time.time()
    global_setting.set_setting("start_time", start_time)
    logger.info(f"相机连接开始时间：{time_util.get_format_from_time(start_time)}")
    # 记录运行时上一次删除文件时间
    last_delete_time = time.time()
    global_setting.set_setting("last_delete_time", last_delete_time)
    return config


logger.add(
    "./log/infrared_camera/i_camera_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    enqueue=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} |{process.name} | {thread.name} |  {name} : {module}:{line} | {message}"
)
logger.info(f"{'-' * 30}infrared_camera_start{'-' * 30}")
# 设置全局变量
load_global_setting()
