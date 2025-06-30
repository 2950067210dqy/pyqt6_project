"""
响应报文解析
"""
import struct
import time
from enum import Enum

from loguru import logger

from util.time_util import time_util


class Modbus_Slave_Ids(Enum):
    """
    远程地址大全
    """

    UFC = {
        "name": "UFC",
        "description": "气流控制模块",
        'address': 0x02,
        'int': int(0x02)
    }
    UGC = {
        "name": "UGC",
        "description": "二氧化碳含量模块",
        'address': 0x03,
        'int': int(0x03)
    }
    ZOS = {
        "name": "ZOS",
        "description": "氧气含量测量模块",
        'address': 0x04,
        'int': int(0x04)
    }
    ENM = {
        "name": "ENM",
        "description": "鼠笼环境监控模块",
        'address': 0x01,
        'int': int(0x01)
        # 每个鼠笼都有该模块，
        # 地址还要加上当前鼠笼号*16
        # 例如鼠笼1的鼠笼环境监控模块地址就是0x11
    }
    EM = {
        "name": "EM",
        "description": "进食监控模块",
        'address': 0x02,
        'int': int(0x02)
        # 每个鼠笼都有该模块，
        # 地址还要加上当前鼠笼号*16
        # 例如鼠笼1的鼠笼环境监控模块地址就是0x11
    }
    DWM = {
        "name": "DWM",
        "description": "饮水监控模块",
        'address': 0x03,
        'int': int(0x03)
        # 每个鼠笼都有该模块，
        # 地址还要加上当前鼠笼号*16
        # 例如鼠笼1的鼠笼环境监控模块地址就是0x11
    }
    WM = {
        "name": "WM",
        "description": "称重模块",
        'address': 0x04,
        'int': int(0x04)
        # 每个鼠笼都有该模块，
        # 地址还要加上当前鼠笼号*16
        # 例如鼠笼1的鼠笼环境监控模块地址就是0x11
    }


class Modbus_Slave_Type(Enum):
    Not_Each_Mouse_Cage = [
        Modbus_Slave_Ids.UFC, Modbus_Slave_Ids.UGC, Modbus_Slave_Ids.ZOS
    ]
    Each_Mouse_Cage = [
        Modbus_Slave_Ids.ENM, Modbus_Slave_Ids.EM, Modbus_Slave_Ids.DWM, Modbus_Slave_Ids.WM
    ]


class Modbus_Response_Diffent_Type():
    """
    在寻找到Not_Each_Mouse_Cage与Each_Mouse_Cage不同类别的传感器的类
    """

    def __init__(self, name, slave_id, response,
                 response_hex, function_code, update_status_main_signal):
        # 更新状态text框
        self.update_status_main_signal = update_status_main_signal
        self.name = name
        self.slave_id = slave_id
        self.response = response
        self.response_hex = response_hex
        self.function_code = function_code
        self.specific_response = None
        self.init_modbus()

    def init_modbus(self):
        """
        根据传感器名称实例化具体的那个传感器的解析类
        :return:
        """
        if self.name == Modbus_Slave_Ids.UFC.value['name']:
            print("Modbus_Response_URC")
            self.specific_response = Modbus_Response_URC(
                slave_id=self.slave_id,
                response=self.response,
                response_hex=self.response_hex,
                function_code=self.function_code,
                update_status_main_signal=self.update_status_main_signal)
            pass
        elif self.name == Modbus_Slave_Ids.UGC.value['name']:
            pass
        else:
            pass

    pass


class Modbus_Response_Parents():
    def __init__(self, slave_id, response,
                 response_hex, function_code):
        self.slave_id = slave_id
        self.response = response
        self.response_hex = response_hex
        self.function_code = function_code

        self.pack_struct_slave_id_and_function_code = "> B B "
        self.pack_struct_crc = " B B"
        self.response_struct = {
            "slave_id": 0,
            "function_code": 0,
            "return_bytes_nums": 0,
            "data": list(),
            "crc": [0, 0]
        }

        pass

    def parser_response_pack(self, pack_struct, struct_type):
        """
        :param pack_struct: example: self.pack_struct_slave_id_and_function_code + pack_struct + self.pack_struct_crc= '> B B B B B B B'
        :return:
        """
        response_unpack = struct.unpack(
            self.pack_struct_slave_id_and_function_code + pack_struct + self.pack_struct_crc, self.response)
        logger.info(f"响应报文{self.response}-{self.response_hex}-解析结构:{response_unpack}")
        self.response_struct['slave_id'] = response_unpack[0]
        self.response_struct['function_code'] = response_unpack[1]
        self.response_struct['return_bytes_nums'] = response_unpack[2]
        self.response_struct['crc'] = [response_unpack[-2], response_unpack[-1]]
        """
        给的数据位数和我们整个数据解析的个数对不对
        """
        # if len(response_unpack) != 5 + int(self.response_struct['return_bytes_nums']):
        #     logger.error(
        #         f"响应报文{self.response}-{self.response_hex}的数据位数{5 + int(self.response_struct['return_bytes_nums'])}和解析的总位数{len(response_unpack)}不一致！")
        #     return
        if struct_type == "B":
            for i in range(int(self.response_struct['return_bytes_nums'])):
                self.response_struct['data'].append(response_unpack[3 + i])
        else:
            for i in range(int(self.response_struct['return_bytes_nums']) // 2):
                self.response_struct['data'].append(response_unpack[3 + i])

    def int_to_8bit_binary(self, num_list):
        """
        将多个数字转换成多个8位二进制
        :param num:
        :return:
        """
        binary_str_list = []
        # 确保输入是一个整数
        for num in num_list:
            if not isinstance(num, int):
                raise ValueError("Input must be an integer")

            # 处理负数，使用补码表示：将数值加上256（2^8）
            if num < 0:
                num = (1 << 8) + num  # 256 + num

            # 将整数转换为二进制字符串，并填充为8位
            binary_str = bin(num & 0xFF)[2:].zfill(8)
            binary_str_list.append(binary_str)
        return binary_str_list

    def function_code_parser(self):
        pass


class Modbus_Response_URC(Modbus_Response_Parents):
    def __init__(self, slave_id, response,
                 response_hex, function_code, update_status_main_signal):
        super().__init__(slave_id, response,
                         response_hex, function_code)
        self.type = Modbus_Slave_Ids.UFC
        self.update_status_main_signal = update_status_main_signal

    def function_code_parser(self):
        if isinstance(self.function_code, str):
            function_code = int(self.function_code, 16)
        else:
            function_code = self.function_code
        logger.info(f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析功能码：{self.function_code}")
        match function_code:
            case 1:
                self.parser_function_code_1()
                pass
            case 2:
                self.parser_function_code_2()
            case 3:
                self.parser_function_code_3()
            case 4:
                self.parser_function_code_4()
            case 5:
                self.parser_function_code_5()
            case 6:
                self.parser_function_code_6()
            case 7:
                self.parser_function_code_7()
            case _:
                self.parser_function_code_others()
                pass

    def parser_function_code_others(self):
        self.update_status_main_signal.emit(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-无法解析功能码：{self.function_code}")
        pass

    def parser_function_code_1(self):
        function_desc = """
        读输出端口状态信息
        参数长度：3
        """
        pack_struct = "B B B"
        self.parser_response_pack(pack_struct, struct_type="B")
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        data_binary_str_list = self.int_to_8bit_binary(num_list=self.response_struct['data'])
        data_binary_str_list_all = "".join(data_binary_str_list)
        return_datas = []
        port_types = ['参考气', '输出阀', '鼠笼0的电磁阀', '鼠笼1的电磁阀', '鼠笼2的电磁阀', '鼠笼3的电磁阀', '鼠笼4的电磁阀', '鼠笼5的电磁阀', '鼠笼6的电磁阀',
                      '鼠笼7的电磁阀']
        index = 0
        for str_single in data_binary_str_list_all:
            if index >= 6:
                return_datas.append({
                    "desc": port_types[index - 6],
                    'value': int(str_single)
                }
                )
            index += 1

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}输出端口状态：{'正常' if return_data['value'] == 1 else '故障'} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")

    pass

    def parser_function_code_2(self):
        function_desc = """
                读传感器状态信息
                参数长度：2
                """
        pack_struct = "B B"
        self.parser_response_pack(pack_struct, struct_type="B")
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        data_binary_str = self.int_to_8bit_binary(num_list=self.response_struct['data'])[0]
        return_datas = []
        sensor_types = ['流量', '差压', '气压1', '气压2', '备用1', '备用2']
        index = 0
        for str_single in data_binary_str:
            if index >= 2:
                return_datas.append({
                    "desc": sensor_types[index - 2],
                    'value': int(str_single)
                }
                )
            index += 1

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}传感器状态：{'正常' if return_data['value'] == 1 else '故障'} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass

    def parser_function_code_3(self):
        function_desc = """
                        读配置寄存器
                        参数长度：7
                        """
        pack_struct = "B H H H"
        self.parser_response_pack(pack_struct, struct_type="H")
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['流量计配置流量', '调节阀1开度', '调节阀2开度']
        index = 0
        for data_single in self.response_struct['data']:
            return_datas.append({
                "desc": port_types[index],
                'value': int(data_single)
            }
            )
            index += 1
        return_data_str = ""
        index = 0
        for return_data in return_datas:
            match index:
                case 0:
                    return_data_str += f"{return_data['desc']}:{'0~10L/min' if return_data['value'] == 1 else '0~3L/min'} | "
                    pass
                case 1:
                    return_data_str += f"{return_data['desc']}:{return_data['value']}% | "
                    pass
                case 2:
                    return_data_str += f"{return_data['desc']}:{return_data['value']}% | "
                    pass
                case _:
                    pass

            index += 1
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass

    def parser_function_code_4(self):

        pass

    def parser_function_code_5(self):
        pass

    def parser_function_code_6(self):
        pass

    def parser_function_code_7(self):
        pass


class Modbus_Response_Parser():
    """
响应报文解析
    """

    def __init__(self, slave_id, function_code, response, response_hex, update_status_main_signal):
        """

        :param slave_id: 地址码
        :param function_code: 功能码
        :param response: 响应报文
        :param response_hex: 响应报文16进制
        """
        self.update_status_main_signal = update_status_main_signal
        self.slave_id = slave_id
        self.function_code = function_code
        self.response = response
        self.response_hex = response_hex

        self.response_parser: Modbus_Response_Diffent_Type = None
        self.init_self()
        pass

    def init_self(self):
        self.response_parser = self.get_reponse_parser()

    def parser(self):
        self.response_parser.specific_response.function_code_parser()

    def get_reponse_parser(self):
        """
        因为鼠笼传感器的基准与前面几个传感器的基准一致，所以需要根据前面第三位来辨别。
        :return:
        """
        response_parser = None
        slave_id_int = int(self.slave_id, 16)
        # print(f"slave_id_int:{slave_id_int}")
        if slave_id_int > 16:
            # 鼠笼内传感器
            for type in Modbus_Slave_Type.Each_Mouse_Cage.value:
                if type.value['int'] == (slave_id_int % 16):
                    mouse_cage_number = slave_id_int // 16
                    logger.info(f"type.value['name'] Each:{type.value['name']}|mouse_cage_number:{mouse_cage_number}")
                    break
            pass
        else:
            # 非鼠笼内传感器
            for type in Modbus_Slave_Type.Not_Each_Mouse_Cage.value:
                if type.value['int'] == (slave_id_int % 16):
                    logger.info(f"type.value['name'] Not_Each:{type.value['name']}")
                    response_parser = Modbus_Response_Diffent_Type(name=type.value['name'],
                                                                   slave_id=self.slave_id,
                                                                   response=self.response,
                                                                   response_hex=self.response_hex,
                                                                   function_code=self.function_code,
                                                                   update_status_main_signal=self.update_status_main_signal)
                    break
            pass
        return response_parser
        pass
