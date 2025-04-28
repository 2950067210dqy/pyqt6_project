# 自定义图表类
import enum
from datetime import datetime

from PyQt6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis, QBarSeries, QPieSeries, QSplineSeries, \
    QDateTimeAxis
from PyQt6.QtCore import Qt, QPointF, QTimer, QObject, QEvent, QDateTime, QRunnable
from PyQt6.QtGui import QFont, QColor, QBrush, QPainter, QPen
from PyQt6.QtWidgets import QVBoxLayout, QToolTip, QHBoxLayout
from PyQt6 import QtCore
from loguru import logger

from config.global_setting import global_setting
from dao.data_read import data_read
from theme.ThemeManager import Charts_Style_Name
from theme.ThemeQt6 import ThemedWidget
from util.folder_util import File_Types


class tab2_tab0_charts_single(ThemedWidget):

    def __init__(self, datas, parent: QVBoxLayout | QHBoxLayout = None, object_name: str = "",
                 title: str = "", x_name: str = "x", y_name: str = "y",
                 is_span=False):
        """

        :param parent:父组件
        :param object_name:图表objectName
        :param charts_type:图表类型
        :param datas [{name:'',data:{x:[],y:[]}},]
        :param is_span:图表是否平滑
        """
        super().__init__()
        self.x_name = x_name
        self.y_name = y_name
        # 主题颜色
        self.theme = global_setting.get_setting("theme_manager").get_charts_style()
        # 当前样式名
        self.theme_name = Charts_Style_Name.NORMAL.value
        # 是否平滑图表
        self.is_span = is_span
        self.title = title
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
        self.data = []
        self.origin_datas = datas
        self.data_origin_nums = len(datas)
        # 数据的最大值 和最小值
        self.min_and_max_x = [0, 0]
        self.min_and_max_y = [0, 0]
        self._init_ui()

    def _init_ui(self):
        # 创建布局和图表视图
        self.chart_view = QChartView()
        self.chart_view.setMouseTracking(True)  # 开启鼠标追踪

        # self.chart_view.setFixedSize(250, 150)  # 固定大小

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
        self.chart.setTitle(self.title)

        # 设置序列 和图表类型
        self._set_series()
        # 获取数据
        self.get_data()
        # 将数据放入series中 更新数据
        self.set_data_to_series()
        # 设置坐标轴
        self._set_x_axis()
        self._set_y_axis()

        # 设置样式
        self.set_style()

        # 添加到视图
        self.chart_view.setChart(self.chart)

    def get_data(self):
        self.data = self.transfer_data(origin_datas=self.origin_datas)
        self.get_max_and_min_data()
        pass

    #   设置图表类型 line 折线图
    def _set_series(self):

        # 折线图
        # 添加数据系列
        for i in range(self.data_origin_nums):
            if self.is_span:
                single_series = QSplineSeries()
            else:
                single_series = QLineSeries()
            single_series.setObjectName(f"{self.object_name}_series_{i + 1}")

            self.series.append(single_series)
        pass

    # 设置x轴
    def _set_x_axis(self):
        # 将坐标轴关联到图表
        if self.x_axis == None:
            self.x_axis = QValueAxis()

        # 设置坐标轴范围
        # self.x_axis.setLabelsAngle(90)  # 旋转90°竖着显示日期
        self.x_axis.setRange(self.min_and_max_x[0],
                             self.min_and_max_x[1])
        self.x_axis.setTitleText(self.x_name)
        self.chart.removeAxis(self.x_axis)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        for i in range(len(self.series)):
            self.series[i].attachAxis(self.x_axis)

        pass

    # 设置y轴
    def _set_y_axis(self):
        # 将坐标轴关联到图表
        if self.y_axis == None:
            self.y_axis = QValueAxis()
        # 设置坐标轴范围
        self.y_axis.setTitleText(self.y_name)
        self.y_axis.setRange(self.min_and_max_y[0], self.min_and_max_y[1])
        # self.y_axis.setLabelFormat("%.1f")
        self.chart.removeAxis(self.y_axis)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        for i in range(len(self.series)):
            self.series[i].attachAxis(self.y_axis)

        pass

    # 转换数据 将读取的数据格式转换成[[QPointF(1, 1 + 1 * 200), QPointF(2, 2 - 1 * 200), QPointF(3, 3 + 1 * 200)],
    #         #              [QPointF(1, 1 + 2 * 200), QPointF(2, 2 - 2 * 200), QPointF(3, 3 + 2 * 200)]]
    def transfer_data(self, origin_datas):
        new_datas = []
        for i in range(self.data_origin_nums):
            new_data = []
            for origin_datas_row in range(len(origin_datas[i]['data']['x'])):
                q_point = QPointF(
                    float(origin_datas[i]['data']['x'][origin_datas_row]),
                    float(origin_datas[i]['data']['y'][origin_datas_row]))
                new_data.append(q_point)
            new_datas.append(new_data)
        return new_datas

    pass

    # 获取数据的最大x最小x最大y最小y
    def get_max_and_min_data(self):
        rows = len(self.data)
        # 如果没有数据 直接传0为最大最小值
        if rows == 0:
            self.min_and_max_x = [0, 0]
            self.min_and_max_y = [0, 0]
            return

        # 找一个初始值
        max_x = 0
        max_y = 0
        min_x = 0
        min_y = 0
        for row in range(rows):
            if len(self.data[row]) != 0:
                max_x = self.data[row][0].x()
                min_x = self.data[row][0].x()
                max_y = self.data[row][0].y()
                min_y = self.data[row][0].y()

        for row in range(rows):
            if len(self.data[row]) != 0:
                for column in range(len(self.data[row])):
                    max_x = max(max_x, self.data[row][column].x())
                    max_y = max(max_y, self.data[row][column].y())
                    min_x = min(min_x, self.data[row][column].x())
                    min_y = min(min_y, self.data[row][column].y())
        # 如果调整的数据的最大值和最小值都还是比之前的最大值和最小值小或大就不进行改变 大部分时间固定坐标轴 x轴不需要大部分时间固定
        # if min_x < self.min_and_max_x[0]:
        #     self.min_and_max_x[0] = min_x
        # if max_x > self.min_and_max_x[1]:
        #     self.min_and_max_x[1] = max_x
        self.min_and_max_x[0] = min_x
        self.min_and_max_x[1] = max_x
        if min_y < self.min_and_max_y[0]:
            self.min_and_max_y[0] = min_y
        if max_y > self.min_and_max_y[1]:
            self.min_and_max_y[1] = max_y

        logger.info(
            f"{self.object_name}‘s data’s min&max x=[{self.min_and_max_x[0]},{self.min_and_max_x[1]}] y=[{self.min_and_max_y[0]},{self.min_and_max_y[1]}]")

    # 将数据放入series中
    def set_data_to_series(self):
        for i in range(self.data_origin_nums):
            self.series[i].setName(f"源{self.origin_datas[i]['series_name']}")
            self.series[i].replace(
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
    def set_x_axis_style(self, root_object_name: str = "",
                         title_font_style: QFont = QFont("微软雅黑", 6),
                         labels_color: QColor = QColor("#34495E"), grid_line_color: QColor = QColor("#BDC3C7")):
        _translate = QtCore.QCoreApplication.translate

        # self.x_axis.setTitleText(_translate(root_object_name, x_axis_title))

        self.x_axis.setTitleFont(title_font_style)

        self.x_axis.setLabelsColor(labels_color)  # 标签颜色
        self.x_axis.setGridLineColor(grid_line_color)  # 网格线颜色
        pass

    # 设置y坐标轴样式
    def set_y_axis_style(self, root_object_name: str = "",
                         title_font_style: QFont = QFont("微软雅黑", 6),
                         labels_color: QColor = QColor("#34495E"), grid_line_color: QColor = QColor("#BDC3C7")):
        _translate = QtCore.QCoreApplication.translate
        # self.y_axis.setTitleText(_translate(root_object_name, y_axis_title))

        self.y_axis.setTitleFont(title_font_style)
        self.y_axis.setLabelsColor(labels_color)  # 标签颜色
        self.y_axis.setGridLineColor(grid_line_color)  # 网格线颜色
        pass

    # 设置图例样式
    def set_legend_style(self, align=Qt.AlignmentFlag.AlignBottom,
                         font_colors: [QColor] = [QColor("#121212")]):
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(align)
        # 将图例放置在图表内部右上角，偏移一点距离
        self.chart.legend().setPos(QPointF(self.chart.plotArea().right() - 150, self.chart.plotArea().top() + 10))

        markers = self.chart.legend().markers()
        for i in range(len(markers)):
            markers[i].setLabelBrush(QBrush(font_colors[i]))

    # 设置series样式
    def set_series_style(self, font_colors: [QColor] = [QColor("#121212")]):
        for i in range(self.data_origin_nums):
            self.series[i].setColor(font_colors[i])
            self.series[i].setPen(QPen(font_colors[i]))
            self.series[i].setBrush(QBrush(font_colors[i]))

    # 设置chart样式
    def set_chart_style(self, backgroud_color: QBrush = QBrush(QColor("#121212")),
                        plotarea_color: QBrush = QBrush(QColor("#121212")),
                        title_font_style: QFont = QFont("Arial", 8, QFont.Weight.Bold),
                        title_font_color: QColor = QColor("#ffffff")):
        self.chart.setPlotAreaBackgroundBrush(backgroud_color)
        self.chart.setBackgroundBrush(plotarea_color)
        self.set_title_style(font_color=title_font_color, font_style=title_font_style)

    # 设置series和legend样式
    def set_series_lenged_style(self):
        series_color = global_setting.get_setting("theme_manager").get_contrast_color(
            colorHex=self.theme[self.theme_name]['background_color'], color_delta_start=-100, color_delta_end=100,
            color_nums=self.data_origin_nums)
        self.set_series_style(
            font_colors=[QColor(series_color[i]) for i in
                         range(self.data_origin_nums)])
        self.set_legend_style(font_colors=[QColor(series_color[i]) for i in
                                           range(self.data_origin_nums)
                                           ])
        pass

    # 设置样式
    def set_style(self):
        self.theme = global_setting.get_setting("theme_manager").get_charts_style()
        self.set_chart_style(
            plotarea_color=QBrush(QColor(QColor(global_setting.get_setting("theme_manager").get_neighbor_color(
                colorHex=self.theme[self.theme_name]['background_color'], color_nums=1)[0]))),

            backgroud_color=QBrush(QColor(self.theme[self.theme_name]['background_color'])),
            title_font_color=QColor(global_setting.get_setting("theme_manager").get_contrast_color(
                colorHex=self.theme[self.theme_name]['background_color'], color_nums=1)[0]),
            title_font_style=QFont("Arial", 8, QFont.Weight.Bold))
        self.set_series_lenged_style()
        axis_color = global_setting.get_setting("theme_manager").get_contrast_color(
            colorHex=self.theme[self.theme_name]['background_color'], color_nums=2)
        self.set_x_axis_style(root_object_name=self.parent_layout.objectName(),
                              labels_color=QColor(axis_color[0]),
                              grid_line_color=QColor(axis_color[1]))
        self.set_y_axis_style(root_object_name=self.parent_layout.objectName(),
                              labels_color=QColor(axis_color[0]),
                              grid_line_color=QColor(axis_color[1]))

        pass
