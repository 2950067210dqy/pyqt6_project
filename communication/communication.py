import threading

from communication.ini_pareser.ini_parser import ini_parser

import serial
from serial.tools import list_ports
from loguru import logger
import time


class communication(threading.Thread):
    """
    串口类 子线程
    """
    config_file_path = "./serial_port_config.ini"

    def __init__(self):
        """
        类实例化函数
        :param
        :return 无返回值
        """
        super().__init__()
        # 串口配置
        self.config_parser = ini_parser(self.config_file_path)
        # 串口配置数据{"section":{"key1":value1,"key2":value2,....}，...}
        self.config = self.config_parser.read()
        if (len(self.config) != 0):
            logger.info("串口配置文件读取成功。")
        else:
            logger.error("串口配置文件读取失败。")
            return
        self.ser = None  # 串口类
        self.running = True  # 控制线程运行的标志
        # 串口接收实例化
        self.serial_init()
        pass

    def is_port_occupied(self):
        """
        检测我们的配置端口是否被占用
        :return: True False
        """
        # 获取可用的端口
        available_ports = self.list_available_ports()
        # 判断配置的端口是否可用
        if not available_ports:
            logger.error(f"串口{str(self.config['Serial']['port'])}连接--当前设备无可用的端口")
            return True
        if str(self.config['Serial']['port']) not in available_ports:
            logger.error(
                f"串口{str(self.config['Serial']['port'])}连接--配置文件中的端口{str(self.config['Serial']['port'])}无法使用，请换个端口！")
            logger.error(f"串口{str(self.config['Serial']['port'])}连接--当前可用端口:{available_ports}")
            return True
        return False

    def list_available_ports(self):
        """
        获取可用的端口
        :return:[port,...]
        """
        ports = list_ports.comports()
        return [port.device for port in ports]

    def serial_init(self):
        """
        串口实例化 读取ini的配置文件进行配置
        :return:无
        """
        if self.is_port_occupied():
            logger.error("串口连接--当前设备所设置端口错误！")
            logger.error(f"串口实例化失败！")
            self.running = False
        else:
            try:
                self.ser = serial.Serial(
                    port=str(self.config['Serial']['port']),  # 端口号（Windows下为COMx，Linux下为/dev/ttyUSBx）
                    baudrate=int(self.config['Serial']['baudrate']),  # 波特率（常见值：9600, 115200等）
                    bytesize=int(self.config['Serial']['bytesize']),  # 数据位（默认为8）
                    parity=serial.PARITY_NONE if str(
                        self.config['Serial']['parity']).lower() == "none" else serial.PARITY_EVEN if str(
                        self.config['Serial']['parity']).lower() == "even" else serial.PARITY_ODD,
                    # 校验位（NONE, EVEN, ODD）
                    stopbits=int(self.config['Serial']['stopbits']),  # 停止位（1或2）
                    timeout=int(self.config['Serial']['timeout']),  # 读取超时时间（秒）
                )
                logger.info(f"串口{str(self.config['Serial']['port'])}连接成功")
            except KeyboardInterrupt:
                logger.error(f"串口{str(self.config['Serial']['port'])}连接--程序被用户终止！")
            except Exception as e:
                logger.error(f"串口{str(self.config['Serial']['port'])}连接--发生错误: {e}！")
            finally:
                pass
                # if self.ser and self.ser.is_open:
                #     self.ser.close()
                #     print("串口已关闭")

    def run(self):
        # 接收数据
        if self.running:
            self.recieve()

        pass

    def stop(self):
        self.running = False
        logger.warning(f"串口{str(self.config['Serial']['port'])}连接线程停止")
        self.join()  # 等待线程结束

    def recieve(self):
        """
        接收数据
        :return:
        """
        logger.info(f"串口开始接收数据")
        while self.running:
            # 读取数据（非阻塞方式）
            if self.ser.in_waiting > 0:
                data = self.ser.readline()
                if data:
                    try:
                        decoded = data.decode('utf-8').strip()
                        logger.info(f"串口{str(self.config['Serial']['port'])}接收数据 {decoded}")
                    except UnicodeDecodeError:
                        logger.info(f"串口{str(self.config['Serial']['port'])}接收原始字节 {data.hex()}")
            time.sleep(0.01)  # 避免CPU占用过高
