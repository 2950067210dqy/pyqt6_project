import typing

from loguru import logger

from theme.ThemeQt6 import ThemedWidget
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget, QMainWindow

from theme.ThemeQt6 import ThemedWidget
from ui.tab7 import Ui_tab7_frame


class Tab_7(ThemedWidget):
    def showEvent(self, a0: typing.Optional[QtGui.QShowEvent]) -> None:
        # 加载qss样式表
        logger.warning("tab7——show")

    def hideEvent(self, a0: typing.Optional[QtGui.QHideEvent]) -> None:
        logger.warning("tab7--hide")

    def __init__(self, parent=None, geometry: QRect = None, title=""):
        super().__init__()
        # 类型 0 是Qframe 1是Qmainwindow
        self.type = 1
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
        self.ui = Ui_tab7_frame()
        self.ui.setupUi(self)

        self._retranslateUi()
        pass

    # 实例化自定义ui
    def _init_customize_ui(self):
        pass

    # 实例化功能
    def _init_function(self):
        pass
