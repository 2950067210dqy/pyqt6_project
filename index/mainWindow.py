import sys
import time
from datetime import datetime

from PyQt6 import uic, QtCore, QtWidgets, QtGui
from PyQt6.QtCore import QRect, QThread, pyqtSignal, QFile
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton
from loguru import logger

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

class MainWindow(ThemedWidget):
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
        # 加载qss样式表
        self._init_style_sheet()
        self.init_icon_style()
        pass

    # 实例化ui
    def _init_ui(self, title=""):
        # 将ui文件转成py文件后 直接实例化该py文件里的类对象  uic工具转换之后就是这一段代码

        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self._retranslateUi(windows_title=global_setting.get_setting("configer")['window']['title'])
        pass

    # 实例化自定义ui
    def _init_customize_ui(self):

        #  实例化左侧菜单
        self._init_left_menu()
        pass

    # 实例化图标样式
    def init_icon_style(self):
        # 找到主窗口中的所有QPushButton对象
        pushBtns = self.findChildren(QPushButton)
        # 给每个QPushButton对象 添加相关样式 并且更换icon样式 start
        for btn in pushBtns:
            # 更换图标样式 start
            # 更换左侧菜单图标样式
            if btn.property("icon_name") != None:
                icon_name = btn.property("icon_name")
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(f":/{global_setting.get_setting('style')}/{icon_name}"),
                               QtGui.QIcon.Mode.Normal,
                               QtGui.QIcon.State.Off)
                btn.setIcon(icon)
                btn.setIconSize(QtCore.QSize(20, 20))
            # 更换其他按钮图标样式
            else:
                #  获得其他图标的objectname的前缀 注意我们的带有图标的QPushButton的ObjectName的前缀必须要和我们所设置得图标文件的名字一样，否则这里将不起效果
                other_btn_object_name_prefix = btn.objectName().split("_")[0]
                # 导出的图标不进行处理
                if other_btn_object_name_prefix !="export":
                    path = f":/{global_setting.get_setting('style')}/{other_btn_object_name_prefix}.svg"
                    # 找不到图标文件就写进日志
                    if not QFile.exists(path):
                        logger.warning(f"{btn.objectName()} button's icon resource file was not found！")
                    # 否则就更新图标
                    else:
                        icon = QtGui.QIcon()
                        icon.addPixmap(QtGui.QPixmap(path),
                                       QtGui.QIcon.Mode.Normal,
                                       QtGui.QIcon.State.Off)
                        btn.setIcon(icon)
                        btn.setIconSize(QtCore.QSize(20, 20))
            # 给每个QPushButton对象 添加相关样式
            btn.setStyleSheet(global_setting.get_setting("theme_manager").get_button_style(isSelected=False))
        pass

    # 实例化功能
    def _init_function(self):
        # 更新时间功能
        self.update_time_function_start()
        # 切换白天黑夜主题功能
        self.toggle_style_mode()
        # logo按钮返回主页功能
        self.logo_return_default_page()
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
                                  root_object_name=self.objectName())
            # 添加按钮信号槽
            bt.click_connect(i['id'], self, tab_ids=[item["id"] for item in menu_config])

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
        self.setWindowTitle(
            _translate(self.objectName(), kwargs['windows_title'] if 'windows_title' in kwargs else ""))

    # 添加logo组件和信息
    def setLogo(self, logo_title='', logo_path="", logo_width=0, logo_height=0):
        _translate = QtCore.QCoreApplication.translate
        # Label组件添加文字
        self.ui.logolabel_btn.setText(_translate(self.objectName(), logo_title))
        # lable中的icon实例化
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./resource/" + logo_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.ui.logolabel_btn.setIcon(icon)
        self.ui.logolabel_btn.setIconSize(QtCore.QSize(logo_width, logo_height))
        pass

    # 更新时间功能 信号
    def update_time_function_start(self):
        # 将更新时间信号绑定更新时间label界面函数
        self.update_time_main_signal_gui_update.connect(self.update_time_function_start_gui_update)
        # 启动子线程
        self.time_thread = Time_thread(update_time_main_signal=self.update_time_main_signal_gui_update)
        logger.info("time update thread start")
        self.time_thread.start()

        pass

    # 更新时间功能 界面更新
    def update_time_function_start_gui_update(self, timeStr=""):
        #  获取控件
        time_label: QLabel = self.findChild(QLabel, "time_label")
        # 设置文本
        time_label.setText(timeStr)
        pass

    # 切换白天黑夜主题功能
    def toggle_style_mode(self):
        _translate = QtCore.QCoreApplication.translate
        # 获取按钮组件
        style_btn = self.findChild(QPushButton, "mode_btn")
        # 设置默认文字
        style_btn.setText(_translate(self.objectName(), "白天模式" if global_setting.get_setting(
            "style") == "light" else "暗夜模式"))
        # 绑定事件
        style_btn.clicked.connect(self.toggle_theme)
        pass

    # 切换白天黑夜主题功能
    def toggle_theme(self):
        _translate = QtCore.QCoreApplication.translate
        # 获取按钮
        style_btn: QPushButton = self.findChild(QPushButton, "mode_btn")
        # 根据当前主题变换主题

        new_theme = "dark" if global_setting.get_setting("theme_manager").current_theme == "light" else "light"
        # 将新主题关键字赋值回去
        global_setting.set_setting('style', new_theme)
        global_setting.get_setting("theme_manager").current_theme = new_theme
        # 更改样式
        self.setStyleSheet(global_setting.get_setting("theme_manager").get_style_sheet())

        # 更改自定义组件样式
        # 更改图标样式
        self.init_icon_style()
        # 给默认菜单项设置样式
        default_menu_btn = self.findChild(QPushButton, "btn" + str(global_setting.get_setting("menu_id_now")))
        default_menu_btn.setStyleSheet(
            global_setting.get_setting("theme_manager").get_button_style(isSelected=True))
        # 给每个QPushButton对象 添加相关样式 end

        # 给图表进行主题更新 每个tab里的图表都更新
        for menu in self.left_menu_btns:

            tab = menu['tab']
            # 给tab2页面进行按钮样式更新信号
            if menu['id'] == 2:
                tab.tab.update_btn_css_signal.emit()
            # 找到每个chart对象
            if 'charts_list' not in tab.tab.__dict__:
                logger.warning(f"menu{menu['id']}'s tab page not exists charts_list ！")
                continue
            charts = tab.tab.charts_list

            for chart in charts:
                chart.set_style()
        # 按钮设置显示文字
        style_btn.setText(_translate(self.objectName(), "白天模式" if global_setting.get_setting(
            "theme_manager").current_theme == "light" else "暗夜模式"))

        pass

    # logo按钮返回主页功能
    def logo_return_default_page(self):
        # 获取按钮组件
        logo_label_btn = self.findChild(QPushButton, "logolabel_btn")
        # 绑定事件
        logo_label_btn.clicked.connect(self.logo_return_default_page_click_method)

    # logo按钮返回主页功能 按钮绑定事件
    def logo_return_default_page_click_method(self):
        # 找到默认菜单按钮
        default_btn_id = next(x['id'] for x in self.left_menu_btns if x['visible'])
        # 找到与之对应的tab组件
        base_objectname_pre = "tab"
        base_objectname_suff = "_frame"
        current_tab = self.findChild(QtWidgets.QWidget,
                                     base_objectname_pre + str(default_btn_id) + base_objectname_suff)
        # 并将tab页设为可见
        current_tab.setVisible(True)
        # 找到所有的菜单按钮的id
        tab_ids = [x['id'] for x in self.left_menu_btns]
        # 将其他tab页设为不可见
        for i in tab_ids:
            if i != default_btn_id:
                other_tab = self.findChild(QtWidgets.QWidget,
                                           base_objectname_pre + str(i) + base_objectname_suff)
                other_tab.setVisible(False)
        # 更改当前按钮的样式
        base_objectname_pre_btn = "btn"
        current_btn = self.findChild(QtWidgets.QPushButton, base_objectname_pre_btn + str(default_btn_id))
        current_btn.setStyleSheet(global_setting.get_setting("theme_manager").get_button_style(isSelected=True))
        # 更改其他按钮的样式
        for i in tab_ids:
            if i != default_btn_id:
                other_btn = self.findChild(QtWidgets.QPushButton, base_objectname_pre_btn + str(i))
                other_btn.setStyleSheet(global_setting.get_setting("theme_manager").get_button_style(isSelected=False))
        pass
