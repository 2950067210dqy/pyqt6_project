from PyQt6 import QtCore
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from loguru import logger

from theme.ThemeQt6 import ThemedWidget
from ui.customize_ui import customize_charts
from ui.customize_ui.customize_charts import charts
from ui.tab1 import Ui_tab1_frame


class Tab_1(ThemedWidget):
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
        # 加载qss样式表
        self._init_style_sheet()
        pass

        # 实例化ui

    def _init_ui(self, parent=None, geometry: QRect = None, title=""):
        # 将ui文件转成py文件后 直接实例化该py文件里的类对象  uic工具转换之后就是这一段代码
        # 有父窗口添加父窗口
        if parent != None and geometry != None:
            self.frame = QWidget(parent=parent)
            self.frame.setGeometry(geometry)
        else:
            self.frame = QWidget()
        self.ui = Ui_tab1_frame()
        self.ui.setupUi(self.frame)

        self._retranslateUi()
        pass

    # 实例化自定义ui
    @logger.catch
    def _init_customize_ui(self):
        # 图表 左下布局
        frame_left_bottom = self.frame.findChild(QVBoxLayout, "frame2_contentlayout")
        charts_left_bottom_1 = charts(parent=frame_left_bottom, object_name="charts_tab1_left_bottom_1")
        # charts_left_bottom_2 = charts(parent=frame_left_bottom, object_name="charts_tab1_left_bottom_2")
        # charts_left_bottom_3 = charts(parent=frame_left_bottom, object_name="charts_tab1_left_bottom_3")
        # 图表 右边布局
        frame_right = self.frame.findChild(QVBoxLayout, "frame3_contentlayout")
        charts_right_1 = charts(parent=frame_right, object_name="charts_tab1_right_1")
        charts_right_2 = charts(parent=frame_right, object_name="charts_tab1_right_2")
        charts_right_3 = charts(parent=frame_right, object_name="charts_tab1_right_3")
        self.charts_list.append(charts_left_bottom_1)
        self.charts_list.append(charts_right_1)
        self.charts_list.append(charts_right_2)
        self.charts_list.append(charts_right_3)
        pass

    # 实例化功能
    def _init_function(self):
        pass

    # 将ui文件转成py文件后 直接实例化该py文件里的类对象  uic工具转换之后就是这一段代码 应该是可以统一将文字改为其他语言
    def _retranslateUi(self, **kwargs):
        _translate = QtCore.QCoreApplication.translate

    # 添加子组件
    def set_child(self, child: QWidget, geometry: QRect, visible: bool = True):
        child.setParent(self.frame)
        child.setGeometry(geometry)
        child.setVisible(visible)
        pass

    # 显示窗口
    def show(self):
        self.frame.show()
        pass
