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

        self.response_parser: Modbus_Response_Diffent_Type_Each_Mouse_Cage | Modbus_Response_Diffent_Type_Not_Each_Mouse_Cage = None
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
                    response_parser = Modbus_Response_Diffent_Type_Each_Mouse_Cage(name=type.value['name'],
                                                                                   origin_slave_id=self.slave_id,
                                                                                   mouse_cage_number=mouse_cage_number,
                                                                                   slave_id=f"{(slave_id_int % 16):02X}",
                                                                                   response=self.response,
                                                                                   response_hex=self.response_hex,
                                                                                   function_code=self.function_code,
                                                                                   update_status_main_signal=self.update_status_main_signal)
                    break
            pass
        else:
            # 非鼠笼内传感器
            for type in Modbus_Slave_Type.Not_Each_Mouse_Cage.value:
                if type.value['int'] == (slave_id_int % 16):
                    logger.info(f"type.value['name'] Not_Each:{type.value['name']}")
                    response_parser = Modbus_Response_Diffent_Type_Not_Each_Mouse_Cage(name=type.value['name'],
                                                                                       slave_id=self.slave_id,
                                                                                       response=self.response,
                                                                                       response_hex=self.response_hex,
                                                                                       function_code=self.function_code,
                                                                                       update_status_main_signal=self.update_status_main_signal)
                    break
            pass
        return response_parser
        pass


class Modbus_Response_Diffent_Type_Each_Mouse_Cage():
    """
    在寻找到Each_Mouse_Cage不同类别的传感器的类
    """

    def __init__(self, name, origin_slave_id, mouse_cage_number, slave_id, response,
                 response_hex, function_code, update_status_main_signal):
        # 更新状态text框
        self.update_status_main_signal = update_status_main_signal
        self.name = name
        self.origin_slave_id = origin_slave_id
        self.mouse_cage_number = mouse_cage_number

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
        if self.name == Modbus_Slave_Ids.ENM.value['name']:

            self.specific_response = Modbus_Response_ENM(
                origin_slave_id=self.origin_slave_id,
                mouse_cage_number=self.mouse_cage_number,
                slave_id=self.slave_id,
                response=self.response,
                response_hex=self.response_hex,
                function_code=self.function_code,
                update_status_main_signal=self.update_status_main_signal)
            pass
        elif self.name == Modbus_Slave_Ids.EM.value['name']:
            self.specific_response = Modbus_Response_EM(
                origin_slave_id=self.origin_slave_id,
                mouse_cage_number=self.mouse_cage_number,
                slave_id=self.slave_id,
                response=self.response,
                response_hex=self.response_hex,
                function_code=self.function_code,
                update_status_main_signal=self.update_status_main_signal)
            pass
            pass
        elif self.name == Modbus_Slave_Ids.DWM.value['name']:
            self.specific_response = Modbus_Response_DWM(
                origin_slave_id=self.origin_slave_id,
                mouse_cage_number=self.mouse_cage_number,
                slave_id=self.slave_id,
                response=self.response,
                response_hex=self.response_hex,
                function_code=self.function_code,
                update_status_main_signal=self.update_status_main_signal)
            pass
            pass
        elif self.name == Modbus_Slave_Ids.WM.value['name']:
            self.specific_response = Modbus_Response_WM(
                origin_slave_id=self.origin_slave_id,
                mouse_cage_number=self.mouse_cage_number,
                slave_id=self.slave_id,
                response=self.response,
                response_hex=self.response_hex,
                function_code=self.function_code,
                update_status_main_signal=self.update_status_main_signal)
            pass
            pass
        else:
            pass

    pass


class Modbus_Response_Diffent_Type_Not_Each_Mouse_Cage():
    """
    在寻找到Not_Each_Mouse_Cage不同类别的传感器的类
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

            self.specific_response = Modbus_Response_URC(
                slave_id=self.slave_id,
                response=self.response,
                response_hex=self.response_hex,
                function_code=self.function_code,
                update_status_main_signal=self.update_status_main_signal)
            pass
        elif self.name == Modbus_Slave_Ids.UGC.value['name']:
            self.specific_response = Modbus_Response_UGC(
                slave_id=self.slave_id,
                response=self.response,
                response_hex=self.response_hex,
                function_code=self.function_code,
                update_status_main_signal=self.update_status_main_signal)
            pass
            pass
        elif self.name == Modbus_Slave_Ids.ZOS.value['name']:
            self.specific_response = Modbus_Response_ZOS(
                slave_id=self.slave_id,
                response=self.response,
                response_hex=self.response_hex,
                function_code=self.function_code,
                update_status_main_signal=self.update_status_main_signal)
            pass
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

    def parser_response_pack(self, pack_struct, struct_type, is_pack_return_bytes_nums):
        """
        :param pack_struct: example: self.pack_struct_slave_id_and_function_code + pack_struct + self.pack_struct_crc= '> B B B B B B B'
        :return:
        """
        response_unpack = struct.unpack(
            self.pack_struct_slave_id_and_function_code + pack_struct + self.pack_struct_crc, self.response)
        logger.info(f"响应报文{self.response}-{self.response_hex}-解析结构:{response_unpack}")
        self.response_struct['slave_id'] = response_unpack[0]
        # 返回字节数 :有时候响应报文会不带返回字节数，这时候改变数据比特的index,并且不unpack return_bytes_nums,这时候使用直接计算data长度充当return_bytes_nums
        if is_pack_return_bytes_nums:
            data_start_index = 3
            self.response_struct['return_bytes_nums'] = response_unpack[2]
            pass
        else:
            data_start_index = 2
            # 减去slave_id,function_code 和crc2位
            self.response_struct['return_bytes_nums'] = len(response_unpack) - 4
            pass
        self.response_struct['function_code'] = response_unpack[1]

        self.response_struct['crc'] = [response_unpack[-2], response_unpack[-1]]
        """
        给的数据位数和我们整个数据解析的个数对不对
        """
        # if len(response_unpack) != 5 + int(self.response_struct['return_bytes_nums']):
        #     logger.error(
        #         f"响应报文{self.response}-{self.response_hex}的数据位数{5 + int(self.response_struct['return_bytes_nums'])}和解析的总位数{len(response_unpack)}不一致！")
        #     return
        if isinstance(struct_type, str) and struct_type.upper() == "B":
            for i in range(int(self.response_struct['return_bytes_nums'])):
                self.response_struct['data'].append(response_unpack[data_start_index + i])
        else:
            for i in range(int(self.response_struct['return_bytes_nums']) // 2):
                self.response_struct['data'].append(response_unpack[data_start_index + i])

    def get_signed_int(self, bin_str):
        """
        根据8位二进制数获得有符号的整数
        :return:
        """
        # 确保 bin_str 是 8 位二进制数
        if len(bin_str) != 8 or not all(bit in '01' for bit in bin_str):
            raise ValueError("输入必须是一个8位二进制字符串")

        # 先将其转换为无符号整数
        unsigned_int = int(bin_str, 2)

        # 如果最高位是 1，则说明它是负数，计算补码
        if unsigned_int >= 128:  # 对于8位补码，数字 >= 128 是负数
            signed_int = unsigned_int - 256  # 转换为负数
        else:
            signed_int = unsigned_int

        return signed_int

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


class Modbus_Response_ENM(Modbus_Response_Parents):
    def __init__(self, origin_slave_id,
                 mouse_cage_number,
                 slave_id,
                 response,
                 response_hex,
                 function_code,
                 update_status_main_signal):
        super().__init__(slave_id, response,
                         response_hex, function_code)
        self.origin_slave_id = origin_slave_id
        self.mouse_cage_number = mouse_cage_number
        self.type = Modbus_Slave_Ids.ENM
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

            case 17:
                self.parser_function_code_17()

            case _:
                self.parser_function_code_others()

                pass

    pass
    """
    11 01 X
    """

    def parser_function_code_1(self):
        function_desc = """
                       读输出端口状态信息
                       参数长度：2
                       """
        pack_struct = "B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        data_binary_str_list = self.int_to_8bit_binary(num_list=self.response_struct['data'])
        data_binary_str_list_all = "".join(data_binary_str_list)
        return_datas = []
        port_types = ['跑轮刹车', '光照控制']
        index = 0
        for str_single in data_binary_str_list_all:
            if index == 6:
                return_datas.append({
                    "desc": port_types[index - 6],
                    'value': '已刹车' if int(str_single) == 1 else '未刹车'
                }
                )
            if index == 7:
                return_datas.append({
                    "desc": port_types[index - 6],
                    'value': '已开灯' if int(str_single) == 1 else '未开灯'
                }
                )
            index += 1

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}状态：{return_data['value']} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-鼠笼{self.mouse_cage_number}-{function_desc}-{return_data_str}")
        return return_datas
        pass

    """
        11 02 X
        """

    def parser_function_code_2(self):
        function_desc = """
                               读输出端口状态信息
                               参数长度：2
                               """
        pack_struct = "B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        data_binary_str_list = self.int_to_8bit_binary(num_list=self.response_struct['data'])
        data_binary_str_list_all = "".join(data_binary_str_list)
        return_datas = []
        port_types = ['湿度传感器状态', '气压传感器状态', '噪声传感器状态']

        index = 0
        for str_single in data_binary_str_list_all:
            if index >= 5:
                return_datas.append({
                    "desc": port_types[index - 5],
                    'value': int(str_single)
                }
                )
            index += 1

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}状态：{'正常' if return_data['value'] == 1 else '故障'} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-鼠笼{self.mouse_cage_number}-{function_desc}-{return_data_str}")
        return return_datas
        pass
        pass

    """
        11 03 X
        """

    def parser_function_code_3(self):
        function_desc = """
                       读配置寄存器
                       参数长度：7
                      """
        pack_struct = "B H H H"
        self.parser_response_pack(pack_struct, struct_type="H", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['光照亮度', '光照色温', '模块地址']
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
            if index == 2:
                return_data_str += f"{return_data['desc']}:0x{return_data['value']:04X} | "
            else:
                return_data_str += f"{return_data['desc']}:{return_data['value']} | "
            index += 1
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-鼠笼{self.mouse_cage_number}-{function_desc}-{return_data_str}")
        pass

        return return_datas
        pass

    """
        11 04 X
        """

    def parser_function_code_4(self):
        function_desc = """
                                       读传感器测量值
                                       参数长度：13
                                        """
        pack_struct = "B " * 13
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['温度测量值(℃)', '湿度测量值(%RH)', '噪声测量值(dB)', '大气压测量值(KPa)', '当前计量周期内跑轮圈数测量值']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.get_signed_int(
                                "".join(self.int_to_8bit_binary([self.response_struct['data'][i - 1]]))
                                )) + "." + str(
                                self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                case 3:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 5:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 8:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(int("".join(self.int_to_8bit_binary(
                                num_list=[self.response_struct['data'][i - 2], self.response_struct['data'][i - 1]])),
                                2)) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 11:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(int("".join(self.int_to_8bit_binary(
                                num_list=[self.response_struct['data'][i - 2], self.response_struct['data'][i - 1]])),
                                2)) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case _:
                    pass
        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-鼠笼{self.mouse_cage_number}-{function_desc}-{return_data_str}")
        pass
        return return_datas
        pass

    """
        11 05 X
        """

    def parser_function_code_5(self):
        pass

    """
        11 06 X
        """

    def parser_function_code_6(self):
        pass

    """
        11 11 X
        """

    def parser_function_code_17(self):
        pass

    def parser_function_code_others(self):
        pass


class Modbus_Response_EM(Modbus_Response_Parents):
    def __init__(self, origin_slave_id,
                 mouse_cage_number,
                 slave_id,
                 response,
                 response_hex,
                 function_code,
                 update_status_main_signal):
        super().__init__(slave_id, response,
                         response_hex, function_code)
        self.origin_slave_id = origin_slave_id
        self.mouse_cage_number = mouse_cage_number
        self.type = Modbus_Slave_Ids.EM
        self.update_status_main_signal = update_status_main_signal

    def function_code_parser(self):
        if isinstance(self.function_code, str):
            function_code = int(self.function_code, 16)
        else:
            function_code = self.function_code
        logger.info(f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析功能码：{self.function_code}")
        match function_code:

            case 2:
                self.parser_function_code_2()
            case 4:
                self.parser_function_code_4()

            case 17:
                self.parser_function_code_17()

            case _:
                self.parser_function_code_others()

                pass

    pass


class Modbus_Response_DWM(Modbus_Response_Parents):
    def __init__(self, origin_slave_id,
                 mouse_cage_number,
                 slave_id,
                 response,
                 response_hex,
                 function_code,
                 update_status_main_signal):
        super().__init__(slave_id, response,
                         response_hex, function_code)
        self.origin_slave_id = origin_slave_id
        self.mouse_cage_number = mouse_cage_number
        self.type = Modbus_Slave_Ids.DWM
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
            case 4:
                self.parser_function_code_4()

            case 5:
                self.parser_function_code_5()

            case 17:
                self.parser_function_code_17()

            case _:
                self.parser_function_code_others()

                pass

    pass
    pass


class Modbus_Response_WM(Modbus_Response_Parents):
    def __init__(self, origin_slave_id,
                 mouse_cage_number,
                 slave_id,
                 response,
                 response_hex,
                 function_code,
                 update_status_main_signal):
        super().__init__(slave_id, response,
                         response_hex, function_code)
        self.origin_slave_id = origin_slave_id
        self.mouse_cage_number = mouse_cage_number
        self.type = Modbus_Slave_Ids.WM
        self.update_status_main_signal = update_status_main_signal

    def function_code_parser(self):
        if isinstance(self.function_code, str):
            function_code = int(self.function_code, 16)
        else:
            function_code = self.function_code
        logger.info(f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析功能码：{self.function_code}")
        match function_code:
            case 2:
                self.parser_function_code_2()

            case 4:
                self.parser_function_code_4()
            case 17:
                self.parser_function_code_17()

            case _:
                self.parser_function_code_others()

                pass

    pass
    pass


class Modbus_Response_ZOS(Modbus_Response_Parents):
    def __init__(self, slave_id, response,
                 response_hex, function_code, update_status_main_signal):
        super().__init__(slave_id, response,
                         response_hex, function_code)
        self.type = Modbus_Slave_Ids.ZOS
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

            case 17:
                self.parser_function_code_17()

            case _:
                self.parser_function_code_others()

                pass

    """
           04 01 X
           """

    def parser_function_code_1(self):
        function_desc = """
               读输出端口状态信息
               参数长度：2
               """
        pack_struct = "B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        data_binary_str_list = self.int_to_8bit_binary(num_list=self.response_struct['data'])
        data_binary_str_list_all = "".join(data_binary_str_list)
        return_datas = []
        port_types = ['继电器：控制氧传感器通断电']
        index = 0
        for str_single in data_binary_str_list_all:
            if index == 7:
                return_datas.append({
                    "desc": port_types[index - 7],
                    'value': int(str_single)
                }
                )
            index += 1

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}状态：{'ON' if return_data['value'] == 1 else 'OFF'} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        return return_datas
        pass

    """
               04 02 X
               """

    def parser_function_code_2(self):
        function_desc = """
                       读输出端口状态信息
                       参数长度：2
                       """
        pack_struct = "B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        data_binary_str_list = self.int_to_8bit_binary(num_list=self.response_struct['data'])
        data_binary_str_list_all = "".join(data_binary_str_list)
        return_datas = []
        port_types = ['氧传感器状态', '温度传感器状态']

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
            return_data_str += f"{return_data['desc']}状态：{'ON' if return_data['value'] == 1 else 'OFF'} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        return return_datas
        pass
        pass

    """
               04 03 X
               """

    def parser_function_code_3(self):
        function_desc = """
                读配置寄存器
                参数长度：3
               """
        pack_struct = "B H"
        self.parser_response_pack(pack_struct, struct_type="H", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['氧传感器配置（预留）']
        index = 0
        for data_single in self.response_struct['data']:
            return_datas.append({
                "desc": port_types[index],
                'value': int(data_single)
            }
            )
            index += 1
        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass

        return return_datas
        pass

    """
               04 04 X
               """

    def parser_function_code_4(self):
        function_desc = """
                               读传感器测量值
                               参数长度：5
                                """
        pack_struct = "B " * 5
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['氧传感器测量值(%)', '温度传感器测量值(℃)']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                case 3:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': int("".join(self.int_to_8bit_binary(
                            num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)
                    }
                    )
                    j += 1
                    pass

                case _:
                    pass
        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas
        pass

    """
               04 05 X
               """

    def parser_function_code_5(self):
        function_desc = """
                              写从机单个开关量输出（ON/OFF）
                              参数长度：4
                              """
        pack_struct = "B B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=False)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['氧传感器起始地址值', '氧传感器开、关控制']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                    }
                    )
                    j += 1
                    pass
                case 2:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': "ON" if int(self.response_struct['data'][i]) == 255 else "OFF"
                    }
                    )
                    j += 1
                    pass
                case _:
                    pass

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} |"
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas

        pass

    """
               04 06 X
               """

    def parser_function_code_6(self):
        function_desc = """
                写单个保持寄存器
                参数长度：4
                                """
        pack_struct = "B B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=False)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types_0 = ['模块地址地址', '新分配的模块地址值']
        port_types_1 = ['寄存器地址', '氧传感器设置（预留）']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    match self.response_struct['data'][i]:
                        case 0:
                            return_datas.append({
                                "desc": port_types_0[j],
                                'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                            }
                            )
                            pass
                        case 1:
                            return_datas.append({
                                "desc": port_types_1[j],
                                'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                            }
                            )
                            pass

                        case _:
                            pass
                    j += 1
                    pass
                case 3:
                    match self.response_struct['data'][1]:
                        case 0:
                            return_datas.append({
                                "desc": port_types_0[j],
                                'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                            }
                            )
                            pass
                        case 1:
                            return_datas.append({
                                "desc": port_types_1[j],
                                'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                            }
                            )
                            pass

                        case _:
                            pass
                    j += 1
                    pass
                case _:
                    pass

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} |"
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas

    """
               04 11 X
               """

    def parser_function_code_17(self):
        function_desc = """
                                       读取模块ID信息等
                                       参数长度：17
                                       """
        pack_struct = "B H H H H H H H H"
        self.parser_response_pack(pack_struct, struct_type="H", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['生产厂商', '硬件版本', '软件版本', '出厂地址', '当前地址', '预留1', '预留2', '预留3']
        index = 0
        for data_single in self.response_struct['data']:
            return_datas.append({
                "desc": port_types[index],
                'value': f"{data_single:016b}"
            }
            )
            index += 1
        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas
        pass

    def parser_function_code_others(self):
        self.update_status_main_signal.emit(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-无法解析功能码：{self.function_code}")
        pass


class Modbus_Response_UGC(Modbus_Response_Parents):
    def __init__(self, slave_id, response,
                 response_hex, function_code, update_status_main_signal):
        super().__init__(slave_id, response,
                         response_hex, function_code)
        self.type = Modbus_Slave_Ids.UGC
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

            case 17:
                self.parser_function_code_17()

            case _:
                self.parser_function_code_others()

                pass

    """
           03 01 X
           """

    def parser_function_code_1(self):
        function_desc = """
               读输出端口状态信息
               参数长度：3
               """
        pack_struct = "B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        data_binary_str_list = self.int_to_8bit_binary(num_list=self.response_struct['data'])
        data_binary_str_list_all = "".join(data_binary_str_list)
        return_datas = []
        port_types = ['预留7', '预留6', '预留5', '预留4', '预留3', '预留2', '预留1', '调节阀4',
                      '调节阀3', '调节阀2', '调节阀1', '五选一阀5', '五选一阀4', '五选一阀3', '五选一阀2', '五选一阀1']
        index = 0
        for str_single in data_binary_str_list_all:
            return_datas.append({
                "desc": port_types[index],
                'value': int(str_single)
            }
            )
            index += 1

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}状态：{'ON' if return_data['value'] == 1 else 'OFF'} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        return return_datas
        pass

    """
               03 02 X
               """

    def parser_function_code_2(self):
        function_desc = """
                       读输出端口状态信息
                       参数长度：3
                       """
        pack_struct = "B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        data_binary_str_list = self.int_to_8bit_binary(num_list=self.response_struct['data'])
        data_binary_str_list_all = "".join(data_binary_str_list)
        return_datas = []
        port_types = ['预留7', '预留6', '预留5', '预留4', '预留3', '预留2', '预留1', 'CO2',
                      '气压2', '气压1', '湿度2', '湿度1', '温度2', '温度1', '流量2', '流量1']
        index = 0
        for str_single in data_binary_str_list_all:
            return_datas.append({
                "desc": port_types[index],
                'value': int(str_single)
            }
            )
            index += 1

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}状态：{'ON' if return_data['value'] == 1 else 'OFF'} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        return return_datas
        pass
        pass

    """
               03 03 X
               """

    def parser_function_code_3(self):
        function_desc = """
                读配置寄存器
                参数长度：9
               """
        pack_struct = "B H H H H"
        self.parser_response_pack(pack_struct, struct_type="H", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['调节阀1开度', '调节阀2开度', '调节阀3开度', '调节阀4开度']
        index = 0
        for data_single in self.response_struct['data']:
            return_datas.append({
                "desc": port_types[index],
                'value': int(data_single)
            }
            )
            index += 1
        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']}% | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass

        return return_datas
        pass

    """
               03 04 X
               """

    def parser_function_code_4(self):
        function_desc = """
                               读传感器测量值
                               参数长度：21
                                """
        pack_struct = "B " * 21
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['流量计1', '流量计2', '温度1(℃)', '温度2(℃)', '湿度1(%RH)', '湿度2(%RH)', '气压1(KPa)', '气压2(KPa)', 'CO2', '保留']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': int("".join(self.int_to_8bit_binary(
                            num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)
                    }
                    )
                    j += 1
                    pass
                case 3:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': int("".join(self.int_to_8bit_binary(
                            num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)
                    }
                    )
                    j += 1
                    pass
                case 5:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 7:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 9:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                    pass
                case 11:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 13:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 15:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 17:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 19:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case _:
                    pass
        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas
        pass

    """
               03 05 X
               """

    def parser_function_code_5(self):
        function_desc = """
                              写从机单个开关量输出（ON/OFF）
                              参数长度：4
                              """
        pack_struct = "B B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=False)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['电磁阀起始地址值', '电磁阀开、关控制']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                    }
                    )
                    j += 1
                    pass
                case 2:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': "ON" if int(self.response_struct['data'][i]) == 255 else "OFF"
                    }
                    )
                    j += 1
                    pass
                case _:
                    pass

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} |"
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas

        pass

    """
               03 06 X
               """

    def parser_function_code_6(self):
        function_desc = """
                       写单个保持寄存器
                       参数长度：4
                               """
        pack_struct = "B B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=False)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types_1 = ['寄存器地址', '调节阀1开度']
        port_types_2 = ['寄存器地址', '调节阀2开度']
        port_types_3 = ['寄存器地址', '调节阀3开度']
        port_types_4 = ['寄存器地址', '调节阀4开度']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    return_datas.append({
                        "desc": port_types_1[j],
                        'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                    })
                    j += 1
                    pass
                case 3:
                    match self.response_struct['data'][1]:
                        case 1:
                            return_datas.append({
                                "desc": port_types_1[j],
                                'value': f"{int(''.join(self.int_to_8bit_binary(num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)}%"
                            }
                            )
                            pass
                        case 2:
                            return_datas.append({
                                "desc": port_types_2[j],
                                'value': f"{int(''.join(self.int_to_8bit_binary(num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)}%"
                            }
                            )
                            pass
                        case 3:
                            return_datas.append({
                                "desc": port_types_3[j],
                                'value': f"{int(''.join(self.int_to_8bit_binary(num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)}%"
                            }
                            )
                            pass
                        case 4:
                            return_datas.append({
                                "desc": port_types_4[j],
                                'value': f"{int(''.join(self.int_to_8bit_binary(num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)}%"
                            }
                            )
                            pass
                        case _:
                            pass
                    j += 1
                    pass
                case _:
                    pass

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} |"
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas
        pass

    """
               03 11 X
               """

    def parser_function_code_17(self):
        function_desc = """
                                       读取模块ID信息等
                                       参数长度：17
                                       """
        pack_struct = "B H H H H H H H H"
        self.parser_response_pack(pack_struct, struct_type="H", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['生产厂商', '硬件版本', '软件版本', '出厂地址', '当前地址', '预留1', '预留2', '预留3']
        index = 0
        for data_single in self.response_struct['data']:
            return_datas.append({
                "desc": port_types[index],
                'value': f"{data_single:016b}"
            }
            )
            index += 1
        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas
        pass

    def parser_function_code_others(self):
        self.update_status_main_signal.emit(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-无法解析功能码：{self.function_code}")
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
            case 17:
                self.parser_function_code_17()
            case _:
                self.parser_function_code_others()
                pass

    def parser_function_code_others(self):
        self.update_status_main_signal.emit(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-无法解析功能码：{self.function_code}")
        pass

    """
        02 01 X
        """

    def parser_function_code_1(self):
        function_desc = """
        读输出端口状态信息
        参数长度：3
        """
        pack_struct = "B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
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
        return return_datas

    pass
    """
        02 02 X
        """

    def parser_function_code_2(self):
        function_desc = """
                读传感器状态信息
                参数长度：2
                """
        pack_struct = "B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
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
        return return_datas

    """
        02 03 X
        """

    def parser_function_code_3(self):
        function_desc = """
                        读配置寄存器
                        参数长度：7
                        """
        pack_struct = "B H H H"
        self.parser_response_pack(pack_struct, struct_type="H", is_pack_return_bytes_nums=True)
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

        return return_datas

    """
        02 04 X
        """

    def parser_function_code_4(self):
        function_desc = """
                        读传感器测量值
                        参数长度：13
                         """
        pack_struct = "B B B B B B B B B B B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['流量计测量值(sccm)', '差压计测量值(kPa)', '气压计1测量值(kPa)', '气压计2测量值(kPa)', '备用1测量值', '备用2测量值']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': int("".join(self.int_to_8bit_binary(
                            num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)
                    }
                    )
                    j += 1
                    pass
                case 3:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1] - 7) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 5:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 7:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                case 9:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                    pass
                case 11:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': float(
                            str(self.response_struct['data'][i - 1]) + "." + str(self.response_struct['data'][i]))
                    }
                    )
                    j += 1
                    pass
                    pass
                case _:
                    pass
        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas

    """
        02 05 X
        """

    def parser_function_code_5(self):
        function_desc = """
                       写从机单个开关量输出（ON/OFF）
                       参数长度：4
                       """
        pack_struct = "B B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=False)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['电磁阀起始地址值', '电磁阀开、关控制']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                    }
                    )
                    j += 1
                    pass
                case 2:
                    return_datas.append({
                        "desc": port_types[j],
                        'value': "ON" if int(self.response_struct['data'][i]) == 255 else "OFF"
                    }
                    )
                    j += 1
                    pass
                case _:
                    pass

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} |"
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas

    """
    02 06 X
    """

    def parser_function_code_6(self):
        function_desc = """
                            写单个保持寄存器
                            参数长度：4
                        """
        pack_struct = "B B B B"
        self.parser_response_pack(pack_struct, struct_type="B", is_pack_return_bytes_nums=False)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types_0 = ['模块地址地址', '新分配的模块地址值']
        port_types_1 = ['寄存器地址', '流量计测量范围']
        port_types_2 = ['寄存器地址', '调节阀1开度']
        port_types_3 = ['寄存器地址', '调节阀2开度']
        j = 0
        for i in range(len(self.response_struct['data'])):
            match i:
                case 1:
                    match self.response_struct['data'][i]:
                        case 0:
                            return_datas.append({
                                "desc": port_types_0[j],
                                'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                            }
                            )
                            pass
                        case 1:
                            return_datas.append({
                                "desc": port_types_1[j],
                                'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                            }
                            )
                            pass
                        case 2:
                            return_datas.append({
                                "desc": port_types_2[j],
                                'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                            }
                            )
                            pass
                        case 3:
                            return_datas.append({
                                "desc": port_types_3[j],
                                'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                            }
                            )
                            pass
                        case _:
                            pass
                    j += 1
                    pass
                case 3:
                    match self.response_struct['data'][1]:
                        case 0:
                            return_datas.append({
                                "desc": port_types_0[j],
                                'value': f"0X{self.response_struct['data'][i - 1]:02X}{self.response_struct['data'][i]:02X}"
                            }
                            )
                            pass
                        case 1:
                            return_datas.append({
                                "desc": port_types_1[j],
                                'value': '0~3L/min' if int("".join(self.int_to_8bit_binary(
                                    num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])),
                                    2) == 0 else '0-10L/min'
                            }
                            )
                            pass
                        case 2:
                            return_datas.append({
                                "desc": port_types_2[j],
                                'value': f"{int(''.join(self.int_to_8bit_binary(num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)}%"
                            }
                            )
                            pass
                        case 3:
                            return_datas.append({
                                "desc": port_types_3[j],
                                'value': f"{int(''.join(self.int_to_8bit_binary(num_list=[self.response_struct['data'][i - 1], self.response_struct['data'][i]])), 2)}%"
                            }
                            )
                            pass
                        case _:
                            pass
                    j += 1
                    pass
                case _:
                    pass

        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} |"
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas

    """
        02 11 X
    """

    def parser_function_code_17(self):
        function_desc = """
                                读取模块ID信息等
                                参数长度：17
                                """
        pack_struct = "B H H H H H H H H"
        self.parser_response_pack(pack_struct, struct_type="H", is_pack_return_bytes_nums=True)
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-开始解析报文：{self.response_hex}|{self.response_struct}")
        return_datas = []
        port_types = ['生产厂商', '硬件版本', '软件版本', '出厂地址', '当前地址', '预留1', '预留2', '预留3']
        index = 0
        for data_single in self.response_struct['data']:
            return_datas.append({
                "desc": port_types[index],
                'value': f"{data_single:016b}"
            }
            )
            index += 1
        return_data_str = ""
        for return_data in return_datas:
            return_data_str += f"{return_data['desc']}:{return_data['value']} | "
        logger.info(
            f"响应报文-{self.type.value['name']}-{self.type.value['description']}-解析成功：{function_desc}-{return_data_str}")
        self.update_status_main_signal.emit(
            f"{time_util.get_format_from_time(time.time())}-响应报文解析-{function_desc}-{return_data_str}")
        pass
        return return_datas
