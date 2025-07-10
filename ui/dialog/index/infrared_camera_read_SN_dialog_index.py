import traceback
import typing
from queue import Queue

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QRect, Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QDialog, QComboBox, QLabel, QPushButton, QDialogButtonBox
from loguru import logger

from config.global_setting import global_setting
from entity.MyQThread import MyQThread
from equipment.infrared_camera.senxor.utils import query_devices, query_single_devices

from theme.ThemeQt6 import ThemedWidget

import pyrealsense2 as rs

from ui.dialog.infrared_camera_config_dialog import Ui_infrared_camera_config_dialog
from ui.dialog.infrared_camera_read_SN_dialog import Ui_infrared_camera_seting_dialog
from util.folder_util import folder_util
from util.json_util import json_util



class infrared_camera_read_SN_dialog(QDialog):
    """

    """


    def scan_realsense(self):  # 搜索相机
        global_setting.get_setting("queue").put({'data': 'stop', 'to': 'main_infrared_camera'})
        device = query_single_devices()

        return device

    def showEvent(self, a0: typing.Optional[QtGui.QShowEvent]) -> None:
        # 加载qss样式表
        logger.warning("tab7——show")

    def hideEvent(self, a0: typing.Optional[QtGui.QHideEvent]) -> None:
        logger.warning("tab7--hide")

    def __init__(self, parent=None, geometry: QRect = None, title=""):
        super().__init__()
        # 相机序列号数据
        self.camera_series=''
        # 显示数据框
        self.show_label: QLabel = None
        # 刷新按钮
        self.refresh_btn: QPushButton = None
        # ok按钮
        self.ok_btn: QPushButton = None

        # 获得数据
        self.SN=self.get_data()
        # 实例化ui
        self._init_ui(parent, geometry, title)
        # 实例化自定义ui
        self._init_customize_ui()

        # 实例化功能
        self._init_function()

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
        self.ui = Ui_infrared_camera_seting_dialog()
        self.ui.setupUi(self)
        # 窗口总是在最顶层
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        # 隐藏右上角的关闭按钮
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.setModal(True)
        self.setWindowTitle(title)
        pass


        pass

    def get_data(self):
        return self.scan_realsense()

        pass

    # 实例化自定义ui
    def _init_customize_ui(self):
        self.show_label: QLabel = self.findChild(QLabel, "show_label")
        self.show_label.setText(f"{self.SN}")
        # 获取 OK 按钮的引用
        button_box = self.findChild(QDialogButtonBox, "dialog_btn")
        if button_box is not None:
            self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        # 获取 REFRESH 按钮的引用
        self.refresh_btn = self.findChild(QPushButton, "refresh")
        pass

    # 实例化功能
    def _init_function(self):
        # 其他的按钮事件连接
        if self.ok_button is not None:
            self.ok_button.clicked.connect(self.ok_func)
        if self.refresh_btn is not None:
            self.refresh_btn.clicked.connect(self.refresh_func)
        pass

    def show_frame(self):

        self.show()



    def refresh_func(self):
        """
        refresh按钮事件
        :return:
        """
        self.SN=self.get_data()
        self.show_label.setText(f"{self.SN}")


    def ok_func(self):
        """
        ok按钮事件
        :return:
        """

        pass
