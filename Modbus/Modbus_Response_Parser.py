"""
响应报文解析
"""
from enum import Enum


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
    Not_Each = [
        Modbus_Slave_Ids.UFC, Modbus_Slave_Ids.UGC, Modbus_Slave_Ids.ZOS
    ]
    Each = [
        Modbus_Slave_Ids.ENM, Modbus_Slave_Ids.EM, Modbus_Slave_Ids.DWM, Modbus_Slave_Ids.WM
    ]


class Modbus_Response():
    def __init__(self, name, function_code):
        self.name = name
        self.function_code = function_code
        self.specific_response = None
        self.init_modbus()

    def init_modbus(self):

        if self.name == Modbus_Slave_Ids.UFC.value['name']:
            print("Modbus_Response_URC")
            self.specific_response = Modbus_Response_URC(function_code=self.function_code)
            pass
        elif self.name == Modbus_Slave_Ids.UGC.value['name']:
            pass
        else:
            pass

    pass


class Modbus_Response_Parents():

    def function_code_parser(self):
        pass


class Modbus_Response_URC(Modbus_Response_Parents):
    def __init__(self, function_code):
        self.function_code = function_code

    def function_code_parser(self):
        if isinstance(self.function_code, str):
            function_code = int(self.function_code, 16)
        else:
            function_code = self.function_code
        match function_code:
            case 1:
                pass
            case 2:
                return self.parser_2()
            case _:
                pass
        return "000000000000000"

    def parser_2(self):
        return "12333333333333333"
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

        self.response_parser: Modbus_Response = None
        self.init_self()
        pass

    def init_self(self):
        self.response_parser = self.get_reponse_parser()

    def parser(self):
        self.update_status_main_signal.emit(self.response_parser.specific_response.function_code_parser())

    def get_reponse_parser(self):
        response_parser = None
        slave_id_int = int(self.slave_id, 16)
        print(f"slave_id_int:{slave_id_int}")
        if slave_id_int > 16:
            # 鼠笼内传感器
            for type in Modbus_Slave_Type.Each.value:
                if type.value['int'] == (slave_id_int % 16):
                    print(f"type.value['name'] Each:{type.value['name']}")
                    response_parser = Modbus_Response(name=type.value['name'], function_code=self.function_code)

                    break
            pass
        else:
            # 非鼠笼内传感器
            for type in Modbus_Slave_Type.Not_Each.value:
                if type.value['int'] == (slave_id_int % 16):
                    print(f"type.value['name'] Not_Each:{type.value['name']}")
                    response_parser = Modbus_Response(name=type.value['name'], function_code=self.function_code)
                    break
            pass
        return response_parser
        pass
