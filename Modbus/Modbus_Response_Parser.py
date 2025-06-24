"""
响应报文解析
"""


class Modbus_Slave_Ids():
    """
    远程地址大全
    """
    ids = [
        {
            "name": "UFC",
            "description": "气流控制模块",
            'address': 0x02
        },
        {
            "name": "UGC",
            "description": "二氧化碳含量模块",
            'address': 0x03
        },
        {
            "name": "ZOS",
            "description": "氧气含量测量模块",
            'address': 0x04
        },
        {
            "name": "ENM",
            "description": "鼠笼环境监控模块",
            'address': 0x01
            # 每个鼠笼都有该模块，
            # 地址还要加上当前鼠笼号*16
            # 例如鼠笼1的鼠笼环境监控模块地址就是0x11
        },
        {
            "name": "EM",
            "description": "进食监控模块",
            'address': 0x02
            # 每个鼠笼都有该模块，
            # 地址还要加上当前鼠笼号*16
            # 例如鼠笼1的鼠笼环境监控模块地址就是0x11
        },
        {
            "name": "DWM",
            "description": "饮水监控模块",
            'address': 0x03
            # 每个鼠笼都有该模块，
            # 地址还要加上当前鼠笼号*16
            # 例如鼠笼1的鼠笼环境监控模块地址就是0x11
        },
        {
            "name": "WM",
            "description": "称重模块",
            'address': 0x04
            # 每个鼠笼都有该模块，
            # 地址还要加上当前鼠笼号*16
            # 例如鼠笼1的鼠笼环境监控模块地址就是0x11
        },
    ]


class Modbus_Response_Parser():
    """
响应报文解析
    """

    def __init__(self, slave_id, function_code, response, response_hex):
        """

        :param slave_id: 地址码
        :param function_code: 功能码
        :param response: 响应报文
        :param response_hex: 响应报文16进制
        """
        self.slave_id = slave_id
        self.function_code = function_code
        self.response = response
        self.response_hex = response_hex
        pass

    def find_slave_ids_by_slave_id(self):
        pass
