import math
import typing

from loguru import logger

from Modbus.Modbus_Type import Modbus_Slave_Ids
from config.global_setting import global_setting
from entity.send_message import Send_Message
from theme.ThemeQt6 import ThemedWidget
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QRect, pyqtSignal
from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QFrame, QGroupBox, QGridLayout, QHBoxLayout, QLabel, \
    QVBoxLayout, QScrollArea

from theme.ThemeQt6 import ThemedWidget
from ui.customize_ui.tab.index.tab2_tab0_index import Store_thread_for_tab_frame
from ui.customize_ui.tab.tab2_tab1 import Ui_tab_1_frame
from ui.tab7 import Ui_tab7_frame
from util.number_util import number_util


class Tab2_tab1(ThemedWidget):
    # 更新端口选择和鼠笼选择
    update_port_and_mouse_cage = pyqtSignal()
    # 显示数据
    show_data_signal = pyqtSignal(dict)

    def showEvent(self, a0: typing.Optional[QtGui.QShowEvent]) -> None:
        logger.warning(f"{self.objectName()}——show")
        if self.store_thread_for_tab_frame is not None and self.store_thread_for_tab_frame.isRunning():

            self.store_thread_for_tab_frame.resume()
        elif not self.store_thread_for_tab_frame.isRunning():

            self.store_thread_for_tab_frame.start()

    def hideEvent(self, a0: typing.Optional[QtGui.QHideEvent]) -> None:
        logger.warning(f"{self.objectName()}--hidden")
        if self.store_thread_for_tab_frame is not None and self.store_thread_for_tab_frame.isRunning():
            self.store_thread_for_tab_frame.pause()

    def __init__(self, parent=None, geometry: QRect = None, title=""):
        super().__init__()
        # 类型
        self.type = Modbus_Slave_Ids.UGC

        # 找到开始获取信息按钮
        self.start_btn: QPushButton = None
        # 找到停止获取信息按钮
        self.stop_btn: QPushButton = None
        # 找到刷新全部信息按钮
        self.refresh_btn: QPushButton = None
        self.store_thread_for_tab_frame = None

        # 实例化ui
        self._init_ui(parent, geometry, title)

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
        self.ui = Ui_tab_1_frame()
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

        # 实例化发送查询报文线程
        if self.store_thread_for_tab_frame is None:
            self.store_thread_for_tab_frame = Store_thread_for_tab_frame(
                name=self.objectName(),
            )

        # 实例化按钮功能
        self.init_btn_func()
        pass

    def init_btn_func(self):
        # 实例化按钮功能
        # 找到开始获取信息按钮
        self.start_btn: QPushButton = self.findChild(QPushButton, 'start')
        # 找到停止获取信息按钮
        self.stop_btn: QPushButton = self.findChild(QPushButton, 'stop')
        # 找到刷新全部信息按钮
        self.refresh_btn: QPushButton = self.findChild(QPushButton, 'refresh')
        self.start_btn.setDisabled(True)
        self.start_btn.clicked.connect(self.start_btn_func)
        self.stop_btn.clicked.connect(self.stop_btn_func)
        self.refresh_btn.clicked.connect(self.refresh_btn_func)
        pass

    def start_btn_func(self):
        """
        开始获取信息按钮功能
        :return:
        """
        if self.store_thread_for_tab_frame is not None and self.store_thread_for_tab_frame.isRunning():

            self.store_thread_for_tab_frame.resume()
        elif not self.store_thread_for_tab_frame.isRunning():

            self.store_thread_for_tab_frame.start()
        else:
            # 实例化发送查询报文线程
            self.store_thread_for_tab_frame = Store_thread_for_tab_frame(
                name=self.objectName(),
            )
            self.store_thread_for_tab_frame.start()
        self.stop_btn.setDisabled(False)
        self.start_btn.setDisabled(True)

    def stop_btn_func(self):
        """
        停止获取信息按钮功能
        :return:
        """
        if self.store_thread_for_tab_frame is not None and self.store_thread_for_tab_frame.isRunning():
            self.store_thread_for_tab_frame.pause()
        self.start_btn.setDisabled(False)
        self.stop_btn.setDisabled(True)

    def refresh_btn_func(self):
        """
        刷新全部信息按钮功能
        :return:
        """
        # 实例化发送查询报文线程
        self.refresh_btn.setDisabled(True)
        self.store_thread_for_tab_frame.stop()
        self.store_thread_for_tab_frame.terminate()
        self.store_thread_for_tab_frame = None
        self.store_thread_for_tab_frame = Store_thread_for_tab_frame(
            name=self.objectName(),
        )
        self.store_thread_for_tab_frame.start()
        self.start_btn.setDisabled(True)
        self.stop_btn.setDisabled(False)
        self.refresh_btn.setDisabled(False)

    def update_send_data(self):
        # 更新mouse_cage_number
        logger.info(f"{self.objectName()}触发发送报文更新数据")
        # for send_data_single in self.send_datas:
        #     send_data_single.message['port'] = global_setting.get_setting("tab2_select_port")
        #     pass
        pass

    def show_data(self, data: list):
        # 显示数据
        logger.info(f"{self.objectName()}显示数据：{data}")
        if data is not None and len(data) != 0:
            match data['function_code']:
                case 1:
                    self.show_data_by_function_code_1(data['data'])
                    pass
                case 2:
                    self.show_data_by_function_code_2(data['data'])
                    pass
                case 3:
                    self.show_data_by_function_code_3(data['data'])
                    pass
                case 4:
                    self.show_data_by_function_code_4(data['data'])
                    pass
                case 17:  # 0x11的10进制就是17
                    self.show_data_by_function_code_17(data['data'])
                    pass
                case _:
                    pass
            pass

    def show_data_by_function_code_1(self, data):
        #  根据不同功能码显示数据
        function_group_box: QGroupBox = self.findChild(QGroupBox, 'function_01')
        function_layout: QVBoxLayout = self.findChild(QVBoxLayout, "function_01_layout")
        grid_layout: QGridLayout = self.findChild(QGridLayout, "function_01_gird_layout")
        if grid_layout is None:
            # 没有就新建
            # 创建一个 QScrollArea
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)  # 允许调整大小
            # 创建 QGridLayout
            grid_layout = QGridLayout()
            grid_layout.setContentsMargins(10, 20, 10, 10)
            grid_layout.setObjectName(f"function_01_gird_layout")
            # 3列 n行
            cols = 3
            rows = math.ceil(len(data) / cols)
            for row in range(rows):
                for col in range(cols):
                    if row * cols + col < len(data):
                        content_frame = QWidget()
                        content_frame_layout = QHBoxLayout()

                        desc_label = QLabel()
                        desc_label.setText(data[row * cols + col]['desc'] + ":")
                        value_label = QLabel()
                        value_label.setText(f"<span style='color: green;'>ON</span>"
                                            if data[row * cols + col][
                                                   'value'] == 1 else f"<span style='color: red;'>OFF</span>")
                        content_frame_layout.addWidget(desc_label)
                        content_frame_layout.addWidget(value_label)
                        content_frame.setLayout(content_frame_layout)

                        grid_layout.addWidget(content_frame, row, col)

            # 设置 QGroupBox 的布局为 QGridLayout
            function_group_box.setLayout(grid_layout)
            scroll_area.setWidget(function_group_box)
            function_layout.addWidget(scroll_area)
        else:
            # 有就修改值
            labels_layout = function_group_box.findChildren(QHBoxLayout)
            if labels_layout is not None and len(labels_layout) != 0:
                i = 0
                for label_layout in labels_layout:
                    labels = label_layout.parent().findChildren(QLabel)
                    if labels is not None and len(labels) != 0:
                        labels[0].setText(data[i]['desc'] + ":")
                        labels[1].setText(f"<span style='color: green;'>ON</span>"
                                          if data[i]['value'] == 1 else f"<span style='color: red;'>OFF</span>")
                        pass
                    i += 1

            pass
        pass

    def show_data_by_function_code_2(self, data):
        #  根据不同功能码显示数据
        function_group_box: QGroupBox = self.findChild(QGroupBox, 'function_02')
        function_layout: QVBoxLayout = self.findChild(QVBoxLayout, "function_02_layout")
        grid_layout: QGridLayout = self.findChild(QGridLayout, "function_02_gird_layout")
        if grid_layout is None:
            # 没有就新建
            # 创建一个 QScrollArea
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)  # 允许调整大小
            # 创建 QGridLayout
            grid_layout = QGridLayout()
            grid_layout.setContentsMargins(10, 20, 10, 10)
            grid_layout.setObjectName(f"function_02_gird_layout")
            # 3列 n行
            cols = 3
            rows = math.ceil(len(data) / cols)
            for row in range(rows):
                for col in range(cols):
                    if row * cols + col < len(data):
                        content_frame = QWidget()
                        content_frame_layout = QHBoxLayout()

                        desc_label = QLabel()
                        desc_label.setText(data[row * cols + col]['desc'] + ":")
                        value_label = QLabel()
                        value_label.setText(f"<span style='color: green;'>正常</span>"
                                            if data[row * cols + col][
                                                   'value'] == 1 else f"<span style='color: red;'>故障</span>")
                        content_frame_layout.addWidget(desc_label)
                        content_frame_layout.addWidget(value_label)
                        content_frame.setLayout(content_frame_layout)

                        grid_layout.addWidget(content_frame, row, col)

            # 设置 QGroupBox 的布局为 QGridLayout
            function_group_box.setLayout(grid_layout)
            scroll_area.setWidget(function_group_box)
            function_layout.addWidget(scroll_area)
        else:
            # 有就修改值
            labels_layout = function_group_box.findChildren(QHBoxLayout)
            if labels_layout is not None and len(labels_layout) != 0:
                i = 0
                for label_layout in labels_layout:
                    labels = label_layout.parent().findChildren(QLabel)
                    if labels is not None and len(labels) != 0:
                        labels[0].setText(data[i]['desc'] + ":")
                        labels[1].setText(f"<span style='color: green;'>正常</span>"
                                          if data[i]['value'] == 1 else f"<span style='color: red;'>故障</span>")
                        pass
                    i += 1

            pass
        pass

    def show_data_by_function_code_3(self, data):
        #  根据不同功能码显示数据
        function_group_box: QGroupBox = self.findChild(QGroupBox, 'function_03')
        function_layout: QVBoxLayout = self.findChild(QVBoxLayout, "function_03_layout")
        grid_layout: QGridLayout = self.findChild(QGridLayout, "function_03_gird_layout")
        if grid_layout is None:
            # 没有就新建
            # 创建一个 QScrollArea
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)  # 允许调整大小
            # 创建 QGridLayout
            grid_layout = QGridLayout()
            grid_layout.setContentsMargins(10, 20, 10, 10)
            grid_layout.setObjectName(f"function_03_gird_layout")
            # 3列 n行
            cols = 3
            rows = math.ceil(len(data) / cols)
            for row in range(rows):
                for col in range(cols):
                    if row * cols + col < len(data):
                        content_frame = QWidget()
                        content_frame_layout = QHBoxLayout()

                        desc_label = QLabel()
                        desc_label.setText(data[row * cols + col]['desc'] + ":")
                        value_label = QLabel()

                        value_label.setText(
                            f"{data[row * cols + col]['value']}%")

                        content_frame_layout.addWidget(desc_label)
                        content_frame_layout.addWidget(value_label)
                        content_frame.setLayout(content_frame_layout)

                        grid_layout.addWidget(content_frame, row, col)

            # 设置 QGroupBox 的布局为 QGridLayout
            function_group_box.setLayout(grid_layout)
            scroll_area.setWidget(function_group_box)
            function_layout.addWidget(scroll_area)
        else:
            # 有就修改值
            labels_layout = function_group_box.findChildren(QHBoxLayout)
            if labels_layout is not None and len(labels_layout) != 0:
                i = 0
                for label_layout in labels_layout:
                    labels = label_layout.parent().findChildren(QLabel)
                    if labels is not None and len(labels) != 0:
                        labels[0].setText(data[i]['desc'] + ":")
                        labels[1].setText(
                            f"{data[i]['value']}%")

                    i += 1

            pass
        pass

    def show_data_by_function_code_4(self, data):
        #  根据不同功能码显示数据
        function_group_box: QGroupBox = self.findChild(QGroupBox, 'function_04')
        function_layout: QVBoxLayout = self.findChild(QVBoxLayout, "function_04_layout")
        grid_layout: QGridLayout = self.findChild(QGridLayout, "function_04_gird_layout")
        if grid_layout is None:
            # 没有就新建
            # 创建一个 QScrollArea
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)  # 允许调整大小
            # 创建 QGridLayout
            grid_layout = QGridLayout()
            grid_layout.setContentsMargins(10, 20, 10, 10)
            grid_layout.setObjectName(f"function_04_gird_layout")
            # 3列 n行
            cols = 3
            rows = math.ceil(len(data) / cols)
            for row in range(rows):
                for col in range(cols):
                    if row * cols + col < len(data):
                        content_frame = QWidget()
                        content_frame_layout = QHBoxLayout()

                        desc_label = QLabel()
                        desc_label.setText(f"<span style=''>{data[row * cols + col]['desc']}:</span>")
                        value_label = QLabel()
                        value_label.setText(
                            f"<span style='font-weight: bold;font-size:17px;'>{data[row * cols + col]['value']}</span>")

                        content_frame_layout.addWidget(desc_label)
                        content_frame_layout.addWidget(value_label)
                        content_frame.setLayout(content_frame_layout)

                        grid_layout.addWidget(content_frame, row, col)

            # 设置 QGroupBox 的布局为 QGridLayout
            function_group_box.setLayout(grid_layout)
            scroll_area.setWidget(function_group_box)
            function_layout.addWidget(scroll_area)
        else:
            # 有就修改值
            labels_layout = function_group_box.findChildren(QHBoxLayout)
            if labels_layout is not None and len(labels_layout) != 0:
                i = 0
                for label_layout in labels_layout:
                    labels = label_layout.parent().findChildren(QLabel)
                    if labels is not None and len(labels) != 0:
                        labels[0].setText(f"<span style=''>{data[i]['desc']}:</span>")
                        labels[1].setText(f"<span style='font-weight: bold;font-size:17px;'>{data[i]['value']}</span>")
                        pass
                    i += 1

            pass
        pass

    def show_data_by_function_code_17(self, data):
        #  根据不同功能码显示数据
        function_group_box: QGroupBox = self.findChild(QGroupBox, 'function_11')
        function_layout: QVBoxLayout = self.findChild(QVBoxLayout, "function_11_layout")
        grid_layout: QGridLayout = self.findChild(QGridLayout, "function_11_gird_layout")
        if grid_layout is None:
            # 没有就新建
            # 创建一个 QScrollArea
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)  # 允许调整大小
            # 创建 QGridLayout
            grid_layout = QGridLayout()
            grid_layout.setContentsMargins(10, 20, 10, 10)
            grid_layout.setObjectName(f"function_11_gird_layout")
            # 3列 n行
            cols = 3
            rows = math.ceil(len(data) / cols)
            for row in range(rows):
                for col in range(cols):
                    if row * cols + col < len(data):
                        content_frame = QWidget()
                        content_frame_layout = QHBoxLayout()

                        desc_label = QLabel()
                        desc_label.setText(data[row * cols + col]['desc'] + ":")
                        value_label = QLabel()
                        value_label.setText(f"{data[row * cols + col]['value']}")

                        content_frame_layout.addWidget(desc_label)
                        content_frame_layout.addWidget(value_label)
                        content_frame.setLayout(content_frame_layout)

                        grid_layout.addWidget(content_frame, row, col)

            # 设置 QGroupBox 的布局为 QGridLayout
            function_group_box.setLayout(grid_layout)
            scroll_area.setWidget(function_group_box)
            function_layout.addWidget(scroll_area)
        else:
            # 有就修改值
            labels_layout = function_group_box.findChildren(QHBoxLayout)
            if labels_layout is not None and len(labels_layout) != 0:
                i = 0
                for label_layout in labels_layout:
                    labels = label_layout.parent().findChildren(QLabel)
                    if labels is not None and len(labels) != 0:
                        labels[0].setText(data[i]['desc'] + ":")
                        labels[1].setText(f"{data[i]['value']}")
                        pass
                    i += 1

            pass
        pass
        pass
