import sys

from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QPushButton

from config.global_setting import global_setting
from config.yamlParser import YamlParserObject
from index.mainWindow import MainWindow

from resource_py import mainPage_rc
from theme.ThemeManager import ThemeManager
from ui.customize_ui.left_menu_btn import Ui_left_menu_btn


###
# 显示窗口类 对主窗口进行相关加载ui 并可以显示
#
# ###
class AllWindows():
    # 实例化
    def __init__(self):
        self._init_ui()

        pass

    # 私有方法 load ui
    def _init_ui(self):
        # 主窗口实例化
        self.mainWindow = MainWindow(title=global_setting.get_setting("configer")['window']['title'])

        # 根据配置文件加载相应的ui
        self._generate()
        # # 根据样式风格设置公共样式
        # self._generate_style()
        pass

    # 私有方法 根据配置文件加载相应的ui
    def _generate(self):
        # 添加左侧菜单 从配置文件中
        self._set_left_menu_tab()
        # 给左侧菜单项按钮添加按钮鼠标按压悬浮样式
        self._set_btn_style_hover_pressed()
        # 从配置文件中配置程序logo信息
        self.mainWindow.setLogo(global_setting.get_setting("configer")['logo']['title'],
                                global_setting.get_setting("configer")['logo']['pict_path'],
                                global_setting.get_setting("configer")['logo']['pict_width'],
                                global_setting.get_setting("configer")['logo']['pict_height'])

    # def _generate_style(self):
    #     # 初始化主题
    #
    #     self.mainWindow.frame.setStyleSheet(global_setting.get_setting("theme_manager").get_style_sheet())
    #     # self.mainWindow.frame.setStyleSheet(
    #     #     global_setting.get_setting("style_sheet")[global_setting.get_setting("style")])
    #     pass

    #  私有方法 给左侧菜单项按钮添加按钮鼠标按压悬浮样式
    def _set_btn_style_hover_pressed(self):
        # 找到主窗口中的所有QPushButton对象
        pushBtns = self.mainWindow.frame.findChildren(QPushButton)
        # 给每个QPushButton对象 添加相关样式
        for btn in pushBtns:
            btn.setStyleSheet(Ui_left_menu_btn.hover_pressed_btn_qss)
        # 给默认菜单项设置样式
        default_id = 1
        for i in self.mainWindow.left_menu_btns:
            if i['visible']:
                default_id = i['id']
        default_menu_btn = self.mainWindow.frame.findChild(QPushButton, "btn" + str(default_id))
        default_menu_btn.setStyleSheet(Ui_left_menu_btn.selection_btn_qss + Ui_left_menu_btn.hover_pressed_btn_qss)

    # 私有方法 添加左侧菜单 从配置文件中
    def _set_left_menu_tab(self):
        # 通过配置信息 将左侧菜单按钮和tab进行绑定
        for i in self.mainWindow.left_menu_btns:
            self.mainWindow.set_child(child=i['tab'].frame,
                                      geometry=QtCore.QRect(
                                          global_setting.get_setting("configer")['tab']['position']['x'],
                                          global_setting.get_setting("configer")['tab']['position']['y'],
                                          global_setting.get_setting("configer")['tab']['position']['width'],
                                          global_setting.get_setting("configer")['tab']['position']['height']),
                                      visible=i['visible'])
            pass
        pass

    # 公共方法 显示窗口
    def show(self):
        self.mainWindow.show()
        pass
