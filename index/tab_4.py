from datetime import datetime

from PyQt6.QtGui import QPixmap
from loguru import logger

from config.global_setting import global_setting
from dao.data_read import data_read
from theme.ThemeQt6 import ThemedWidget
from PyQt6 import QtCore
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QPushButton, \
    QLabel

from theme.ThemeQt6 import ThemedWidget
from ui.tab4 import Ui_tab4_frame
from util.folder_util import File_Types


class Tab_4(ThemedWidget):

    def __init__(self, parent=None, geometry: QRect = None, title=""):
        super().__init__()
        # 图像列表
        self.charts_list = []
        self.data = None
        # 数据获取器
        self.data_read = data_read(file_type=File_Types.GRAPHY.value,
                                   data_origin_port=["COM3"])
        # 实例化ui
        self._init_ui(parent, geometry, title)
        # 实例化自定义ui
        self._init_customize_ui()
        # 获取数据
        # self.get_data()
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
        self.ui = Ui_tab4_frame()
        self.ui.setupUi(self.frame)

        self._retranslateUi()
        pass

        pass

    def get_data(self):
        self.data = self.data_read.read_service.get_data_image(times=datetime.now(), data_origin_port="COM3")
        pass

    # 实例化自定义ui
    def _init_customize_ui(self):
        self.init_btn_label()
        if self.data != None and len(self.data) != 0:
            self.init_graphy()

        pass

    def init_btn_label(self):
        """
        初始化按钮和label的初始信息
        :return:
        """
        start_btn: QPushButton = self.frame.findChild(QPushButton, "start_btn")
        stop_btn: QPushButton = self.frame.findChild(QPushButton, "stop_btn")
        state_label: QLabel = self.frame.findChild(QLabel, "state_label")
        start_btn.setDisabled(False)
        stop_btn.setDisabled(True)
        state_label.setText("未连接")

        pass

    def init_graphy(self):
        """
        实例化图片组件
        :return:
        """
        self.parent_layout = self.frame.findChild(QHBoxLayout, "tab4_layout")
        self.graphics_view_list = self.frame.findChildren(QGraphicsView)
        graphics_view_left = []
        graphics_view_right = []
        for i in range(len(self.graphics_view_list)):
            logger.info(self.graphics_view_list[i].objectName())
            if "left" in self.graphics_view_list[i].objectName():
                logger.error(f"left{i}")

                graphics_view_left.append(self.graphics_view_list[i])
                # 自动缩放视图，使图片完全显示，保持宽高比
                # self.graphics_view_list[i].fitInView(pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
                pass
            elif "right" in self.graphics_view_list[i].objectName():
                logger.error(f"right{i}")

                graphics_view_right.append(self.graphics_view_list[i])
                # 自动缩放视图，使图片完全显示，保持宽高比
                # self.graphics_view_list[i].fitInView(pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
                pass
            else:
                pass
            self.graphics_view_list[i].setDragMode(QGraphicsView.DragMode.ScrollHandDrag)  # 开启拖拽模式
        for i in range(len(graphics_view_left)):
            scene = QGraphicsScene()
            # 按比例缩放到目标宽高内
            if len(self.data[0]['data']) != 0:
                scaled_pixmap = self.data[0]['data'][i].scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            else:
                scaled_pixmap = QPixmap()
            pixmap_item = QGraphicsPixmapItem(scaled_pixmap)
            scene.addItem(pixmap_item)

            # 设置场景给视图
            graphics_view_left[i].setScene(scene)

        for i in range(len(graphics_view_right)):
            scene = QGraphicsScene()
            # 按比例缩放到目标宽高内
            if len(self.data[1]['data']) != 0:
                scaled_pixmap = self.data[1]['data'][i].scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            else:
                scaled_pixmap = QPixmap()
            pixmap_item = QGraphicsPixmapItem(scaled_pixmap)
            scene.addItem(pixmap_item)

            # 设置场景给视图
            graphics_view_right[i].setScene(scene)

            # # 可选：关闭滚动条，避免出现滚动条
            # self.graphics_view_list[i].setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            # self.graphics_view_list[i].setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    # 实例化功能
    def _init_function(self):
        self.init_btn_handle()
        pass

    def init_btn_handle(self):
        """
        将按钮绑定功能函数
        """
        # 找到两个按钮 和状态显示label
        start_btn = self.frame.findChild(QPushButton, "start_btn")
        stop_btn = self.frame.findChild(QPushButton, "stop_btn")
        state_label: QLabel = self.frame.findChild(QLabel, "state_label")
        # 绑定功能
        start_btn.clicked.connect(lambda: self.start_btn_func(start_btn, stop_btn, state_label))
        stop_btn.clicked.connect(lambda: self.stop_btn_func(start_btn, stop_btn, state_label))
        pass

    def start_btn_func(self, start_btn: QPushButton, stop_btn: QPushButton, state_label: QLabel):
        """
        开始按钮的函数
        :return:
        """

        state_label.setText("已连接")
        stop_btn.setDisabled(False)
        start_btn.setDisabled(True)

        pass

    def stop_btn_func(self, start_btn: QPushButton, stop_btn: QPushButton, state_label: QLabel):
        """
        停止按钮的函数
        :return:
        """
        state_label.setText("未连接")
        stop_btn.setDisabled(True)
        start_btn.setDisabled(False)
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
