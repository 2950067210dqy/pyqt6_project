import sys

from PyQt6 import uic, QtCore
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget
from loguru import logger

from index.tab_1 import Tab_1
from index.tab_2 import Tab_2
from index.tab_3 import Tab_3
from index.tab_4 import Tab_4
from index.tab_5 import Tab_5
from index.tab_6 import Tab_6
from resource_py import mainPage_rc
from theme.ThemeQt6 import ThemedWidget


# 左侧菜单按钮控制的菜单窗口类

class Tab(ThemedWidget):
    # 不同的菜单窗口类
    classes = [Tab_1, Tab_2, Tab_3, Tab_4, Tab_5, Tab_6]

    # 实例化
    def __init__(self, parent=None, geometry: QRect = None, title="", id=1):
        super().__init__()
        # 实例化ui
        self._init_ui(parent, geometry, title, id)
        pass

    # 实例化ui
    def _init_ui(self, parent=None, geometry: QRect = None, title="", id=1):
        # 根据 id 绑定相应的菜单窗口
        self.tab = Tab.classes[id - 1]()
        # self.tab = Tab_1()
