import typing

from loguru import logger

from Modbus.Modbus_Response_Parser import Modbus_Slave_Ids
from config.global_setting import global_setting
from entity.send_message import Send_Message
from theme.ThemeQt6 import ThemedWidget
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QRect, pyqtSignal
from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QFrame

from theme.ThemeQt6 import ThemedWidget
from ui.customize_ui.tab.tab2_tab0 import Ui_tab_0_frame
from ui.tab7 import Ui_tab7_frame
from util.number_util import number_util


class Tab2_tab0(ThemedWidget):
    # 更新端口选择和鼠笼选择
    update_port_and_mouse_cage = pyqtSignal()
    show_data_signal = pyqtSignal(list)

    def showEvent(self, a0: typing.Optional[QtGui.QShowEvent]) -> None:
        logger.warning(f"tab2_tab0——show")

    def hideEvent(self, a0: typing.Optional[QtGui.QHideEvent]) -> None:
        logger.warning(f"tab2——tab0--hidden")

    def __init__(self, parent=None, geometry: QRect = None, title=""):
        super().__init__()
        # 类型 0 是Qframe 1是Qmainwindow
        self.type = 1
        # 获取tab2 frame组件
        self.ancestor: QFrame = None
        # 要发送的数据
        self.send_datas = []
        self.send_datas = [
            Send_Message(slave_address=Modbus_Slave_Ids.UFC.value['address'],
                         slave_desc=Modbus_Slave_Ids.UFC.value['description'], function_code=1,
                         function_desc="读输出端口状态信息", message={
                    'port': global_setting.get_setting("tab2_select_port"),
                    'data': number_util.set_int_to_4_bytes_list(10),
                    'slave_id': format(int(Modbus_Slave_Ids.UFC.value['address']), '02X'),
                    'function_code': format(int(f"{1}", 16), '02X'),
                }),
            Send_Message(slave_address=Modbus_Slave_Ids.UFC.value['address'],
                         slave_desc=Modbus_Slave_Ids.UFC.value['description'], function_code=2,
                         function_desc="读传感器状态信息", message={
                    'port': global_setting.get_setting("tab2_select_port"),
                    'data': number_util.set_int_to_4_bytes_list(6),
                    'slave_id': format(int(Modbus_Slave_Ids.UFC.value['address']), '02X'),
                    'function_code': format(int(f"{2}", 16), '02X'),
                }),
            Send_Message(slave_address=Modbus_Slave_Ids.UFC.value['address'],
                         slave_desc=Modbus_Slave_Ids.UFC.value['description'], function_code=3,
                         function_desc="读配置寄存器", message={
                    'port': global_setting.get_setting("tab2_select_port"),
                    'data': number_util.set_int_to_4_bytes_list(3),
                    'slave_id': format(int(Modbus_Slave_Ids.UFC.value['address']), '02X'),
                    'function_code': format(int(f"{3}", 16), '02X'),
                }),
            Send_Message(slave_address=Modbus_Slave_Ids.UFC.value['address'],
                         slave_desc=Modbus_Slave_Ids.UFC.value['description'], function_code=4,
                         function_desc="读传感器测量值", message={
                    'port': global_setting.get_setting("tab2_select_port"),
                    'data': number_util.set_int_to_4_bytes_list(6),
                    'slave_id': format(int(Modbus_Slave_Ids.UFC.value['address']), '02X'),
                    'function_code': format(int(f"{4}", 16), '02X'),
                }),
            Send_Message(slave_address=Modbus_Slave_Ids.UFC.value['address'],
                         slave_desc=Modbus_Slave_Ids.UFC.value['description'], function_code=17,
                         function_desc="读取模块ID信息等", message={
                    'port': global_setting.get_setting("tab2_select_port"),
                    'data': number_util.set_int_to_4_bytes_list(0),
                    'slave_id': format(int(Modbus_Slave_Ids.UFC.value['address']), '02X'),
                    'function_code': format(int(f"{11}", 16), '02X'),
                }),
        ]

        # 实例化ui
        self._init_ui(parent, geometry, title)
        # # 获取祖先组件
        # self.get_ancestor()
        # 实例化自定义ui
        self._init_customize_ui()
        # 实例化功能
        self._init_function()
        # 加载qss样式表
        self._init_style_sheet()

        pass

    # 实例化ui
    def _init_ui(self, parent=None, geometry: QRect = None, title=""):
        # 将ui文件转成py文件后 直接实例化该py文件里的类对象  uic工具转换之后就是这一段代码
        # 有父窗口添加父窗口
        if parent != None and geometry != None:
            self.setParent(parent)
            self.setGeometry(geometry)
        else:
            pass
        self.ui = Ui_tab_0_frame()
        self.ui.setupUi(self)

        self._retranslateUi()
        pass

    # 实例化自定义ui
    def _init_customize_ui(self):
        pass

    # 实例化功能
    def _init_function(self):
        # 绑定更新发送数据的槽
        self.update_port_and_mouse_cage.connect(self.update_send_data)
        # 绑定显示数据的槽
        self.show_data_signal.connect(self.show_data)
        pass

    def update_send_data(self):
        # 更新senddata的port和mouse_cage_number
        logger.info(f"{self.objectName()}触发发送报文更新数据")
        for send_data_single in self.send_datas:
            send_data_single.message['port'] = global_setting.get_setting("tab2_select_port")
            pass
        pass

    def show_data(self, data: list):
        # 显示数据
        logger.info(f"{self.objectName()}显示数据：{data}")
