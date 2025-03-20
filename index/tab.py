import sys

from PyQt6 import uic, QtCore
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget
from resource_py import mainPage_rc
from theme.ThemeQt6 import ThemedWidget
from ui.tab1 import Ui_tab1_frame
from ui.tab2 import Ui_tab2_frame
from ui.tab3 import Ui_tab3_frame
from ui.tab4 import Ui_tab4_frame
from ui.tab5 import Ui_tab5_frame
from ui.tab6 import Ui_tab6_frame


# 左侧菜单按钮控制的菜单窗口类
class Tab(QWidget, ThemedWidget):
    # 不同的菜单窗口类
    classes = [Ui_tab1_frame, Ui_tab2_frame, Ui_tab3_frame, Ui_tab4_frame, Ui_tab5_frame, Ui_tab6_frame]

    # 实例化
    def __init__(self, parent=None, geometry: QRect = None, title="", id=1):
        super().__init__()
        # 实例化ui
        self._init_ui(parent, geometry, title, id)
        pass

    # 实例化ui
    def _init_ui(self, parent=None, geometry: QRect = None, title="", id=1):
        # 有父窗口添加父窗口
        if parent != None and geometry != None:
            self.frame = QWidget(parent=parent)
            self.frame.setGeometry(geometry)
        else:
            self.frame = QWidget()
        # 根据 id 绑定相应的菜单窗口
        self.ui = Tab.classes[id - 1]()
        # self.ui = Ui_tab2_frame()
        self.ui.setupUi(self.frame)
        self._retranslateUi(windows_title=title)

    def _retranslateUi(self, **kwargs):
        _translate = QtCore.QCoreApplication.translate
        self.frame.setWindowTitle(
            _translate(self.frame.objectName(), kwargs['windows_title'] if 'windows_title' in kwargs else ""))

    # 添加子组件
    def set_child(self, child: QWidget, geometry: QRect, visible: bool = True):
        child.setParent(self.frame)
        child.setGeometry(geometry)
        child.setVisible(visible)
        pass

    # 显示窗口
    def show(self):
        self.frame.show()
