import threading

import serial
import struct
import time

from PyQt6.QtCore import pyqtSignal
from loguru import logger

from Modbus.Modbus_Response_Parser import Modbus_Response_Parser
from config.global_setting import global_setting
from util.time_util import time_util


class ModbusRTUMaster:
    # 初始化后代表着连接串口，只有当close以后才会释放
    def __init__(self, port='COM1', timeout=1, update_status_main_signal=None,
                 ):
        # 可修改参数
        self.sport = port  # 这里是随便写的，要配合前端选框来
        self.timeout = timeout  # 可能需要修改
        # 获取主线程更新界面信号
        self.update_status_main_signal: pyqtSignal = update_status_main_signal

        self.ser = None

    def close(self):
        self.ser.close()

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
            data_bytes = [int(x, 16) for x in data_hex_list]
            # logger.info(f"data_hex_list: {data_hex_list}|data_bytes: {data_bytes}")
            # 组装帧
            frame = struct.pack('>B B B B B B', slave_id, function_code, *data_bytes)
            crc = self.calculate_crc(frame)
            str_frame = frame.hex()
            str_crc = crc.hex()
            logger.info(f"frame: {frame} , {str_frame}|crc: {crc} , {str_crc}")
            return frame + crc
        except Exception as e:
            self.update_status_main_signal.emit(f"构造报文出错: {e}")
            logger.error(f"{time_util.get_format_from_time(time.time())}-{self.sport}-构造报文出错: {e}")
            return None

    def send_command(self, slave_id, function_code, data_hex_list, is_parse_response=True):
        """
        发送Modbus RTU命令帧，接收并解析响应。
        :param data_hex_list ['00','00','00','00'] 16进制
        :param is_parse_response 是否解析响应报文 默认解析
        :return: (response_hex: str, success: bool)
        """
        try:

            self.ser = serial.Serial(
                port=self.sport,
                baudrate=115200,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=self.timeout
            )
            if self.update_status_main_signal is not None:
                self.update_status_main_signal.emit(
                    f"{time_util.get_format_from_time(time.time())}-{self.sport}-连接成功")
            logger.info(f"{self.sport}-连接成功")
            frame = self.build_frame(slave_id, function_code, data_hex_list)
            if self.update_status_main_signal is not None:
                self.update_status_main_signal.emit(
                    f"{time_util.get_format_from_time(time.time())}-{self.sport}-发送数据帧{frame.hex()}")
            logger.info(f"{time_util.get_format_from_time(time.time())}-{self.sport}-发送数据帧{frame.hex()}")
            try:

                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                self.ser.write(frame)

            except Exception as e:
                logger.error(e)
            time.sleep(float(global_setting.get_setting('monitor_data')['SEND']['get_response_delay']))

            response = self.ser.read(256)
            # self.update_status_main_signal.emit(
            #     f"{time_util.get_format_from_time(time.time())}-{self.sport}-收到消息-{response.hex()}")
            # 超时判断
            if not response:
                if self.update_status_main_signal is not None:
                    self.update_status_main_signal.emit(
                        f"{time_util.get_format_from_time(time.time())}-{self.sport}-Time OUT1-未获取到响应数据")
                logger.error(f"{time_util.get_format_from_time(time.time())}-{self.sport}-Time OUT1-未获取到响应数据")
                if self.ser is not None and self.ser.is_open:  # 确保关闭连接
                    logger.error("关闭连接")
                    self.ser.close()
                    self.ser = None
                return None, None, False

            # 数据错误
            if len(response) < 5:
                if self.update_status_main_signal is not None:
                    self.update_status_main_signal.emit(
                        f"{time_util.get_format_from_time(time.time())}-{self.sport}-Time OUT2-返回数据位数错误")
                logger.error(f"{time_util.get_format_from_time(time.time())}-{self.sport}-Time OUT2-返回数据位数错误")
                if self.ser is not None and self.ser.is_open:  # 确保关闭连接
                    self.ser.close()
                    self.ser = None
                return response, response.hex(), False

            data_part = response[:-2]
            crc_received = response[-2:]
            crc_expected = self.calculate_crc(data_part)

            # 数据错误，CRC验证失败
            if crc_received != crc_expected:
                if self.update_status_main_signal is not None:
                    self.update_status_main_signal.emit(
                        f"{time_util.get_format_from_time(time.time())}-{self.sport}-Time OUT3-数据错误，CRC验证失败")
                logger.error(f"{time_util.get_format_from_time(time.time())}-{self.sport}-Time OUT3-数据错误，CRC验证失败")
                if self.ser is not None and self.ser.is_open:  # 确保关闭连接
                    self.ser.close()
                    self.ser = None
                return response, response.hex(), False

            # 检查是否是异常响应
            function_code = response[1]
            if function_code & 0x80:
                exception_code = response[2]
                if self.update_status_main_signal is not None:
                    self.update_status_main_signal.emit(
                        f"{time_util.get_format_from_time(time.time())}-{self.sport}-异常：功能码=0x{function_code:02X}, 异常码=0x{exception_code:02X}")
                logger.error(
                    f"{time_util.get_format_from_time(time.time())}-{self.sport}-异常：功能码=0x{function_code:02X}, 异常码=0x{exception_code:02X}")
                if self.ser is not None and self.ser.is_open:  # 确保关闭连接
                    self.ser.close()
                    self.ser = None
                return response, response.hex(), False
            if self.update_status_main_signal is not None:
                self.update_status_main_signal.emit(
                    f"{time_util.get_format_from_time(time.time())}-{self.sport}-CRC校验通过，正常响应")
            logger.info(f"{time_util.get_format_from_time(time.time())}-{self.sport}-CRC校验通过，正常响应")
            if self.update_status_main_signal is not None:
                self.update_status_main_signal.emit(
                    f"{time_util.get_format_from_time(time.time())}-{self.sport}-收到响应消息-{response.hex()}-数据部分{data_part.hex()}")
            if self.ser is not None and self.ser.is_open:  # 确保关闭连接
                self.ser.close()
                self.ser = None
            """
            解析响应报文
            """
            if is_parse_response:
                self.parse_response(response=response, response_hex=response.hex(), send_state=True, slave_id=slave_id,
                                    function_code=function_code)
            return response, response.hex(), True

        except Exception as e:
            if self.update_status_main_signal is not None:
                self.update_status_main_signal.emit(
                    f"{time_util.get_format_from_time(time.time())}-{self.sport}-❗ 串口通信异常: {e}")
            logger.error(f"❗ 串口通信异常: {e}")
            if self.ser is not None and self.ser.is_open:  # 确保关闭连接
                self.ser.close()
                self.ser = None
            return None, None, False

    def parse_response(self, response, response_hex, send_state, slave_id, function_code):
        # 响应报文是正确的，即发送状态时正确的 进行解析响应报文
        logger.info(f"response-{response}|response_hex-{response_hex}|send_state-{send_state}")
        if send_state:
            logger.info("开始解析报文")
            modbus_response_parser = Modbus_Response_Parser(slave_id=slave_id,
                                                            function_code=function_code, response=response,
                                                            response_hex=response_hex,

                                                            )
            return modbus_response_parser.parser()
        return None, None
