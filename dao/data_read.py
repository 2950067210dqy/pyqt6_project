from enum import Enum

from loguru import logger

from config.global_setting import global_setting
from dao.data_read_csv import data_read_csv
from dao.data_read_graphy import data_read_graphy
from dao.data_read_txt import data_read_txt
from dao.data_read_xlsx import data_read_xlsx
from util.folder_util import File_Types


class data_read():
    """
    数据获取器
    """

    def __init__(self, file_type: str = 'txt', data_origin_port=[]):
        self.file_type = file_type.lower()
        match self.file_type:
            case File_Types.TXT.value:
                self.read_service = data_read_txt(data_origin_port=data_origin_port,
                                                  data_storage_loc=global_setting.get_setting(
                                                      "communiation_project_path"))
                pass
            case File_Types.CSV.value:
                self.read_service = data_read_csv(data_origin_port=data_origin_port,
                                                  data_storage_loc=global_setting.get_setting(
                                                      "communiation_project_path"))
                pass
            case File_Types.XLSX.value:
                self.read_service = data_read_xlsx(data_origin_port=data_origin_port,
                                                   data_storage_loc=global_setting.get_setting(
                                                       "communiation_project_path"))
            case File_Types.GRAPHY.value:
                self.read_service = data_read_graphy(data_origin_port=data_origin_port,
                                                     data_storage_loc=global_setting.get_setting(
                                                         "communiation_project_path"))

            case _:
                logger.error(f"未支持该数据格式：{file_type}，仅支持下列数据格式{[type.value for type in File_Types]}")
                pass
