# 自定义图表类
from PyQt6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6 import QtCore
from loguru import logger

from config.global_setting import global_setting
from theme.ThemeQt6 import ThemedWidget


class charts(ThemedWidget):

    def __init__(self, parent: QVBoxLayout = None, object_name: str = ""):
        super().__init__()
        # obejctName
        self.object_name = object_name
        # 父布局
        self.parent_layout = parent
        # 图表对象
        self.chart: QChart = None
        # 数据系列对象
        self.series: QLineSeries = None
        # x轴
        self.x_axis: QValueAxis = None
        # y轴
        self.y_axis: QValueAxis = None
        self._init_ui()
        # 设置样式
        self.set_style()

    def _init_ui(self):
        # 创建布局和图表视图
        self.chart_view = QChartView()
        self.chart_view.setObjectName(f"{self.object_name}")
        self.parent_layout.addWidget(self.chart_view)

        # 初始化数据
        self._init_chart()

    def _init_chart(self):
        # 创建图表对象
        self.chart = QChart()
        self.chart.setObjectName(f"{self.object_name}_chart")
        self.chart.setTitle("自定义图表示例")

        # 添加数据系列
        self.series = QLineSeries()
        self.series.setObjectName(f"{self.object_name}_series")
        self.series.setName("测试")
        self.series.append(0, 5)
        self.series.append(1, 10)
        self.series.append(2, 15)
        self.chart.addSeries(self.series)
        # 设置坐标轴
        self._set_x_axis()
        self._set_y_axis()
        # 添加到视图
        self.chart_view.setChart(self.chart)

    # 设置x轴
    def _set_x_axis(self):
        # 将坐标轴关联到图表
        self.x_axis = QValueAxis()
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.x_axis)
        pass

    # 设置y轴
    def _set_y_axis(self):
        # 将坐标轴关联到图表
        self.y_axis = QValueAxis()
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.y_axis)
        pass

    # 设置标题字体和颜色
    def set_title_style(self, font_style: QFont = QFont("Arial", 8, QFont.Weight.Bold),
                        font_color: QColor = QColor("#2C3E50")):
        # 设置标题字体和颜色
        self.chart.setTitleFont(font_style)
        self.chart.setTitleBrush(QBrush(font_color))  # 深蓝色

    # 设置x坐标轴样式
    def set_x_axis_style(self, root_object_name: str = "", x_axis_title: str = "x",
                         title_font_style: QFont = QFont("微软雅黑", 6),
                         labels_color: QColor = QColor("#34495E"), grid_line_color: QColor = QColor("#BDC3C7")):
        _translate = QtCore.QCoreApplication.translate

        self.x_axis.setTitleText(_translate(root_object_name, x_axis_title))
        self.x_axis.setTitleFont(title_font_style)
        self.x_axis.setLabelsColor(labels_color)  # 标签颜色
        self.x_axis.setGridLineColor(grid_line_color)  # 网格线颜色
        pass

    # 设置y坐标轴样式
    def set_y_axis_style(self, root_object_name: str = "", y_axis_title: str = "y",
                         title_font_style: QFont = QFont("微软雅黑", 6),
                         labels_color: QColor = QColor("#34495E")):
        _translate = QtCore.QCoreApplication.translate
        self.y_axis.setTitleText(_translate(root_object_name, y_axis_title))
        self.y_axis.setTitleFont(title_font_style)
        self.y_axis.setLabelsColor(labels_color)  # 标签颜色
        pass

    # 设置样式
    def set_style(self):
        theme = global_setting.get_setting("theme_manager").get_themes_color(mode=1)
        self.chart.setPlotAreaBackgroundBrush(QBrush(QColor(theme['--secondary'])))
        self.chart.setBackgroundBrush(QBrush(QColor(theme['--secondary'])))
        self.series.setColor(QColor(theme['--text_hover']))
        self.set_title_style(font_color=QColor(theme['--text']))
        self.set_x_axis_style(labels_color=QColor(theme['--text']), grid_line_color=QColor(theme['--text']))
        self.set_y_axis_style(labels_color=QColor(theme['--text']))
        pass
