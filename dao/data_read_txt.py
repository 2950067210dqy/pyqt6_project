from datetime import datetime

from loguru import logger

from config.global_setting import global_setting
from dao.parser.txt_parser import txt_parser
from entity.txt_data import txt_data
from util.time_util import time_util


class data_read_txt():
    """
    读取txt数据类
    """
    suffix = "txt"

    def __init__(self, data_storage_loc=global_setting.get_setting("communiation_project_path"),
                 data_origin_port=[]):
        # data数据存储的项目目录地址
        self.data_storage_loc = data_storage_loc
        # 数据串口
        self.data_origin_port = data_origin_port
        # 文本控制器
        self.txt_parser = txt_parser()
        pass

    def read_all_data_seq(self, times: datetime = datetime.now(), data_origin_port: str = "") -> [
        txt_data()]:
        """
        顺序获取日期的单个文件数据
        :param now datetime类型的时间数据
        :param data_origin_port 数据串口
        :return: [txt_data()]
        """
        if len(self.data_origin_port) == 0 and data_origin_port == "":
            logger.warning(f"未传入串口参数")
            return []
            pass
        if len(self.data_origin_port) == 1 and data_origin_port == "":
            # 若未传参数则用内置参数
            data_origin_port_temp = self.data_origin_port[0]
        else:
            data_origin_port_temp = data_origin_port
        year, week, day = time_util.get_times_week_info(times)
        path = self.data_storage_loc + global_setting.get_setting("serial_config")['Storage'][
            'fold_path'] + global_setting.get_setting("serial_config")['Storage'][
                   'port_prefix'] + data_origin_port_temp + "/" + str(
            year) + "/" + f"{week}week" + "/" + str(day) + f".{self.suffix}"

        data = self.txt_parser.read_seq(files_path=[path], data_start=[1],
                                        data_nums=[self.txt_parser.get_file_data_nums(file_path=path)], data_step=[1])[
            0]
        return data

        pass

    def read_all_datas_seq(self, times: datetime = datetime.now(), data_origin_port: str = []) -> [[
        txt_data()]]:
        """
        顺序获取多个文件数据
        :param now datetime类型的时间数据
        :param data_origin_port 数据串口[]
        :return: [[txt_data()]]
        """
        if len(self.data_origin_port) == 0 and len(data_origin_port) == 0:
            logger.warning(f"未传入串口参数")
            return []
            pass
        if len(self.data_origin_port) == 1 and len(data_origin_port) == 0:
            # 若未传参数则用内置参数
            data_origin_port_temp = self.data_origin_port
        else:
            data_origin_port_temp = data_origin_port
        year, week, day = time_util.get_times_week_info(times)
        path_s = []
        data_start = []
        data_step = []
        for port in data_origin_port_temp:
            data_start.append(1)
            data_step.append(1)
            path = self.data_storage_loc + global_setting.get_setting("serial_config")['Storage'][
                'fold_path'] + global_setting.get_setting("serial_config")['Storage'][
                       'port_prefix'] + port + "/" + str(
                year) + "/" + f"{week}week" + "/" + str(day) + f".{self.suffix}"
            path_dict = {}
            path_dict['port'] = port
            path_dict['file_path'] = path
            path_s.append(path_dict)
        datas = self.txt_parser.read_seq(files_path=path_s, data_start=data_start,
                                         data_nums=self.txt_parser.get_files_data_nums(files_path=path_s),
                                         data_step=data_step)
        return datas
        pass

    def read_range_data_seq(self, times: datetime = datetime.now(), data_origin_port: str = "", data_start: int = 1,
                            data_nums: int = 1, data_step: int = 1) -> [[
        txt_data()]]:
        """
        顺序获取日期的单个文件范围数据
        :param now datetime类型的时间数据
        :param data_origin_port 数据串口
        :param data_nums 读取数据数量nums
        :param data_start 数据范围开始 读取范围data_start到data_start+data_nums 的数据
        :param data_step 数据步长 每隔几个数据取数据 如果为负值则从后往前隔着取
        :return: [txt_data()]
        """
        if len(self.data_origin_port) == 0 and data_origin_port == "":
            logger.warning(f"未传入串口参数")
            return []
            pass
        if len(self.data_origin_port) == 1 and data_origin_port == "":
            # 若未传参数则用内置参数
            data_origin_port_temp = self.data_origin_port[0]
        else:
            data_origin_port_temp = data_origin_port
        year, week, day = time_util.get_times_week_info(times)
        path = self.data_storage_loc + global_setting.get_setting("serial_config")['Storage'][
            'fold_path'] + global_setting.get_setting("serial_config")['Storage'][
                   'port_prefix'] + data_origin_port_temp + "/" + str(
            year) + "/" + f"{week}week" + "/" + str(day) + f".{self.suffix}"
        data = self.txt_parser.read_seq(files_path=[path], data_start=[data_start],
                                        data_nums=[data_nums], data_step=[data_step])[0]
        return data

    def read_range_datas_seq(self, times: datetime = datetime.now(), data_origin_port: list = [], data_start: list = [],
                             data_nums: list = [], data_step: list = []) -> [[
        txt_data()]]:
        """
        顺序获取多个文件范围数据
        :param now datetime类型的时间数据
        :param data_origin_port 数据串口[]
        :param data_nums 读取数据数量nums
        :param data_start 数据范围开始 读取范围data_start到data_start+data_nums 的数据
        :param data_step 数据步长 每隔几个数据取数据 如果为负值则从后往前隔着取
        :return: [[txt_data()]]
        """
        if len(self.data_origin_port) == 0 and len(data_origin_port) == 0:
            logger.warning(f"未传入串口参数")
            return []
            pass
        if len(self.data_origin_port) == 1 and len(data_origin_port) == 0:
            # 若未传参数则用内置参数
            data_origin_port_temp = self.data_origin_port
        else:
            data_origin_port_temp = data_origin_port
        year, week, day = time_util.get_times_week_info(times)

        path_s = []
        for port in data_origin_port_temp:
            path = self.data_storage_loc + global_setting.get_setting("serial_config")['Storage'][
                'fold_path'] + global_setting.get_setting("serial_config")['Storage'][
                       'port_prefix'] + port + "/" + str(
                year) + "/" + f"{week}week" + "/" + str(day) + f".{self.suffix}"
            path_dict = {}
            path_dict['port'] = port
            path_dict['file_path'] = path
            path_s.append(path_dict)
        datas = self.txt_parser.read_seq(files_path=path_s, data_start=data_start,
                                         data_nums=data_nums,
                                         data_step=data_step)
        return datas
        pass
