import pandas as pd
from loguru import logger

from util.folder_util import folder_util


class xlsx_parser():
    """
    txt解析器
    """

    def __init__(self, files_path=[]):
        """
        实例化方法
        :param files_path:文件地址list [{‘port’:'COM3','file_path':'./data/..'},....]
        """
        self.files_path = files_path
        pass

    def set_files_path(self, files_path=[]):
        self.files_path = files_path

    def is_files_exist(self, files_path=[]):
        """
        判断多个文件是否存在
        :param files_path 多个文件地址
        :return: [True False]
        """
        if len(files_path) == 0 and len(self.files_path) == 0:
            # 参数错误
            logger.warning("数据文件存储位置参数错误！")
            return []
            pass

        if len(files_path) != 0:
            # 用参数中的files_path
            files_path_temp = files_path
            pass
        else:
            # 未带参数则用实例化时的参数
            files_path_temp = self.files_path
            pass
        is_exists = []
        for dict_temp in files_path_temp:
            is_exists.append(self.is_file_exist(dict_temp['file_path']))
            pass
        return is_exists

    def is_file_exist(self, file_path=''):
        """
        判断单个文件是否存在
        :return: True False
        """
        return folder_util.is_exist_file(file_path)
        pass

    def read_data(self, files_path=[]):
        """
        获取xlsx数据
        :return:
        """
        if len(files_path) == 0 and len(self.files_path) == 0:
            # 参数错误
            logger.warning("数据文件存储位置参数错误！")
            return []
            pass
        if len(files_path) != 0:
            # 用参数中的files_path
            files_path_temp = files_path
            pass
        else:
            # 未带参数则用实例化时的参数
            files_path_temp = self.files_path
            pass

        # 返回数据
        return_datas = []
        for dict_temp in files_path_temp:
            # 判断数据文件是否存在
            is_data_file_exist = self.is_file_exist(dict_temp['file_path'])
            if is_data_file_exist:
                # 读取整个表格为 DataFrame
                df = pd.read_excel(dict_temp['file_path'], engine='openpyxl')
                return_datas.append(df)
        return return_datas
