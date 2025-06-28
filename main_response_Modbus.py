"""
模拟响应串口
"""
import struct
import threading
import time
import traceback

import serial
from loguru import logger
from serial.tools import list_ports

from util.time_util import time_util


class communication(threading.Thread):
    """
    串口类 子线程
    """

    def __init__(self, category="receive", index=0):
        """
        类实例化函数
        :param category 通讯串口类别 receive接收串口 send发送串口
        :param index 第几个串口的index 配置文件中的receive_port的下标
        :param config_file_path 串口配置文件地址 "./communicate_config.ini"
        :return 无返回值
        """
        super().__init__()
        self.index = index
        self.category = category

        self.port = "COM3"
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
            logger.error(f"{self.category}串口{str(self.port)}连接--当前设备无可用的端口")
            return True
        if str(self.port) not in available_ports:
            logger.error(
                f"{self.category}串口{str(self.port)}连接--配置文件中的端口{str(self.port)}无法使用，请换个端口！")
            logger.error(f"串口{str(self.port)}连接--当前可用端口:{available_ports}")
            return True
        logger.info(f"{self.category}串口{str(self.port)}连接--当前可用端口:{available_ports}")
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
            logger.error(
                f"{self.category}串口{str(self.port)}连接--当前设备所设置端口{str(self.port)}错误！")
            logger.error(f"{self.category}串口{str(self.port)}实例化失败！")
            self.running = False
        else:

            try:
                self.ser = serial.Serial(
                    port=self.port,
                    baudrate=115200,
                    bytesize=8,
                    parity='N',
                    stopbits=1,
                    timeout=1
                )
                logger.info(f"{self.category}串口{str(self.port)}连接成功")
            except KeyboardInterrupt:
                logger.error(f"{self.category}串口{str(self.port)}连接--程序被用户终止！")
                self.running = False
            except Exception as e:
                logger.error(
                    f"{self.category}串口{str(self.port)}连接--发生错误: {e} |  异常堆栈跟踪：{traceback.print_exc()}！")
                self.running = False
            finally:
                pass
                # if self.ser and self.ser.is_open:
                #     self.ser.close()
                #     print("串口已关闭")

    def run(self):
        # 接收数据
        if self.running:
            # 接收串口介绍数据
            if self.category == "receive":
                # 全局变量
                self.receive()
            # 发送串口发送数据
            else:
                self.send()
        pass

    def stop(self):

        self.running = False
        logger.warning(f"{self.category}串口{str(self.port)}连接线程停止")
        self.join()  # 等待线程结束

    def send(self):
        """
        发送数据
        :return:
        """
        logger.info(f"{self.category}串口{str(self.port)}开始发送数据")
        # while self.running:  # 循环接收数据
        #
        #     # date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        #     # 生成一个指定范围内的浮点数，例如 1.5 到 5.5
        #     datas = {}
        #     data = ""
        #     data = str(random.uniform(-100, 100))
        #     datas['data'] = data
        #     datas['index'] = self.index
        #     datas_str = json.dumps(datas)
        #     logger.info(f"{self.category}串口{str(self.port)}发送数据: {datas_str}")
        #     self.ser.write(datas_str.encode())
        #     time.sleep(float(self.config['Serial']['delay']))

    def binary_to_hex(self, binary_str):
        """
        根据二进制字符串的位数转成相应个数的16进制数
        :param binary_str:
        :return:
        """
        # 检查输入是否为有效的二进制字符串
        if not all(bit in '01' for bit in binary_str):
            raise ValueError("Input must be a binary string.")

        # 计算需要补充的零的数量
        padding_length = (4 - (len(binary_str) % 4)) % 4

        # 补零
        padded_str = '0' * padding_length + binary_str

        # 结果列表
        hex_values = []

        # 每4位分一组
        for i in range(0, len(padded_str), 4):
            # 取出当前的4位二进制数
            chunk = padded_str[i:i + 4]

            # 将4位二进制字符串转换为整数
            hex_value = int(chunk, 2)

            # 转换为16进制并去掉 '0x' 前缀，并转换为大写
            hex_values.append(hex(hex_value)[2:].upper())

        return hex_values

    def calculate_crc(self, data: bytes) -> bytes:
        '''计算Modbus RTU CRC-16，小端返回'''
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return struct.pack('<H', crc)

    def build_frame(self, slave_id, function_code, data_hex_list):
        '''
        构造完整 Modbus RTU 报文（包含CRC）
        data_hex_list: 4个字节数据，十六进制字符串，如 ['00', '00', '00', 'FF']
        返回: 完整的 bytes 报文
        '''
        try:
            # 字符串转整数
            slave_id = int(slave_id, 16)
            function_code = int(function_code, 16)
            logger.info(f"data_hex_list: {data_hex_list}")
            data_bytes = [int(x, 16) for x in data_hex_list]
            logger.info(f"data_hex_list: {data_hex_list}|data_bytes: {data_bytes}")
            # 组装帧
            frame = struct.pack('>B B B B B', slave_id, function_code, *data_bytes)
            crc = self.calculate_crc(frame)
            str_frame = frame.hex()
            str_crc = crc.hex()
            logger.info(f"frame: {frame} , {str_frame}|crc: {crc} , {str_crc}")
            return frame + crc
        except Exception as e:
            logger.error(f"{time_util.get_format_from_time(time.time())}-{self.port}-构造报文出错: {e}")
            return None

    def receive(self):
        """
        接收数据
        :return:
        """

        logger.info(f"{self.category}串口{str(self.port)}开始接收数据")
        while self.running:
            # 读取数据（非阻塞方式）
            count = self.ser.inWaiting()
            if count != 0:
                # data = self.ser.readline()
                data = self.ser.read(count)
                self.ser.flushInput()
                if data:
                    try:
                        logger.info(f"{self.category}串口{str(self.port)}接收数据: {data}|未转义：{data.hex()}")
                        return_bytes = self.build_frame(slave_id='2', function_code='2',
                                                        data_hex_list=['1'] + self.binary_to_hex("00111111"))
                        # 根据发送来的数据进行响应
                        self.ser.write(return_bytes)

                    except UnicodeDecodeError:
                        logger.info(f"{self.category}串口{str(self.port)}接收原始字节: {data.hex()}")
                time.sleep(1)  # 避免CPU占用过高


def main():
    # 加载日志配置
    logger.add(
        "./log/comm/COM_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} |{process.name} | {thread.name} |  {name} : {module}:{line} | {message}"
    )
    logger.info(f"{'-' * 30}comm_start{'-' * 30}")
    try:
        communication_received_thread = communication(category="receive", index=0)
        communication_received_thread.start()
    except Exception as e:
        logger.error(f"模拟响应串口出错！:{e}")
    pass
