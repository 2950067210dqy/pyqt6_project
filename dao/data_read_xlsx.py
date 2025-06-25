import math
import re
from datetime import datetime

from loguru import logger

from config.global_setting import global_setting
from dao.parser.xlsx_parser import xlsx_parser
from entity.xlsx_data import xlsx_datas, xlsx_datas_item_three_phase, xlsx_datas_item_three_phase_item, \
    xlsx_datas_item_device, xlsx_datas_item_each, xlsx_datas_item_each_result
from entity.xlsx_data_column import xlsx_data, xlsx_datas_type_item, xlsx_datas_phase_item, xlsx_datas_device_item
from util.folder_util import File_Types
from util.time_util import time_util


class data_read_xlsx():
    """
    读取csv类
    """

    suffix = File_Types.XLSX.value

    def __init__(self, data_storage_loc=global_setting.get_setting("communiation_project_path"),
                 data_origin_port=[]):
        # data数据存储的项目目录地址
        self.data_storage_loc = data_storage_loc
        # 数据串口
        self.data_origin_port = data_origin_port
        # 文本控制器
        self.xlsx_parser = xlsx_parser()
        pass
        # 获取三相流数据

    def get_graphics_data(self, times: datetime = datetime.now(), data_origin_port: str = ""):
        """
           获取单个图片文件数据
           :param now datetime类型的时间数据
           :param data_origin_port 数据串口
           :return:
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
            'fold_path'] + "graphy/" + global_setting.get_setting("serial_config")['Storage'][
                   'port_prefix'] + data_origin_port_temp + "/" + str(
            year) + "/" + f"{week}week" + "/" + str(day) + f".{self.suffix}"
        path_dict = {}
        path_dict['port'] = data_origin_port_temp
        path_dict['file_path'] = path

        datas = self.xlsx_parser.read_data(files_path=[path_dict])
        data = datas[0]
        return data
        pass

    # 获取柱状图三相流数据
    def get_three_phase_flow_data_column(self, times: datetime = datetime.now(), data_origin_port: str = ""):
        """
           获取单个文件数据
           :param now datetime类型的时间数据
           :param data_origin_port 数据串口
           :return:
        """
        base_number = 1000000  # ppm 化简
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
            'fold_path'] + "charts/" + global_setting.get_setting("serial_config")['Storage'][
                   'port_prefix'] + data_origin_port_temp + "/" + str(
            year) + "/" + f"{week}week" + "/" + str(day) + f".{self.suffix}"
        path_dict = {}
        path_dict['port'] = data_origin_port_temp
        path_dict['file_path'] = path
        datas = self.xlsx_parser.read_data(files_path=[path_dict])
        data = datas[0]
        data_each_counts = 36
        return_data = xlsx_data()

        # 删除含缺失值的行
        data_clean = data.dropna()
        df_colum_0_unique = data_clean.drop_duplicates(subset=[data_clean.columns[0]])
        df_colum_1_unique = data_clean.drop_duplicates(subset=[data_clean.columns[1]])

        return_data.rated_frequency = float("".join(re.findall(r'[0-9]', df_colum_1_unique.iloc[0, 1])))
        return_data.rated_frequency_unit = "".join(re.findall(r'[A-Za-z]', df_colum_1_unique.iloc[0, 1]))
        return_data.rated_voltage = float(
            "".join(re.findall(r'[0-9]', df_colum_0_unique.iloc[0, 0].split(",")[0])))
        return_data.rated_voltage_unit = "".join(
            re.findall(r'[A-Za-z]', df_colum_0_unique.iloc[0, 0].split(",")[0]))

        # 获得四项数据名  # 收集X轴
        xlsx_datas_type_item_obj_x_data = []
        for row in range(data_clean.shape[0]):

            temp = row / data_each_counts
            index = math.floor(temp)
            if temp == 0:
                xlsx_datas_type_item_obj = xlsx_datas_type_item()
                xlsx_datas_type_item_obj.name = "功率W"
                # 收集x轴
                xlsx_datas_type_item_obj.data.x.name.append(data.iloc[2, 2])
                xlsx_datas_type_item_obj.data.x.name.append("电流/A")
                return_data.data.append(xlsx_datas_type_item_obj)
                pass
            elif temp == 1:
                xlsx_datas_type_item_obj = xlsx_datas_type_item()
                xlsx_datas_type_item_obj.name = "电压"
                # 收集x轴
                xlsx_datas_type_item_obj.data.x.name.append(data.iloc[2, 2])
                xlsx_datas_type_item_obj.data.x.name.append("电流/A")
                return_data.data.append(xlsx_datas_type_item_obj)
                return_data.data[index - 1].data.x.data = xlsx_datas_type_item_obj_x_data
                xlsx_datas_type_item_obj_x_data = []
                pass
            elif temp == 2:
                xlsx_datas_type_item_obj = xlsx_datas_type_item()
                xlsx_datas_type_item_obj.name = "电流"
                # 收集x轴
                xlsx_datas_type_item_obj.data.x.name.append(data.iloc[2, 2])
                xlsx_datas_type_item_obj.data.x.name.append("电流/A")
                return_data.data.append(xlsx_datas_type_item_obj)
                return_data.data[index - 1].data.x.data = xlsx_datas_type_item_obj_x_data
                xlsx_datas_type_item_obj_x_data = []
                pass
            elif temp == 3:
                xlsx_datas_type_item_obj = xlsx_datas_type_item()
                xlsx_datas_type_item_obj.name = "相角"
                # 收集x轴
                xlsx_datas_type_item_obj.data.x.name.append(data.iloc[2, 2])
                xlsx_datas_type_item_obj.data.x.name.append("电流/A")
                return_data.data.append(xlsx_datas_type_item_obj)
                return_data.data[index - 1].data.x.data = xlsx_datas_type_item_obj_x_data
                xlsx_datas_type_item_obj_x_data = []
            # 额定电流单位
            rated_current_unit = "".join(re.findall(r'[A-Za-z]', data_clean.iloc[row, 0].strip().split(",")[1]))
            if rated_current_unit == "mA":
                rated_current = float(
                    "".join(re.findall(r'[0-9]', data_clean.iloc[row, 0].strip().split(",")[1]))) / 1000
                pass
            else:
                rated_current = float("".join(re.findall(r'[0-9]', data_clean.iloc[row, 0].strip().split(",")[1])))
                pass
            # 相角 和 额定电流
            xlsx_datas_type_item_obj_x_data.append([data_clean.iloc[row, 2], rated_current])
        return_data.data[- 1].data.x.data = xlsx_datas_type_item_obj_x_data

        # 设置y轴数据
        # A相 B相 C相
        df_rows_2_4_unique = data.iloc[2, 4:].dropna()
        # 设备名列
        df_rows_3_4 = data.iloc[3, 4:]
        for row in range(data_clean.shape[0]):
            temp = row / data_each_counts
            index = math.floor(temp)
            if temp == 0 or temp == 1 or temp == 2 or temp == 3:
                # A相 B相 C相
                for j in range(df_rows_2_4_unique.shape[0]):
                    xlsx_datas_phase_item_obj = xlsx_datas_phase_item()
                    xlsx_datas_phase_item_obj.name = df_rows_2_4_unique.iloc[j]
                    # 两个设备
                    device_series = df_rows_3_4.drop_duplicates()[:-2]
                    for device_row in range(device_series.shape[0]):
                        xlsx_datas_device_item_obj = xlsx_datas_device_item()
                        xlsx_datas_device_item_obj.name = device_series.iloc[device_row]

                        xlsx_datas_phase_item_obj.data.append(xlsx_datas_device_item_obj)
                        pass
                    return_data.data[index].data.y.append(xlsx_datas_phase_item_obj)
                pass
        # 设置y的具体值
        for row in range(data_clean.shape[0]):
            temp = row / data_each_counts
            index = math.floor(temp)
            # A相 B相 C相
            for j in range(df_rows_2_4_unique.shape[0]):

                # 两个设备
                device_series = df_rows_3_4.drop_duplicates()[:-2]
                for device_row in range(device_series.shape[0]):
                    return_data.data[index].data.y[j].data[device_row].data.append(
                        data_clean.iloc[row, int(df_rows_2_4_unique.index[j][-1]) + device_row])
                    pass

                pass
        return return_data

    # 获取三相流数据
    def get_three_phase_flow_data(self, times: datetime = datetime.now(), data_origin_port: str = ""):
        """
           获取单个文件数据
           :param now datetime类型的时间数据
           :param data_origin_port 数据串口
           :return:
        """
        base_number = 1000000  # ppm 化简
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
            'fold_path'] + "charts/" + global_setting.get_setting("serial_config")['Storage'][
                   'port_prefix'] + data_origin_port_temp + "/" + str(
            year) + "/" + f"{week}week" + "/" + str(day) + f".{self.suffix}"
        path_dict = {}
        path_dict['port'] = data_origin_port_temp
        path_dict['file_path'] = path
        datas = self.xlsx_parser.read_data(files_path=[path_dict])
        data = datas[0]
        data_each_counts = 36
        return_data = xlsx_datas()
        # 删除含缺失值的行
        data_clean = data.dropna()
        # 获得相位角参数 频率参数 电压参数
        df_colum_0_unique = data_clean.drop_duplicates(subset=[data_clean.columns[0]])
        df_colum_1_unique = data_clean.drop_duplicates(subset=[data_clean.columns[1]])
        df_colum_2_unique = data_clean.drop_duplicates(subset=[data_clean.columns[2]])

        return_data.rated_frequency = float("".join(re.findall(r'[0-9]', df_colum_1_unique.iloc[0, 1])))
        return_data.rated_frequency_unit = "".join(re.findall(r'[A-Za-z]', df_colum_1_unique.iloc[0, 1]))
        return_data.rated_voltage = float(
            "".join(re.findall(r'[0-9]', df_colum_0_unique.iloc[0, 0].split(",")[0])))
        return_data.rated_voltage_unit = "".join(
            re.findall(r'[A-Za-z]', df_colum_0_unique.iloc[0, 0].split(",")[0]))
        df_rows_2_4_unique = data.iloc[2, 4:].dropna()

        # 设备名列
        df_rows_3_4 = data.iloc[3, 4:]
        for i in range(df_rows_2_4_unique.shape[0]):
            datas_item_three_phase = xlsx_datas_item_three_phase()
            datas_item_three_phase.phase_name = df_rows_2_4_unique.iloc[i]
            df_colum_2_unique_rows = df_colum_2_unique.shape[0]
            for df_colum_2_unique_row in range(df_colum_2_unique_rows):
                datas_item_three_phase_item = xlsx_datas_item_three_phase_item()
                datas_item_three_phase_item.rated_phase_angle = df_colum_2_unique.iloc[df_colum_2_unique_row, 2]
                datas_item_three_phase_item.rated_phase_angle_unit = data.iloc[2, 2].strip()[-1]
                device_series = df_rows_3_4.drop_duplicates()[:-2]
                for device_row in range(device_series.shape[0]):
                    datas_item_device = xlsx_datas_item_device()
                    datas_item_device.device_name = device_series.iloc[device_row]
                    # 该相角的数据
                    datas_item_each = xlsx_datas_item_each()
                    for row in range(data_clean.shape[0]):

                        if float(data_clean.iloc[row, 2]) == datas_item_three_phase_item.rated_phase_angle:
                            datas_item_each.y_counts = 4
                            rated_current_unit = "".join(
                                re.findall(r'[a-zA-Z]', data_clean.iloc[row, 0].strip().split(",")[1]))
                            datas_item_each_result_rated_current = xlsx_datas_item_each_result()
                            if rated_current_unit == "mA":
                                # 统一单位为A
                                datas_item_each_result_rated_current.result = float(
                                    "".join(re.findall(r'[0-9]', data_clean.iloc[row, 0].strip().split(",")[1]))) / 1000
                                pass
                            else:
                                datas_item_each_result_rated_current.result = float(
                                    "".join(re.findall(r'[0-9]', data_clean.iloc[row, 0].strip().split(",")[1])))
                                pass
                            datas_item_each_result_rated_current.result_unit = "A"

                            temp = row / data_each_counts
                            # 数据纵坐标 =相位纵坐标+device_row
                            column = int(df_rows_2_4_unique.index[i][-1]) + device_row

                            if temp < 1:
                                datas_item_each_result_power = xlsx_datas_item_each_result()
                                datas_item_each_result_power.result = data_clean.iloc[row, column]
                                datas_item_each_result_power.result_error = data_clean.iloc[
                                                                                row, int(df_rows_2_4_unique.index[i][
                                                                                             -1]) + 3] / base_number
                                datas_item_each_result_power.result_unit = "W"
                                datas_item_each_result_power.result_error_unit = "ppm"
                                datas_item_each.result_power_datas.append(datas_item_each_result_power)
                                # 加一次不然重复
                                datas_item_each.rated_current_datas.append(datas_item_each_result_rated_current)
                                pass
                            elif temp >= 1 and temp < 2:
                                datas_item_each_result_voltage = xlsx_datas_item_each_result()
                                datas_item_each_result_voltage.result = data_clean.iloc[row, column]
                                datas_item_each_result_voltage.result_error = data_clean.iloc[
                                                                                  row, int(df_rows_2_4_unique.index[i][
                                                                                               -1]) + 3] / base_number
                                datas_item_each_result_voltage.result_unit = return_data.rated_voltage_unit
                                datas_item_each_result_voltage.result_error_unit = "ppm"
                                datas_item_each.result_voltage_datas.append(datas_item_each_result_voltage)
                                pass
                            elif temp >= 2 and temp < 3:
                                datas_item_each_result_current = xlsx_datas_item_each_result()
                                datas_item_each_result_current.result_unit = rated_current_unit
                                if datas_item_each_result_current.result_unit == "mA":
                                    datas_item_each_result_current.result = float(data_clean.iloc[row, column]) / 1000
                                else:
                                    datas_item_each_result_current.result = float(data_clean.iloc[row, column])
                                    pass
                                datas_item_each_result_current.result_error = data_clean.iloc[
                                                                                  row, int(df_rows_2_4_unique.index[i][
                                                                                               -1]) + 3] / base_number
                                datas_item_each_result_current.result_error_unit = "ppm"
                                datas_item_each.result_current_datas.append(datas_item_each_result_current)
                                pass
                            else:
                                datas_item_each_result_phase = xlsx_datas_item_each_result()
                                datas_item_each_result_phase.result = data_clean.iloc[row, column]
                                datas_item_each_result_phase.result_error = data_clean.iloc[
                                                                                row, int(df_rows_2_4_unique.index[i][
                                                                                             -1]) + 3] / base_number
                                datas_item_each_result_phase.result_unit = datas_item_three_phase_item.rated_phase_angle_unit

                                datas_item_each_result_phase.result_error_unit = datas_item_three_phase_item.rated_phase_angle_unit
                                datas_item_each.result_phase_datas.append(datas_item_each_result_phase)
                                pass
                            datas_item_device.data = datas_item_each
                        pass
                    datas_item_three_phase_item.data.append(datas_item_device)
                    pass
                datas_item_three_phase.data.append(datas_item_three_phase_item)
                pass

            return_data.datas.append(datas_item_three_phase)
        return return_data
        pass


pass
