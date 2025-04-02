# 自定义图表类
import enum

from PyQt6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis, QBarSeries, QPieSeries, QSplineSeries
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QFont, QColor, QBrush, QPainter, QPen
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6 import QtCore
from loguru import logger

from config.global_setting import global_setting
from theme.ThemeQt6 import ThemedWidget


class charts(ThemedWidget):
    # 折线图
    Line = 1
    # 柱状图
    Column = 2
    # 饼图
    Pie = 3

    def __init__(self, parent: QVBoxLayout = None, object_name: str = "", charts_type=Line, data_origin_nums=1,
                 is_span=False):
        super().__init__()
        # 主题颜色
        self.theme = global_setting.get_setting("theme_manager").get_themes_color(mode=1)
        # 是否平滑图表
        self.is_span = is_span
        # 数据源数量
        self.data_origin_nums = data_origin_nums
        # 图表类型
        self.charts_type = charts_type
        # obejctName
        self.object_name = object_name
        # 父布局
        self.parent_layout = parent
        # 图表对象
        self.chart: QChart = None
        # 数据系列对象 可能有多个数据源 所以设置为列表
        self.series: [QLineSeries | QBarSeries | QPieSeries] = []
        # x轴
        self.x_axis: QValueAxis = None
        # y轴
        self.y_axis: QValueAxis = None
        # 数据
        self.data = None
        # 数据的最大值 和最小值
        self.min_and_max_x = []
        self.min_and_max_y = []
        self._init_ui()

    def _init_ui(self):
        # 创建布局和图表视图
        self.chart_view = QChartView()

        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)  # 关键设置 抗锯齿
        self.chart_view.setObjectName(f"{self.object_name}")
        self.parent_layout.addWidget(self.chart_view)

        # 初始化图表
        self._init_chart()

    def _init_chart(self):
        theme = self.theme
        # 创建图表对象
        self.chart = QChart()
        self.chart.setObjectName(f"{self.object_name}_chart")
        self.chart.setTitle("自定义图表")

        # 设置序列 和图表类型
        self._set_series()

        # 获取数据
        self.get_data()
        # 将数据放入series中
        self.set_data_to_series()
        # 设置坐标轴
        self._set_x_axis()
        self._set_y_axis()

        # 设置样式
        self.set_style()

        # 添加到视图
        self.chart_view.setChart(self.chart)

    #   设置图表类型 line 折线图
    def _set_series(self):
        # chart_type 图标类型 data_origin_nums 数据源数量
        if self.charts_type == self.Column:
            # 柱状图
            pass
        elif self.charts_type == self.Pie:
            # 饼图
            pass
        else:
            # 折线图
            # 添加数据系列
            for i in range(self.data_origin_nums):
                if self.is_span:
                    single_series = QSplineSeries()
                else:
                    single_series = QLineSeries()
                single_series.setObjectName(f"{self.object_name}_series_{i + 1}")
                single_series.setName(f"测试{i + 1}")
                self.series.append(single_series)
            pass

    # 设置x轴
    def _set_x_axis(self):
        # 将坐标轴关联到图表
        self.x_axis = QValueAxis()
        # 设置坐标轴范围
        self.x_axis.setRange(self.min_and_max_x[0], self.min_and_max_x[1])
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        for single_series in self.series:
            single_series.attachAxis(self.x_axis)

        pass

    # 设置y轴
    def _set_y_axis(self):
        # 将坐标轴关联到图表
        self.y_axis = QValueAxis()
        # 设置坐标轴范围
        self.y_axis.setRange(self.min_and_max_y[0], self.min_and_max_y[1])
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        for single_series in self.series:
            single_series.attachAxis(self.y_axis)

        pass

    # 获取数据
    def get_data(self):
        self.data = [[QPointF(1, 1 + 1 * 200), QPointF(2, 2 - 1 * 200), QPointF(3, 3 + 1 * 200)],
                     [QPointF(1, 1 + 2 * 200), QPointF(2, 2 - 2 * 200), QPointF(3, 3 + 2 * 200)]]
        self.get_max_and_min_data()

    # 获取数据的最大x最小x最大y最小y
    def get_max_and_min_data(self):
        rows = len(self.data)
        # 如果没有数据 直接传0为最大最小值
        if rows == 0:
            self.min_and_max_x = [0, 0]
            self.min_and_max_y = [0, 0]
            return
        columns = len(self.data[0])

        # 将数据的第一个值设为初始值
        max_x = self.data[0][0].x()
        max_y = self.data[0][0].y()
        min_x = self.data[0][0].x()
        min_y = self.data[0][0].y()
        for row in range(rows):
            for column in range(columns):
                max_x = max(max_x, self.data[row][column].x())
                max_y = max(max_y, self.data[row][column].y())
                min_x = min(min_x, self.data[row][column].x())
                min_y = min(min_y, self.data[row][column].y())
        self.min_and_max_x = [min_x, max_x]
        self.min_and_max_y = [min_y, max_y]
        logger.info(f"{self.object_name}‘s data’s min&max x=[{min_x},{max_x}] y=[{min_y},{max_y}]")

    # 将数据放入series中
    def set_data_to_series(self):
        for i in range(self.data_origin_nums):
            self.series[i].append(
                self.data[i])
            # 添加该序列
            self.chart.addSeries(self.series[i])
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

        # self.x_axis.setTitleText(_translate(root_object_name, x_axis_title))
        self.x_axis.setTitleText(x_axis_title)
        self.x_axis.setTitleFont(title_font_style)
        self.x_axis.setLabelsColor(labels_color)  # 标签颜色
        self.x_axis.setGridLineColor(grid_line_color)  # 网格线颜色
        pass

    # 设置y坐标轴样式
    def set_y_axis_style(self, root_object_name: str = "", y_axis_title: str = "y",
                         title_font_style: QFont = QFont("微软雅黑", 6),
                         labels_color: QColor = QColor("#34495E"), grid_line_color: QColor = QColor("#BDC3C7")):
        _translate = QtCore.QCoreApplication.translate
        # self.y_axis.setTitleText(_translate(root_object_name, y_axis_title))
        self.y_axis.setTitleText(y_axis_title)
        self.y_axis.setTitleFont(title_font_style)
        self.y_axis.setLabelsColor(labels_color)  # 标签颜色
        self.y_axis.setGridLineColor(grid_line_color)  # 网格线颜色
        pass

    # 设置图例样式
    def set_legend_style(self, align=Qt.AlignmentFlag.AlignBottom, font_colors: [QColor] = [QColor("#121212")]):
        legend = self.chart.legend()

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(align)
        # 给每个图例设置文字颜色
        markers = self.chart.legend().markers()
        for i in range(len(markers)):
            markers[i].setLabelBrush(QBrush(font_colors[i]))

    # 设置series样式
    def set_series_style(self, font_colors: [QColor] = [QColor("#121212")]):
        for i in range(self.data_origin_nums):
            self.series[i].setColor(font_colors[i])
            self.series[i].setPen(QPen(font_colors[i], i + 2))
            self.series[i].setBrush(QBrush(font_colors[i]))
        # for single_series in self.series:
        #     single_series.setColor(QColor(theme['--text_hover']))

    # 设置chart样式
    def set_chart_style(self, backgroud_color: QBrush = QBrush(QColor("#121212")),
                        plotarea_color: QBrush = QBrush(QColor("#121212")),
                        title_font_style: QFont = QFont("Arial", 8, QFont.Weight.Bold),
                        title_font_color: QColor = QColor("#ffffff")):
        self.chart.setPlotAreaBackgroundBrush(backgroud_color)
        self.chart.setBackgroundBrush(plotarea_color)
        self.set_title_style(font_color=title_font_color, font_style=title_font_style)

    # 设置样式
    def set_style(self):
        self.theme = global_setting.get_setting("theme_manager").get_themes_color(mode=1)
        theme = self.theme
        self.set_chart_style(backgroud_color=QBrush(QColor(theme['--secondary'])),
                             plotarea_color=QBrush(QColor(theme['--secondary'])),
                             title_font_color=QColor(theme['--text']),
                             title_font_style=QFont("Arial", 8, QFont.Weight.Bold))
        self.set_series_style(font_colors=[QColor(theme['--text']), QColor(theme['--text_hover'])])
        self.set_x_axis_style(root_object_name=self.parent_layout.objectName(), labels_color=QColor(theme['--text']),
                              grid_line_color=QColor(theme['--text_hover']))
        self.set_y_axis_style(root_object_name=self.parent_layout.objectName(), labels_color=QColor(theme['--text']),
                              grid_line_color=QColor(theme['--text_hover']))
        self.set_legend_style(font_colors=[QColor(theme['--text']), QColor(theme['--text_hover'])])
        pass
