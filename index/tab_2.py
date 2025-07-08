import time
import typing

from loguru import logger
# from pyqt6_plugins.examplebutton import QtWidgets
from Modbus.Modbus import ModbusRTUMaster
from Modbus.Modbus_Response_Parser import Modbus_Response_Parser
from config.global_setting import global_setting
from theme.ThemeQt6 import ThemedWidget
from ui.customize_ui.component.Scroll import Scroll
from ui.customize_ui.tab.index.tab2_tab import Tab2_tab

from ui.tab2 import Ui_tab2_frame
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import QRect, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from theme.ThemeQt6 import ThemedWidget
from util.time_util import time_util


class Send_thread(QThread):
    # 线程信号

    def __init__(self, update_time_main_signal, modbus, send_message):
        super().__init__()
        # 获取主线程更新界面信号
        self.update_time_main_signal: pyqtSignal = update_time_main_signal
        self.modbus = modbus
        self.send_message = send_message
        self.is_strat = True
        pass

    def set_send_message(self, send_message):
        self.send_message = send_message

    def set_modbus(self, modbus):
        self.modbus = modbus

    def run(self):
        while True:

            if self.is_strat:
                self.modbus = ModbusRTUMaster(port=self.send_message['port'], timeout=self.send_message['timeout'],
                                              update_status_main_signal=self.update_time_main_signal)
                try:
                    logger.info(self.send_message)
                    response, response_hex, send_state = self.modbus.send_command(
                        slave_id=self.send_message['slave_id'],
                        function_code=self.send_message['function_code'],
                        data_hex_list=self.send_message['data'])

                    self.is_strat = False
                except Exception as e:
                    logger.error(e)
                    self.update_time_main_signal.emit(f"{time_util.get_format_from_time(time.time())}-{e}")
                finally:
                    self.is_strat = False
            time.sleep(1)
        pass

    pass


class Tab_2(ThemedWidget):

    def showEvent(self, a0: typing.Optional[QtGui.QShowEvent]) -> None:
        # 加载qss样式表
        logger.warning("tab2——show")

    def hideEvent(self, a0: typing.Optional[QtGui.QHideEvent]) -> None:
        logger.warning("tab2--hide")

    def __init__(self, parent=None, geometry: QRect = None, title=""):
        super().__init__()
        # 图像列表
        self.charts_list = []
        # 实例化ui
        self._init_ui(parent, geometry, title)
        # 实例化自定义ui
        self._init_customize_ui()
        # 实例化功能
        self._init_function()
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
        self.ui = Ui_tab2_frame()
        self.ui.setupUi(self)

        self._retranslateUi()
        pass

    # 实例化自定义ui
    def _init_customize_ui(self):
        # 根据监测数据项配置tab页
        self._init_monitor_data_tab_page()
        pass

    # 根据监测数据项配置tab页
    def _init_monitor_data_tab_page(self):
        # tabwidget是否存在
        self.tabWidget = self.findChild(QtWidgets.QTabWidget, "tab_2_tabWidget")
        if self.tabWidget is None:
            # tab页布局
            content_layout_son: QVBoxLayout = self.findChild(QVBoxLayout, "content_layout_son")

            self.tabWidget = QtWidgets.QTabWidget()
            self.tabWidget.setObjectName("tab_2_tabWidget")
            self.tabWidget.setStyleSheet("")
            monitor_data_tab_page_config = global_setting.get_setting("configer")['monitoring_data']
            i = 0
            for monitor_data in monitor_data_tab_page_config:
                tab_parent = QtWidgets.QWidget()
                tab_parent.setObjectName(f"tab_parent_{monitor_data['id'] - 1}_{monitor_data['object_name']}")
                tab_parent_layout = QVBoxLayout(tab_parent)
                tab_parent_layout.setObjectName(
                    f"tab_parent_layout{monitor_data['id'] - 1}_{monitor_data['object_name']}")
                tab = QtWidgets.QWidget()
                tab.setObjectName(f"tab_{monitor_data['id'] - 1}_{monitor_data['object_name']}")
                tab_layout = QVBoxLayout(tab)  # 为tab添加垂直布局
                tab_layout.setObjectName(f"tab_layout_{i}")

                tab_frame = Tab2_tab(id=monitor_data['id'])
                Scroll.set_scroll_to_component(component=tab_frame.tab, component_parent_layout=tab_layout,
                                               scroll_object_name=f"scroll_tab_{i}")
                self.tabWidget.addTab(tab_parent, monitor_data['title'])
                i += 1
                pass
                pass
            content_layout_son.addWidget(self.tabWidget)

    # 实例化功能
    def _init_function(self):
        pass
