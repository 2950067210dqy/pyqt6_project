import traceback

from loguru import logger

# Author: Qinyou Deng
# Create Time:2025-04-17
# Update Time:2025-04-17
from communication.communication_root import communication_root
from config.global_setting import global_setting
from enu.enviroment import enviroment


def receive_serial_port_data():
    """
    接收串口数据
    :return:无
    """

    communication_root_obj = communication_root(data_type="charts")
    logger.info("start serial port communication!")
    communication_root_obj.start()


def set_envir():
    """
    设置环境变量'HOST_COMPUTER_DATA_STORAGE_LOC' 上位机通讯数据存储文件地址
    :return:
    """
    envir = enviroment()
    envir.set_envir()


def main():
    # 移除默认的控制台处理器（默认id是0）
    logger.remove()
    # 加载日志配置
    logger.add(
        "./log/comm/COM_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} |{process.name} | {thread.name} |  {name} : {module}:{line} | {message}"
    )
    logger.info(f"{'-' * 30}comm_start{'-' * 30}")

    # 设置环境变量
    # set_envir()
    # 接收串口数据
    try:
        receive_serial_port_data()
    except Exception as e:
        logger.error(f"comm程序运行异常，原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}，终止comm进程")
