from config.global_setting import global_setting
from dao.parser.csv_parser import csv_parser
from util.folder_util import File_Types


class data_read_csv():
    """
    读取csv类
    """

    suffix = File_Types.CSV.value

    def __init__(self, data_storage_loc=global_setting.get_setting("communiation_project_path"),
                 data_origin_port=[]):
        # data数据存储的项目目录地址
        self.data_storage_loc = data_storage_loc
        # 数据串口
        self.data_origin_port = data_origin_port
        # 文本控制器
        self.csv_parser = csv_parser()
        pass


pass
