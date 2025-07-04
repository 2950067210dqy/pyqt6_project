import importlib
import sys

from PyQt6 import uic, QtCore
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget, QMainWindow
from loguru import logger

from smart_device.index.tab_7 import Tab_7

from smart_device.theme.ThemeQt6 import ThemedWidget

# 左侧菜单按钮控制的菜单窗口类
from util.class_util import class_util


class Tab(ThemedWidget):
    # 不同的菜单窗口类
    classes = [Tab_7]

    # 实例化
    def __init__(self, parent=None, geometry: QRect = None, title="", id=1):
        super().__init__()
        # 实例化ui
        # self.classes = class_util.get_class_obj_from_modules_names(path="./smart_device/index/", mapping="Tab_")
        self._init_ui(parent, geometry, title, id)
        pass

    # 实例化ui
    def _init_ui(self, parent=None, geometry: QRect = None, title="", id=1):
        # 根据 id 绑定相应的菜单窗口
        self.tab = self.classes[id - 1]()

        self.tab.frame.setWindowTitle(title)
        self.tab.frame.setGeometry(geometry)

        # self.tab = Tab_1()

    def show(self):
        self.tab.show()
