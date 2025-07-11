import sys

from PyQt6 import uic, QtCore
from PyQt6.QtWidgets import QPushButton
from loguru import logger

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

    #  私有方法 给左侧菜单项按钮添加按钮鼠标按压悬浮样式
    def _set_btn_style_hover_pressed(self):
        # # 找到主窗口中的所有QPushButton对象
        # pushBtns = self.mainWindow.findChildren(QPushButton)
        # # 给每个QPushButton对象 添加相关样式
        # for btn in pushBtns:
        #     btn.setStyleSheet(global_setting.get_setting("theme_manager").get_button_style(isSelected=False))
        # 给默认菜单项设置样式
        default_menu_btn = self.mainWindow.findChild(QPushButton,
                                                     "btn" + str(global_setting.get_setting("menu_id_now")))
        default_menu_btn.setStyleSheet(global_setting.get_setting("theme_manager").get_button_style(isSelected=True))

    # 私有方法 添加左侧菜单 从配置文件中
    def _set_left_menu_tab(self):
        # 通过配置信息 将左侧菜单按钮和tab进行绑定
        for i in self.mainWindow.left_menu_btns:
            # 设置当前选中菜单id到全局类中
            if i['visible']:
                global_setting.set_setting("menu_id_now", i['id'])
            self.mainWindow.set_child(child=i['tab'].tab,
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
        self.mainWindow.show_frame()
        pass
