from PyQt6.QtCore import QRect
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6 import QtCore

from loguru import logger

from config.global_setting import global_setting

from theme.ThemeManager import ThemeManager


class ThemedWidget(QWidget):
    """混入类实现主题响应"""

    def __init__(self):
        super().__init__()

        global_setting.get_setting("theme_manager").theme_changed.connect(self._update_theme)
        self._init_style_sheet()

    # 加载qss样式
    def _init_style_sheet(self):
        # if hasattr(self, ("frame")) and self.frame != None:
        self.setStyleSheet(global_setting.get_setting("theme_manager").get_style_sheet())

    def _update_theme(self):
        self._init_style_sheet()
        self.setStyleSheet(global_setting.get_setting("theme_manager").get_style_sheet())

    # 将ui文件转成py文件后 直接实例化该py文件里的类对象  uic工具转换之后就是这一段代码 应该是可以统一将文字改为其他语言
    def _retranslateUi(self, **kwargs):
        _translate = QtCore.QCoreApplication.translate

    # 添加子UI组件
    def set_child(self, child: QWidget, geometry: QRect, visible: bool = True):
        # 添加子组件
        child.setParent(self)
        # 添加子组件位置
        child.setGeometry(geometry)
        # 添加子组件可见性
        child.setVisible(visible)
        pass

    def get_ancestor(self, ancestor_obj_name):
        # 获取当前对象的祖先对象
        ancestor = self
        while ancestor is not None and ancestor.objectName() != ancestor_obj_name:
            ancestor = ancestor.parent()
        if ancestor == self:
            logger.info(f"{self.objectName()}没有祖先组件")
        elif ancestor is None:
            logger.info(f"{self.objectName()}未找到祖先{ancestor_obj_name}")
        else:
            logger.info(f"{self.objectName()}找到祖先{ancestor_obj_name}")
        self.ancestor = ancestor

    # 显示窗口
    def show_frame(self):
        self.show()
        pass


class ThemeIconButton(QPushButton):
    def __init__(self, icon_name):
        super().__init__()
        self.icon_name = icon_name
        self.update_icon()

    def update_icon(self):
        path = f":/{global_setting.get_setting('style')}/{self.icon_name}.svg"
        self.setIcon(QIcon(path))
