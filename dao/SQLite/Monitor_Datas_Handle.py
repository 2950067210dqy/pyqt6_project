from Modbus.Modbus_Response_Parser import Modbus_Slave_Type
from config.global_setting import global_setting
from dao.SQLite.SQliteManager import SQLiteManager


# 监控数据操作类
class Monitor_Datas_Handle():
    def __init__(self, db_name):
        self.db_name = db_name
        self.sqlite_manager = SQLiteManager(db_name=db_name)
        self.create_tables()

    def create_tables(self):
        # 实例化公共传感器数据的数据表
        for data_type in Modbus_Slave_Type.Not_Each_Mouse_Cage:
            # 创建表
            self.sqlite_manager.create_table(data_type['name'],
                                             {'id': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'value': '', })
            pass
        # 实例化每个笼子里的传感器的数据表
        for data_type in Modbus_Slave_Type.Each_Mouse_Cage:
            for carge_number in range(1, global_setting.get_setting("configer")['mouse_cage']['nums'] + 1 if
            global_setting.get_setting("configer")['mouse_cage']['nums'] is not None else 2):
                pass
        pass
