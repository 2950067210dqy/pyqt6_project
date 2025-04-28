import os

from PyQt6.QtGui import QPixmap
from loguru import logger

from util.folder_util import folder_util


class graphy_parser():
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

    # 获取文件夹下的所有文件的名称 不递归
    def get_file_names_in_current_dir(self, folder_path):
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # 获取文件夹下的所有图片
    def read_data(self, files_path=[], suffix="png"):
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
            return_data = []
            # 判断数据文件是否存在
            correct_data = {}
            correct_data['name'] = 'correct'
            correct_data['data'] = []
            is_folder_file_exist = folder_util.is_exist_folder(dict_temp['file_path'][0])
            if is_folder_file_exist:
                # 读取
                file_names = self.get_file_names_in_current_dir(dict_temp['file_path'][0])
                for name in file_names:
                    correct_data['data'].append(QPixmap(dict_temp['file_path'][0] + name))
            error_data = {}
            error_data['name'] = 'error'
            error_data['data'] = []
            is_folder_file_exist = folder_util.is_exist_folder(dict_temp['file_path'][1])
            if is_folder_file_exist:
                # 读取
                file_names = self.get_file_names_in_current_dir(dict_temp['file_path'][1])
                for name in file_names:
                    error_data['data'].append(QPixmap(dict_temp['file_path'][1] + name))
            return_data.append(correct_data)
            return_data.append(error_data)
            return_datas.append(return_data)
        return return_datas
