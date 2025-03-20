import sys
import time
from datetime import datetime

from PyQt6 import uic, QtCore, QtWidgets, QtGui
from PyQt6.QtCore import QRect, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton

from config.global_setting import global_setting
from config.yamlParser import YamlParserObject
from index.tab import Tab
from resource_py import mainPage_rc
from theme.ThemeManager import ThemeManager
from theme.ThemeQt6 import ThemedWidget
from ui.customize_ui.left_menu_btn import Ui_left_menu_btn
from ui.main_window_ui import Ui_mainWindow


# 更新时间子线程
class Time_thread(QThread):
    # 线程信号
    update_time_thread_doing = pyqtSignal()

    def __init__(self, update_time_main_signal):
        super(Time_thread, self).__init__()
        # 获取主线程更新界面信号
        self.update_time_main_signal: pyqtSignal = update_time_main_signal
        pass

    def run(self):
        # 不断获取系统时间
        while True:
            # 实时获取当前时间（精确到微秒）
            current_time = datetime.now()

            # 转换为目标格式
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            # 将时间发送信号到绑定槽函数
            self.update_time_main_signal.emit(formatted_time)
            time.sleep(1)
            # print(formatted_time)
        pass

    pass


###
# 主窗口类
#
# ###
class MainWindow(QWidget, ThemedWidget):
    # update_time的更新界面的主信号
    update_time_main_signal_gui_update = pyqtSignal(str)

    # 实例化 参数 title 为 窗口title，
    def __init__(self, title=""):
        super().__init__()
        # 左侧菜单按钮
        self.left_menu_btns = []

        # 实例化ui
        self._init_ui(title)
        # 实例化自定义ui
        self._init_customize_ui()
        # 实例化功能
        self._init_function()
        pass

    # 实例化ui
    def _init_ui(self, title=""):
        # 将ui文件转成py文件后 直接实例化该py文件里的类对象  uic工具转换之后就是这一段代码
        self.frame = QWidget()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self.frame)

        self._retranslateUi(windows_title=global_setting.get_setting("configer")['window']['title'])
        pass

    # 实例化自定义ui
    def _init_customize_ui(self):
        #  实例化左侧菜单
        self._init_left_menu()
        pass

    # 实例化功能
    def _init_function(self):
        # 更新时间功能
        self.update_time_function_start()
        # 切换白天黑夜主题功能
        self.toggle_style_mode()
        pass

    #  实例化左侧菜单
    def _init_left_menu(self):
        #  获取菜单项配置信息
        menu_config = global_setting.get_setting("configer")['left_menu']
        for i in menu_config:
            btn_obj = {}
            # 实例化自定义菜单按钮
            bt = Ui_left_menu_btn(parentWidget=self.ui.left_layout_scroll_widget,
                                  parentLayout=self.ui.left_layout_scroll_widget_layout, id=i['id'],
                                  title=i['title'], icon_path=i['icon_path'],
                                  root_object_name=self.frame.objectName())
            # 添加按钮信号槽
            bt.click_connect(i['id'], self.frame, tab_ids=[item["id"] for item in menu_config])

            btn_obj['btn'] = bt
            btn_obj['id'] = i['id']
            btn_obj['tab'] = Tab(id=i['id'])
            btn_obj['visible'] = i['default']
            # 将菜单按钮对象放入数组中
            self.left_menu_btns.append(btn_obj)

            pass
        # 添加QT中的弹簧组件 将左侧菜单顶上去
        spacerItem = QtWidgets.QSpacerItem(20, 540, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.ui.left_layout_scroll_widget_layout.addItem(spacerItem)

        pass

    # 将ui文件转成py文件后 直接实例化该py文件里的类对象  uic工具转换之后就是这一段代码 应该是可以统一将文字改为其他语言
    def _retranslateUi(self, **kwargs):
        _translate = QtCore.QCoreApplication.translate
        self.frame.setWindowTitle(
            _translate(self.frame.objectName(), kwargs['windows_title'] if 'windows_title' in kwargs else ""))

    # 添加子UI组件
    def set_child(self, child: QWidget, geometry: QRect, visible: bool = True):
        # 添加子组件
        child.setParent(self.frame)
        # 添加子组件位置
        child.setGeometry(geometry)
        # 添加子组件可见性
        child.setVisible(visible)
        pass

    # 添加logo组件和信息
    def setLogo(self, logo_title='', logo_path="", logo_width=0, logo_height=0):
        _translate = QtCore.QCoreApplication.translate
        # Label组件添加文字
        self.ui.logolabel_btn.setText(_translate(self.frame.objectName(), logo_title))
        # lable中的icon实例化
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/" + logo_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.logolabel_btn.setIcon(icon)
        self.ui.logolabel_btn.setIconSize(QtCore.QSize(logo_width, logo_height))
        pass

    # 更新时间功能 信号
    def update_time_function_start(self):
        # 将更新时间信号绑定更新时间label界面函数
        self.update_time_main_signal_gui_update.connect(self.update_time_function_start_gui_update)
        # 启动子线程
        self.time_thread = Time_thread(update_time_main_signal=self.update_time_main_signal_gui_update)
        self.time_thread.start()

        pass

    # 更新时间功能 界面更新
    def update_time_function_start_gui_update(self, timeStr=""):
        #  获取控件
        time_label: QLabel = self.frame.findChild(QLabel, "time_label")
        # 设置文本
        time_label.setText(timeStr)
        pass

    # 切换白天黑夜主题功能
    def toggle_style_mode(self):
        _translate = QtCore.QCoreApplication.translate
        # 获取按钮组件
        style_btn = self.frame.findChild(QPushButton, "mode_btn")
        # 设置默认文字
        style_btn.setText(_translate(self.frame.objectName(), "白天模式" if global_setting.get_setting(
            "theme_manager").current_theme == "light" else "暗夜模式"))
        # 绑定事件
        style_btn.clicked.connect(self.toggle_theme)
        pass

    # 切换白天黑夜主题功能
    def toggle_theme(self):
        _translate = QtCore.QCoreApplication.translate
        # 获取按钮
        style_btn: QPushButton = self.frame.findChild(QPushButton, "mode_btn")
        # 根据当前主题变换主题
        new_theme = "dark" if global_setting.get_setting("theme_manager").current_theme == "light" else "light"
        # 将新主题关键字赋值回去
        global_setting.get_setting("theme_manager").current_theme = new_theme
        # 更改样式
        self.frame.setStyleSheet(global_setting.get_setting("theme_manager").get_style_sheet())
        # 按钮设置显示文字
        style_btn.setText(_translate(self.frame.objectName(), "白天模式" if global_setting.get_setting(
            "theme_manager").current_theme == "light" else "暗夜模式"))

        pass

    # 显示窗口
    def show(self):
        self.frame.show()
        pass
