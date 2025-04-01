# 自定义图表类
from PyQt6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6 import QtCore
from loguru import logger

from theme.ThemeQt6 import ThemedWidget


class charts(ThemedWidget):

    def __init__(self, parent):
        super().__init__()
        # 图表对象
        self.chart: QChart = None
        # 数据系列对象
        self.series: QLineSeries = None
        self._init_ui(parent=parent)

    def _init_ui(self, parent):
        # 创建布局和图表视图
        layout = QVBoxLayout(self)
        self.chart_view = QChartView()
        layout.addWidget(self.chart_view)
        layout.setParent(parent)
        # 初始化数据
        self._create_chart()

    def _create_chart(self):
        # 创建图表对象
        self.chart = QChart()
        self.chart.setTitle("自定义图表示例")

        # 添加数据系列
        self.series = QLineSeries()
        self.series.append(0, 5)
        self.series.append(1, 10)
        self.series.append(2, 15)
        self.chart.addSeries(self.series)

        # 添加到视图
        self.chart_view.setChart(self.chart)

    # 设置标题字体和颜色
    def set_title_style(self, font_style: QFont = QFont("Arial", 16, QFont.Weight.Bold),
                        font_color: QColor = "#2C3E50"):
        # 设置标题字体和颜色
        self.chart.setTitleFont(font_style)
        self.chart.setTitleBrush(font_color)  # 深蓝色

    # 设置x坐标轴样式
    def set_x_axis_style(self, root_object_name: str = "", x_axis_title: str = "x轴",
                         title_font_style: QFont = QFont("微软雅黑", 12),
                         labels_color: QColor = QColor("#34495E"), grid_line_color: QColor = QColor("#BDC3C7")):
        _translate = QtCore.QCoreApplication.translate
        x_axis = QValueAxis()
        x_axis.setTitleText(_translate(root_object_name, x_axis_title))
        x_axis.setTitleFont(title_font_style)
        x_axis.setLabelsColor(labels_color)  # 标签颜色
        x_axis.setGridLineColor(grid_line_color)  # 网格线颜色
        # 将坐标轴关联到图表
        self.chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(x_axis)

        pass

    # 设置y坐标轴样式
    def set_y_axis_style(self, root_object_name: str = "", y_axis_title: str = "y轴",
                         title_font_style: QFont = QFont("微软雅黑", 12),
                         labels_color: QColor = QColor("#34495E")):
        _translate = QtCore.QCoreApplication.translate
        y_axis = QValueAxis()
        y_axis.setTitleText(_translate(root_object_name, y_axis_title))
        y_axis.setTitleFont(title_font_style)
        y_axis.setLabelsColor(labels_color)  # 标签颜色
        # 将坐标轴关联到图表
        self.chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(y_axis)
        pass
