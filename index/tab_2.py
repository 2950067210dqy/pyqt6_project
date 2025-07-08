import time
import typing

from loguru import logger

from Modbus.COM_Scan import scan_serial_ports_with_id
# from pyqt6_plugins.examplebutton import QtWidgets
from Modbus.Modbus import ModbusRTUMaster
from Modbus.Modbus_Response_Parser import Modbus_Response_Parser
from config.global_setting import global_setting
from theme.ThemeQt6 import ThemedWidget

from ui.customize_ui.tab.index.tab2_tab import Tab2_tab

from ui.tab2 import Ui_tab2_frame
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import QRect, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton, QStyle, QComboBox, QListWidget

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
        # 下拉框数据列表
        self.ports = []
        #鼠笼下拉框数据列表
        self.mouse_cages = []
        # 发送的数据结构
        self.send_message = {
            'port': '',
            'data': '',
            'slave_id': 0,
            'function_code': 0,
            'timeout': 0,
            'mouse_cage':0
        }
        self.modbus = None
        self.send_thread: Send_thread = None
        # 实例化ui
        self._init_ui(parent, geometry, title)
        # 获取相关数据
        self._init_data()
        # 实例化自定义ui
        self._init_customize_ui()
        # 实例化功能
        self._init_function()
        self._init_style_sheet()
        self._init_customize_style_sheet()
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
        # 获得相关数据

    def _init_data(self):
        # 获得下拉框数据 串口
        self.ports = scan_serial_ports_with_id()
        # 鼠笼下拉框数据
        self.mouse_cages = [{
            "id": i+1 ,
            "description": f"鼠笼{i+1}",
        } for i in range(int(global_setting.get_setting("configer")['mouse_cage']['nums']))]
        pass
    # 实例化自定义ui
    def _init_customize_ui(self):
        # 实例化下拉框 串口
        self.init_port_combox()
        # 鼠笼下拉框
        self.init_mouse_cage_combox()
        # 根据监测数据项配置tab页
        self._init_monitor_data_tab_page()

        pass

    # 实例化功能
    def _init_function(self):
        # 实例化按钮信号槽绑定
        self.init_btn_func()
        pass

    def _init_customize_style_sheet(self):
        pushbtns: [QPushButton] = self.findChildren(QPushButton)
        for btn in pushbtns:
            btn.setStyleSheet("""
               QPushButton{

                       padding: 5px;

                   }
               """)
        pass

    # 实例化按钮信号槽绑定
    def init_btn_func(self):
        # 重新获取端口按钮
        refresh_port_btn: QPushButton = self.findChild(QPushButton, "tab_2_refresh_port_btn")

        refresh_port_btn.clicked.connect(self.refresh_port)

        pass

    # 重新获取端口
    def refresh_port(self):
        self.ports = []
        self.mouse_cages = []
        self._init_data()
        self.init_port_combox()
        self.init_mouse_cage_combox()
    # 实例化端口下拉框
    def init_port_combox(self):
        port_combox: QComboBox = self.findChild(QComboBox, "tab_2_port_combox")
        if port_combox == None:
            logger.error("tab2实例化端口下拉框失败！")
            return
        port_combox.clear()
        for port_obj in self.ports:
            port_combox.addItem(f"-设备: {port_obj['device']}" + f" #{port_obj['description']}")
            pass
        if len(self.ports) != 0:
            # 默认下拉项
            self.send_message['port'] = self.ports[0]['device']
            self.send_response_text(
                f"{time_util.get_format_from_time(time.time())}- 设备: {self.ports[0]['device']}" + f" #{self.ports[0]['description']}" + "  默认已被选中!")
        port_combox.disconnect()
        port_combox.currentIndexChanged.connect(self.selection_change_port_combox)
    def selection_change_port_combox(self, index):
        try:
            self.send_message['port'] = self.ports[index]['device']

            self.send_response_text(
                f"{time_util.get_format_from_time(time.time())}- 设备: {self.ports[index]['device']}" + f" #{self.ports[index]['description']}" + "  已被选中!")
        except Exception as e:
            logger.error(e)
        pass

    # 实例化鼠笼下拉框
    def init_mouse_cage_combox(self):
        mouse_cage_combox: QComboBox = self.findChild(QComboBox, "tab_2_mouse_cage_combox")
        if mouse_cage_combox == None:
            logger.error("tab2实例化鼠笼下拉框失败！")
            return
        mouse_cage_combox.clear()
        for mouse_cage_obj in self.mouse_cages:
            mouse_cage_combox.addItem(f"{mouse_cage_obj['description']}")
            pass
        if len(self.mouse_cages) != 0:
            # 默认下拉项
            self.send_message['mouse_cage'] = self.mouse_cages[0]['id']
            self.send_response_text(
                f"{time_util.get_format_from_time(time.time())}- {self.mouse_cages[0]['description']}" + "  默认已被选中!")
        mouse_cage_combox.disconnect()
        mouse_cage_combox.currentIndexChanged.connect(self.selection_change_mouse_cage_combox)

    def selection_change_mouse_cage_combox(self, index):
        try:
            self.send_message['mouse_cage'] = self.mouse_cages[index]['id']

            self.send_response_text(
                f"{time_util.get_format_from_time(time.time())}- {self.mouse_cages[index]['description']}" + "  已被选中!")
        except Exception as e:
            logger.error(e)
        pass
    def send_response_text(self, text):
        # 往状态栏发消息
        response_text: QListWidget = self.findChild(QListWidget, "tab_2_responselist")
        if response_text == None:
            logger.error("response_text状态栏未找到！")
            return
        response_text.addItem(text)
        # 滑动滚动条到最底下
        scroll_bar = response_text.verticalScrollBar()
        if scroll_bar != None:
            scroll_bar.setValue(scroll_bar.maximum())
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
                tab_content = QtWidgets.QWidget()
                tab_content.setObjectName(f"tab_{monitor_data['id'] - 1}_{monitor_data['object_name']}")
                # 创建一个 QScrollArea
                scroll_area = QScrollArea(tab_content)
                scroll_area.setObjectName(f"scroll_tab_{i}")
                scroll_area.setWidgetResizable(True)  # 使内容小部件可以调整大小

                # 创建一个内容小部件并填充内容
                tab_frame = Tab2_tab(id=monitor_data['id'])
                content_widget = QWidget()
                content_widget.setObjectName(f"scroll_tab_{i}_content_widget")
                content_widget.setFixedSize(tab_frame.tab.size().width()+100,tab_frame.tab.size().height() + 200)
                layout = QVBoxLayout(content_widget)
                layout.setObjectName(f"scroll_tab_{i}_content_widget_layout")

                layout.addWidget(tab_frame.tab)

                # 将内容小部件添加到 QScrollArea
                scroll_area.setWidget(content_widget)
                # 创建一个布局将 scroll_area 添加进去
                tab_layout = QVBoxLayout(tab_content)
                tab_layout.setObjectName(f"tab_{monitor_data['id'] - 1}_{monitor_data['object_name']}_layout")
                tab_layout.addWidget(scroll_area)
                tab_content.setLayout(tab_layout)

                self.tabWidget.addTab(tab_content, monitor_data['title'])
                i += 1
                pass
                pass
            content_layout_son.addWidget(self.tabWidget)



