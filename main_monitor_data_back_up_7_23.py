import multiprocessing
import os
import queue
import threading
import time

import serial
from serial.tools import list_ports
from PyQt6.QtCore import pyqtSignal
from loguru import logger

from Modbus.Modbus import ModbusRTUMaster
from Modbus.Modbus_Type import Modbus_Slave_Type, Modbus_Slave_Ids, Modbus_Slave_Send_Messages
from communication.ini_pareser.ini_parser import ini_parser
from config.global_setting import global_setting
from config.yamlParser import YamlParserObject
from dao.SQLite.Monitor_Datas_Handle import Monitor_Datas_Handle
from entity.MyQThread import MyQThread
from util.time_util import time_util

# 全局变量
# 实现主线程发一整轮消息，当从线程响应完全部的消息后，主线程在发一整轮消息
MESSAGE_BATCH_SIZE = 0
total_messages_processed = 1
lock = threading.Lock()
batch_complete_event = threading.Event()

# 存储数据锁
store_Q_lock = threading.Lock()
store_Q = queue.Queue()


class read_queue_data_Thread(MyQThread):
    def __init__(self, name):
        super().__init__(name)
        self.queue = None
        self.send_thread: Send_thread = None
        pass

    def dosomething(self):
        if not self.queue.empty():
            message = self.queue.get()
            # message 结构{'to'发往哪个线程，'data'数据,'from'从哪发的}
            if message is not None and isinstance(message, dict) and len(message) > 0 and 'to' in message and message[
                'to'] == 'main_monitor_data':
                logger.error(f"{self.name}_get_message:{message}")
                if 'data' in message:
                    if self.send_thread is not None and self.send_thread.isRunning():
                        # 发送优先级高的报文
                        self.send_thread.add_message(message=message['data'], urgent=True, origin=message['from'])
                        pass
            else:
                # 把消息放回去
                self.queue.put(message)

        pass


read_queue_data_thread = read_queue_data_Thread(name="main_monitor_data_read_queue_data_thread")


class Store_Thread(MyQThread):
    """
    存储请求线程发来的数据到sqlite中
    """

    def __init__(self, name):
        self.handle = None
        super().__init__(name)

    def dosomething(self):
        global store_Q, store_Q_lock
        # 队列中有数据在存储 且接收数据线程存活 才存数据
        if not store_Q.empty():
            try:
                # 加锁
                with store_Q_lock:
                    data = store_Q.get()  # 修改全局变量
                # 解锁会在with块结束后自动处理
            except queue.Empty:
                logger.error(f"数据队列Q为空，获取数据失败！")
            logger.info(f"存储数据线程开始存储数据: {data}")
            # 存储到文件里
            self.store_to_data_base(data)
        time.sleep(float(global_setting.get_setting('monitor_data')['STORAGE']['delay']))
        pass

    def store_to_data_base(self, data):
        try:
            # 存储到数据库中
            if self.handle is not None:
                self.handle.stop()
            self.handle = Monitor_Datas_Handle()  # # 创建数据库
            self.handle.insert_data(data)
        except Exception as e:
            logger.error(f"{self.name}错误：{e}")
        pass

    def stop(self):
        super().stop()
        self.handle.stop()


class Send_thread(MyQThread):
    """
    请求数据线程
    """

    def __init__(self, name=None, modbus=None,
                 ):
        super().__init__(name)

        self.modbus: ModbusRTUMaster = modbus
        # 正常队列和紧急队列 紧急队列的消息立即处理
        self.normal_queue = queue.Queue()
        self.priority_queue = queue.Queue()
        self.lock = threading.Lock()

        pass

    def add_message(self, message, urgent=False, origin=""):
        # origin 为源头
        if urgent:
            self.priority_queue.put({'origin': origin, 'message': message})
        else:
            self.normal_queue.put(message)

    def init_modBus(self, port, origin=None):
        try:

            self.modbus = ModbusRTUMaster(port=port, timeout=float(
                global_setting.get_setting('monitor_data')['Serial']['timeout']),
                                          origin=origin
                                          )
        except Exception as e:
            logger.error(f"{self.name},实例化modbus错误：{e}")
            pass
        pass

    def set_modbus(self, modbus):
        self.modbus = modbus

    def run(self):
        logger.warning(f"{self.name} thread has been started！")
        global lock, total_messages_processed, store_Q, store_Q_lock
        global MESSAGE_BATCH_SIZE
        while self._running:
            self.mutex.lock()
            if self._paused:
                self.condition.wait(self.mutex)  # 等待条件变量
            self.mutex.unlock()

            try:
                # logger.info(self.send_messages)

                # 优先检查紧急队列
                try:
                    message = self.priority_queue.get_nowait()
                    send_message = message['message']
                    self.init_modBus(port=send_message['port'], origin=message['origin'])
                    logger.debug(f"{self.name}接收到查询报文。正在发送查询报文：{send_message}")
                    response, response_hex, send_state = self.modbus.send_command(
                        slave_id=send_message['slave_id'],
                        function_code=send_message['function_code'],
                        data_hex_list=send_message['data'],

                        is_parse_response=False
                    )
                    # 响应报文是正确的，即发送状态时正确的 进行解析响应报文

                    if send_state:
                        return_data, parser_message = self.modbus.parse_response(response=response,
                                                                                 response_hex=response.hex(),
                                                                                 send_state=True,
                                                                                 slave_id=
                                                                                 send_message['slave_id'],
                                                                                 function_code=
                                                                                 send_message['function_code'], )

                        # 把返回数据返回给源头
                        message_struct = {'to': message['origin'], 'data': parser_message, 'from': 'main_monitor_data'}
                        global_setting.get_setting("send_message_queue").put(message_struct)
                        logger.debug(f"main_monitor_data将响应报文的解析数据返回源头：{message_struct}")
                        pass
                except queue.Empty:
                    pass

                # 处理普通消息
                try:
                    send_message = self.normal_queue.get(timeout=0.1)
                    self.init_modBus(port=send_message['port'])
                    response, response_hex, send_state = self.modbus.send_command(
                        slave_id=send_message['slave_id'],
                        function_code=send_message['function_code'],
                        data_hex_list=send_message['data'],
                        is_parse_response=False
                    )
                    # 响应报文是正确的，即发送状态时正确的 进行解析响应报文
                    if send_state:
                        return_data, parser_message = self.modbus.parse_response(response=response,
                                                                                 response_hex=response.hex(),
                                                                                 send_state=True,
                                                                                 slave_id=
                                                                                 send_message['slave_id'],
                                                                                 function_code=
                                                                                 send_message['function_code'], )
                        # 加锁
                        with store_Q_lock:
                            # 放入队列给存储线程进行存储
                            store_Q.put(return_data)  # 修改全局变量
                        # logger.info(f"{total_messages_processed}|{return_data}")
                        pass
                    logger.info(f"响应报文{total_messages_processed}响应结束{'-' * 100}")
                    with lock:
                        if total_messages_processed % MESSAGE_BATCH_SIZE == 0:

                            total_messages_processed = 1
                            MESSAGE_BATCH_SIZE = 0
                            batch_complete_event.set()  # 通知主线程当前批次完成
                        else:
                            total_messages_processed += 1
                except queue.Empty:
                    break
            except Exception as e:
                logger.error(e)

            time.sleep(float(global_setting.get_setting('monitor_data')['SEND']['delay']))


def auto_detect_port():
    """
    自动检测通信串口
    :param baudrate:
    :param test_cmd:
    :param expected_response:
    :param timeout:
    :return:
    """
    ports = list_ports.comports()
    for port in ports:

        try:
            modbus = ModbusRTUMaster(port=port.device, timeout=1)
            response, response_hex, send_state = modbus.send_command(
                slave_id=Modbus_Slave_Send_Messages.UFC.value['send_messages'][0].message['slave_id'],
                function_code=Modbus_Slave_Send_Messages.UFC.value['send_messages'][0].message['function_code'],
                data_hex_list=Modbus_Slave_Send_Messages.UFC.value['send_messages'][0].message['data'],
                is_parse_response=False
            )

            # 响应报文是正确的，即发送状态时正确的 进行解析响应报文
            if send_state:
                return port.device
            # if modbus is not None:
            #     modbus.close()
        except Exception as e:
            logger.error(e)
            continue
    return None


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


def main(q, send_message_q):
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
    # 读取共享信息线程
    global read_queue_data_thread
    read_queue_data_thread.queue = send_message_q
    global_setting.set_setting("queue", q)
    global_setting.set_setting("send_message_queue", send_message_q)

    # 寻找通信端口
    port = auto_detect_port()
    while port is None:
        logger.error("未找到通讯串口！！！！！！！！！！！！！，正在重新寻找")
        port = auto_detect_port()
        time.sleep(2)

    # 存储线程
    store_thread = Store_Thread(name="monitor_data_store_message")
    store_thread.start()

    # 发送报文线程
    send_thread = Send_thread(name="monitor_data_send_message")
    send_thread.start()

    read_queue_data_thread.send_thread = send_thread
    read_queue_data_thread.start()

    # 发送消息
    global MESSAGE_BATCH_SIZE
    message_type = 0  # 0是只要传感器数值查询报文 1是所有查询报文
    while True:
        send_messages = []
        # 公共传感器数据的send_messages
        for data_type in Modbus_Slave_Type.Not_Each_Mouse_Cage_Message.value:
            if message_type == 1:
                # 所有消息
                for message_struct in data_type.value['send_messages']:
                    message_temp = message_struct.message
                    message_temp['port'] = port
                    send_thread.add_message(message=message_temp, urgent=False)
                    send_messages.append(message_temp)
                    MESSAGE_BATCH_SIZE += 1
            else:
                # 单个传感器值消息
                message_temp = data_type.value['send_messages'][0].message
                message_temp['port'] = port
                send_thread.add_message(message=message_temp, urgent=False)
                send_messages.append(message_temp)
                MESSAGE_BATCH_SIZE += 1
            pass
        # 每个笼子里的传感器的send_messages
        for data_type in Modbus_Slave_Type.Each_Mouse_Cage_Message.value:
            for mouse_cage in data_type.value['send_messages']:
                if message_type == 1:
                    # 所有消息
                    for message_struct in mouse_cage:
                        message_temp = message_struct.message
                        message_temp['port'] = port
                        send_thread.add_message(message=message_temp, urgent=False)
                        send_messages.append(message_temp)
                        MESSAGE_BATCH_SIZE += 1
                else:
                    # 单个传感器值消息
                    message_temp = mouse_cage[0].message
                    message_temp['port'] = port
                    send_thread.add_message(message=message_temp, urgent=False)
                    send_messages.append(message_temp)
                    MESSAGE_BATCH_SIZE += 1
            pass
            # 等待从线程处理完当前批次
        logger.info(f"数据请求报文：一共{len(send_messages)}条报文！")
        # print(f"send_messages:{send_messages}")
        batch_complete_event.wait()
        batch_complete_event.clear()  # 重置事件
        logger.info(f"从线程已处理完上批消息，主线程继续发送下一批\n")


if __name__ == "__main__":
    q = multiprocessing.Queue()
    main(q)
