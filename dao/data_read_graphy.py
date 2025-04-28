from datetime import datetime

from loguru import logger

from config.global_setting import global_setting
from dao.parser.graphy_parser import graphy_parser
from util.time_util import time_util


class data_read_graphy():
    """
    读取csv类
    """
    suffix = "png"

    def __init__(self, data_storage_loc=global_setting.get_setting("communiation_project_path"),
                 data_origin_port=[]):
        # data数据存储的项目目录地址
        self.data_storage_loc = data_storage_loc
        # 数据串口
        self.data_origin_port = data_origin_port
        # 控制器
        self.graphy_parser = graphy_parser()
        pass
        # 获取三相流数据

    def get_data_image(self, times: datetime = datetime.now(), data_origin_port: str = ""):
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
            'fold_path'] + "graphy/" + global_setting.get_setting("serial_config")['Storage'][
                   'port_prefix'] + data_origin_port_temp + "/" + str(
            year) + "/" + f"{week}week" + "/" + str(day) + "/"
        path_dict = {}
        path_dict['port'] = data_origin_port_temp
        path_dict['file_path'] = [path + "correct/", path + "error/"]

        datas = self.graphy_parser.read_data(files_path=[path_dict], suffix=self.suffix)
        return datas[0]
        pass
