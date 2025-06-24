import traceback
from datetime import datetime

from loguru import logger

from config.global_setting import global_setting

from entity.txt_data import txt_data
from util.folder_util import folder_util
from util.time_util import time_util


class txt_parser():
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

    def get_file_data_nums(self, file_path=''):
        """
        获取单个文件数据总数
        :return:count
        """
        count = 0
        if self.is_file_exist(file_path=file_path):
            # 逐行读取文件
            try:
                with open(file_path, 'r') as file:
                    for line in file:
                        count += 1
            except Exception as e:
                count = 0
                logger.error(f"读取文件{file_path}失败,失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")
            pass
        return count

    def get_files_data_nums(self, files_path=[]):
        """
        获取多个文件的每个文件的数据总数
        :return:count
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
        counts = []
        for dict_temp in files_path_temp:
            counts.append(self.get_file_data_nums(dict_temp['file_path']))
            pass
        return counts
        pass

    def read_seq_from_index_start(self, files_path=[], data_nums: list = [1], data_start: list = [],
                                  data_step: list = []) -> [[
        txt_data()]]:
        """
        顺序读取数据 数据读取开始位置是根据index的值来开始读取的
        :param files_path 文件地址list [{'port':'','file_path':''},...]
        :param data_nums 读取数据数量[nums]
        :param data_start [] 数据范围开始 读取范围data_start到data_start+data_nums 的数据
        :param data_step [] 数据步长 每隔几个数据取数据 如果为负值则从后往前隔着取
        :return: 返回数据列表 [[txt_data() ,...],....]
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
        index = 0
        for dict_temp in files_path_temp:
            # 判断数据文件是否存在
            is_data_file_exist = self.is_file_exist(dict_temp['file_path'])
            if is_data_file_exist:
                # 将文件的每一行读入列表
                lines = []
                try:
                    with open(dict_temp['file_path'], 'r') as file:
                        lines = file.readlines()  # 读取所有行
                        lines = [line.strip() for line in lines]  # 去掉换行符
                except Exception as e:
                    logger.error(f"读取文件{dict_temp['file_path']}失败,失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")
                # 蒋读取的数据转换为数据格式 [txt_data(),...]
                return_data = []
                nums_temp = 1
                id = 1
                # 步长小于0 逆序输出
                if data_step[index] >= 0:
                    for line in lines:
                        # 空格分割 [0]是数据 [1]是日期
                        if nums_temp >= data_start[index] and nums_temp < data_start[index] + data_nums[
                            index] and nums_temp % data_step[index] == 0:
                            line_datas = line.split(" ")
                            data = txt_data(id, line_datas[0], line_datas[1])
                            return_data.append(data)
                        id += 1
                        nums_temp += 1
                        pass
                else:
                    for line in reversed(lines):
                        # 空格分割 [0]是数据 [1]是日期
                        if nums_temp >= data_start[index] and nums_temp < data_start[index] + data_nums[
                            index] and nums_temp % data_step[index] == 0:
                            line_datas = line.split(" ")
                            data = txt_data(id, line_datas[0], line_datas[1])
                            return_data.append(data)
                        id += 1
                        nums_temp += 1
                        pass
                return_datas.append(return_data)
                pass
            else:
                # 如果不存在文件 就加入空值
                return_datas.append([])
            index += 1
        return return_datas

    def read_seq_from_times_start(self, files_path=[], data_nums: list = [1], data_start: list = [],
                                  data_step: list = [], data_times_delay: int = 1) -> [[
        txt_data()]]:
        """
        顺序读取数据 数据读取开始位置是根据times的值来开始读取的
        :param files_path 文件地址list [{'port':'','file_path':''},...]
        :param data_nums 读取数据数量[nums]
        :param data_start [datetime.value | timestamp.value] 数据范围开始 读取范围data_start到data_start+data_nums 的数据
        :param data_step [] 数据步长 每隔几个数据取数据 如果为负值则从后往前隔着取
        :return: 返回数据列表 [[txt_data() ,...],....]
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
        index = 0
        for dict_temp in files_path_temp:
            # 判断数据文件是否存在
            is_data_file_exist = self.is_file_exist(dict_temp['file_path'])
            if is_data_file_exist:
                # 将文件的每一行读入列表
                lines = []
                try:
                    with open(dict_temp['file_path'], 'r') as file:
                        lines = file.readlines()  # 读取所有行
                        lines = [line.strip() for line in lines]  # 去掉换行符
                except Exception as e:
                    logger.error(f"读取文件{dict_temp['file_path']}失败,失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")
                # 蒋读取的数据转换为数据格式 [txt_data(),...]
                return_data = []
                nums_temp = 1
                id = 1
                # 步长小于0 逆序输出
                if data_step[index] >= 0:
                    for line in lines:

                        # 空格分割 [0]是数据 [1]是日期
                        line_datas = line.split(" ")
                        data_date_time = datetime.strptime(line_datas[1], "%Y-%m-%d/%H:%M:%S.%f").timestamp()

                        if data_date_time >= data_start[index] and nums_temp <= data_nums[
                            index] and nums_temp % data_step[index] == 0:
                            data = txt_data(id, line_datas[0], line_datas[1])
                            return_data.append(data)
                            nums_temp += 1
                        id += 1

                        pass
                else:
                    for line in reversed(lines):
                        # 空格分割 [0]是数据 [1]是日期
                        line_datas = line.split(" ")
                        data_date_time = datetime.strptime(line_datas[1], "%Y-%m-%d/%H:%M:%S.%f").timestamp()

                        if data_date_time >= data_start[index] and nums_temp <= data_nums[
                            index] and nums_temp % data_step[index] == 0:
                            data = txt_data(id, line_datas[0], line_datas[1])
                            return_data.append(data)
                            nums_temp += 1
                        id += 1

                        pass
                return_datas.append(return_data)
                pass
            else:
                # 如果不存在文件 就加入空值
                return_datas.append([])
            index += 1
        return return_datas
