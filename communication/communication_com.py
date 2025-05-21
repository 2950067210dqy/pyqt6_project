import json
import os
import queue
import random
import threading
from datetime import datetime

from communication.ini_pareser.ini_parser import ini_parser

import serial
from serial.tools import list_ports
from loguru import logger
import time

# 创建一个线程安全的队列 队列来存储我们接收到的数据 全局变量
from communication.util.folder_util import folder_util, File_Types
from communication.util.time_util import time_util

Q = queue.Queue()
# 用来表示两个线程的生命 全局变量
receive_thread_alive = False
store_thread_alive = False
# 创建三个锁
Q_lock = threading.Lock()
receive_thread_alive_lock = threading.Lock()
store_thread_alive_lock = threading.Lock()


class store_data(threading.Thread):
    """
    存储数据线程
    """

    def __init__(self, config_file_path="./communicate_config.ini", save_pre_paths=[""]):
        super().__init__()
        # 保存文件的前缀路径
        self.save_pre_paths = save_pre_paths
        # 串口配置
        self.config_parser = ini_parser(config_file_path)
        # 串口配置数据{"section":{"key1":value1,"key2":value2,....}，...}
        self.config = self.config_parser.read()
        if (len(self.config) != 0):
            logger.info("communication_com_store_data通讯配置文件读取成功。")
            self.running = True  # 控制线程运行的标志
        else:
            logger.error("communication_com_store_data通讯配置文件读取失败。")
            self.running = False  # 控制线程运行的标志
            return

        pass

    def run(self):
        # 全局变量
        global store_thread_alive, store_thread_alive_lock
        # 加锁 解锁过程会在with后自动解锁
        with store_thread_alive_lock:
            store_thread_alive = True
        logger.info(f"存储数据线程开始工作")
        while self.running:
            # 存储数据
            self.store()
            pass
        pass

    def stop(self):
        # 全局变量
        global store_thread_alive, store_thread_alive_lock
        # 加锁 解锁过程会在with后自动解锁
        with store_thread_alive_lock:
            store_thread_alive = False
        self.running = False
        logger.warning(f"存储数据线程停止")
        # 清空队列
        while not Q.empty():
            try:
                # 加锁
                with Q_lock:
                    Q.get_nowait()  # 不阻塞地取出所有元素
                # 解锁会在with块结束后自动处理
            except queue.Empty:
                break
        self.join()  # 等待线程结束

    def store(self):
        """
        存储数据
        :return:
        """
        global Q, Q_lock, receive_thread_alive
        # 队列中有数据在存储 且接收数据线程存活 才存数据
        if (not Q.empty() and receive_thread_alive):
            try:
                # 加锁
                with Q_lock:
                    data = Q.get()  # 修改全局变量
                # 解锁会在with块结束后自动处理
            except queue.Empty:
                logger.error(f"数据队列Q为空，获取数据失败！")
            logger.info(f"存储数据线程开始存储数据: {data}")
            # 存储到文件里
            self.store_to_file(data)
            pass

    def store_to_file(self, data=None):
        """
        将数据存储到文件里
        :param data 需要存储的数据
        :return:
        """
        # 获取年 第几周 第几天
        data_dict = json.loads(data)

        year, week_number, weekday = time_util.get_current_week_info()
        file_type = str(self.config['Storage']['file_type']).lower()
        folder_path = self.save_pre_paths[data_dict['index']] + str(year) + "/" + f"{str(week_number)}week" + "/"
        # 创建文件夹
        if not folder_util.is_exist_folder(folder_path):
            folder_util.create_folder(folder_path)
        match file_type:
            case File_Types.TXT.value:
                # txt
                file_path = folder_path + str(weekday) + "." + file_type
                data = data_dict['data'] + " " + datetime.now().strftime('%Y-%m-%d/%H:%M:%S.%f')[:-3]
                folder_util.create_file_txt(file_path=file_path, data=data)
            case File_Types.CSV.value:
                # csv
                pass
            case File_Types.XLSX.value:
                # xlsx
                pass
            case _:
                # 文件格式有误
                logger.error(f"存储的文件类型配置{file_type}有误！,应为下列一种{[type for type in File_Types]}")


class communication(threading.Thread):
    """
    串口类 子线程
    """

    def __init__(self, category="receive", index=0, config_file_path="./communicate_config.ini"):
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
        # 串口配置
        self.config_parser = ini_parser(config_file_path)
        # 串口配置数据{"section":{"key1":value1,"key2":value2,....}，...}
        self.config = self.config_parser.read()
        if (len(self.config) != 0):
            logger.info("communication_com_communication通讯配置文件读取成功。")
        else:
            logger.error("communication_com_communication通讯配置文件读取失败。")
            return
        self.config['Serial']['port'] = \
            [item.strip() for item in self.config['Serial'][self.category + "_port"].split(',')][self.index]
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
            logger.error(f"{self.category}串口{str(self.config['Serial']['port'])}连接--当前设备无可用的端口")
            return True
        if str(self.config['Serial']['port']) not in available_ports:
            logger.error(
                f"{self.category}串口{str(self.config['Serial']['port'])}连接--配置文件中的端口{str(self.config['Serial']['port'])}无法使用，请换个端口！")
            logger.error(f"串口{str(self.config['Serial']['port'])}连接--当前可用端口:{available_ports}")
            return True
        logger.info(f"{self.category}串口{str(self.config['Serial']['port'])}连接--当前可用端口:{available_ports}")
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
                f"{self.category}串口{str(self.config['Serial']['port'])}连接--当前设备所设置端口{str(self.config['Serial']['port'])}错误！")
            logger.error(f"{self.category}串口{str(self.config['Serial']['port'])}实例化失败！")
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
                logger.info(f"{self.category}串口{str(self.config['Serial']['port'])}连接成功")
            except KeyboardInterrupt:
                logger.error(f"{self.category}串口{str(self.config['Serial']['port'])}连接--程序被用户终止！")
                self.running = False
            except Exception as e:
                logger.error(f"{self.category}串口{str(self.config['Serial']['port'])}连接--发生错误: {e}！")
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
                global receive_thread_alive, receive_thread_alive_lock
                # 加锁 解锁过程会在with后自动解锁
                with receive_thread_alive_lock:
                    receive_thread_alive = True
                self.receive()
            # 发送串口发送数据
            else:
                self.send()
        pass

    def stop(self):
        # 全局变量
        global receive_thread_alive, receive_thread_alive_lock
        # 加锁 解锁过程会在with后自动解锁
        with receive_thread_alive_lock:
            receive_thread_alive = False
        self.running = False
        logger.warning(f"{self.category}串口{str(self.config['Serial']['port'])}连接线程停止")
        self.join()  # 等待线程结束

    def send(self):
        """
        发送数据
        :return:
        """
        logger.info(f"{self.category}串口{str(self.config['Serial']['port'])}开始发送数据")
        while self.running:  # 循环接收数据

            # date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            # 生成一个指定范围内的浮点数，例如 1.5 到 5.5
            datas = {}
            data = ""
            data = str(random.uniform(-100, 100))
            datas['data'] = data
            datas['index'] = self.index
            datas_str = json.dumps(datas)
            logger.info(f"{self.category}串口{str(self.config['Serial']['port'])}发送数据: {datas_str}")
            self.ser.write(datas_str.encode())
            time.sleep(float(self.config['Serial']['delay']))

    def receive(self):
        """
        接收数据
        :return:
        """
        # 获取全局变量 Q队列和Q_lock
        global Q, Q_lock, store_thread_alive
        logger.info(f"{self.category}串口{str(self.config['Serial']['port'])}开始接收数据")
        while self.running:
            # 读取数据（非阻塞方式）
            count = self.ser.inWaiting()
            if count != 0:
                # data = self.ser.readline()
                data = self.ser.read(count)
                self.ser.flushInput()
                if data:
                    try:
                        decoded = data.decode('utf-8').strip()
                        # 必须保证 我们的存储线程活着才把数据放到队列里 防止内存泄漏
                        if store_thread_alive:
                            # 加锁
                            with Q_lock:
                                Q.put(decoded)  # 修改全局变量
                            # 解锁会在with块结束后自动处理
                        logger.info(f"{self.category}串口{str(self.config['Serial']['port'])}接收数据: {decoded}")
                    except UnicodeDecodeError:
                        logger.info(f"{self.category}串口{str(self.config['Serial']['port'])}接收原始字节: {data.hex()}")
                time.sleep(float(self.config['Serial']['delay']))  # 避免CPU占用过高
