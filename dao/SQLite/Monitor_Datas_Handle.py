import os

from loguru import logger

from Modbus.Modbus_Response_Parser import Modbus_Slave_Type
from config.global_setting import global_setting
from dao.SQLite.SQliteManager import SQLiteManager

# 监控数据操作类
from util.time_util import time_util


class Monitor_Datas_Handle():
    def __init__(self):
        self.init_construct()

    def init_construct(self):
        self.db_name = self.create_db()
        self.sqlite_manager = SQLiteManager(db_name=self.db_name)
        self.create_tables()
        pass

    def create_db(self):
        """
        创建数据库
        :return:
        """
        year, week_number, weekday = time_util.get_current_week_info()
        # 定义文件夹路径
        folder_path = global_setting.get_setting('monitor_data')['STORAGE']['fold_path'] + os.path.join(

            global_setting.get_setting('monitor_data')['STORAGE']['sub_fold_path'], f'{year}', f'{week_number:02}')

        # 创建文件夹（如果不存在）
        os.makedirs(folder_path, exist_ok=True)
        db_name = f"{weekday}.db"
        db_file_path = os.path.join(folder_path, db_name)
        return db_file_path

    def create_tables(self):
        # 实例化公共传感器数据的数据表
        for data_type in Modbus_Slave_Type.Not_Each_Mouse_Cage.value:
            for table_name_short in data_type.value['table']:
                # 列
                columns = {item[0]: item[2] for item in data_type.value['table'][table_name_short]}
                # 表名称
                table_name = f"{data_type.value['name']}_{table_name_short}"
                # 创建表
                if not self.sqlite_manager.is_exist_table(table_name):
                    self.sqlite_manager.create_table(table_name,
                                                     columns)
                    logger.info(f"数据库{self.db_name}创建数据表{table_name}成功！")
                # 创建该表描述的表
                table_meta_name = f"{table_name}_meta"
                # 不存在则创建和插入
                if not self.sqlite_manager.is_exist_table(table_meta_name):
                    self.sqlite_manager.create_meta_table(table_meta_name)
                    logger.info(f"数据库{self.db_name}创建表结构描述数据表{table_meta_name}成功！")
                    # 插入描述信息
                    for item in data_type.value['table'][table_name_short]:
                        self.sqlite_manager.insert(table_meta_name, item_name=item[0], item_struct=item[2],
                                                   description=item[1])
            pass
        # 实例化每个笼子里的传感器的数据表
        for data_type in Modbus_Slave_Type.Each_Mouse_Cage.value:
            for carge_number in range(1, global_setting.get_setting("configer")['mouse_cage']['nums'] + 1 if
            global_setting.get_setting("configer")['mouse_cage']['nums'] is not None else 2):
                for table_name_short in data_type.value['table']:
                    # 列
                    columns = {item[0]: item[2] for item in data_type.value['table'][table_name_short]}
                    # 表名称
                    table_name = f"{data_type.value['name']}_{table_name_short}_cage_{carge_number}"
                    # 创建表
                    if not self.sqlite_manager.is_exist_table(table_name):
                        self.sqlite_manager.create_table(table_name,
                                                         columns)
                        logger.info(f"数据库{self.db_name}创建数据表{table_name}成功！")
                    # 创建该表描述的表
                    table_meta_name = f"{table_name}_meta"
                    # 不存在则创建和插入
                    if not self.sqlite_manager.is_exist_table(table_meta_name):
                        logger.info(f"数据库{self.db_name}创建表结构描述数据表{table_meta_name}成功！")
                        self.sqlite_manager.create_meta_table(table_meta_name)
                        # 插入描述信息
                        for item in data_type.value['table'][table_name_short]:
                            self.sqlite_manager.insert(table_meta_name, item_name=item[0], item_struct=item[2],
                                                       description=item[1])
        pass

