from loguru import logger
from pyqt6_plugins.examplebutton import QtWidgets

from config.global_setting import global_setting
from theme.ThemeQt6 import ThemedWidget
from ui.customize_ui.tab.tab2_tab0 import tab2_tab0
from ui.customize_ui.tab.tab2_tab1 import tab2_tab1
from ui.tab2 import Ui_tab2_frame
from PyQt6 import QtCore
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from theme.ThemeQt6 import ThemedWidget


class Tab_2(ThemedWidget):
    # 不同的tab的frame
    classes = [tab2_tab0, tab2_tab1]

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
        self.ui = Ui_tab2_frame()
        self.ui.setupUi(self.frame)

        self._retranslateUi()
        pass

    # 实例化自定义ui
    def _init_customize_ui(self):
        # 根据监测数据项配置tab页
        self._init_monitor_data_tab_page()
        pass

    # 根据监测数据项配置tab页
    def _init_monitor_data_tab_page(self):
        # tab页布局
        content_layout_son: QVBoxLayout = self.frame.findChild(QVBoxLayout, "content_layout_son")
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setObjectName("tab_2_tabWidget")
        self.tabWidget.setStyleSheet("")
        monitor_data_tab_page_config = global_setting.get_setting("configer")['monitoring_data']
        for monitor_data in monitor_data_tab_page_config:
            tab = QtWidgets.QWidget()
            tab.setObjectName(f"tab_{monitor_data['id'] - 1}_{monitor_data['object_name']}")
            # 绑定相关的tab页
            tab_frame = self.classes[monitor_data['id'] - 1]()
            if hasattr(tab_frame, 'set_parent') and callable(getattr(tab_frame, 'set_parent')):
                tab_frame.set_parent(parent=tab)
            else:
                tab_frame.setupUi(tab)
            self.tabWidget.addTab(tab, monitor_data['title'])
            pass
            pass
        content_layout_son.addWidget(self.tabWidget)

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
