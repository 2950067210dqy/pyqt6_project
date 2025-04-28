# 自定义图表类
import enum
from datetime import datetime

from PyQt6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis, QBarSeries, QPieSeries, QSplineSeries, \
    QDateTimeAxis, QBarCategoryAxis, QStackedBarSeries, QBarSet, QLogValueAxis
from PyQt6.QtCore import Qt, QPointF, QTimer, QObject, QEvent, QDateTime, QRunnable, QRectF
from PyQt6.QtGui import QFont, QColor, QBrush, QPainter, QPen
from PyQt6.QtWidgets import QVBoxLayout, QToolTip, QHBoxLayout
from PyQt6 import QtCore
from loguru import logger

from config.global_setting import global_setting
from dao.data_read import data_read
from theme.ThemeManager import Charts_Style_Name
from theme.ThemeQt6 import ThemedWidget
from util.folder_util import File_Types


class CustomChartView(QChartView):
    def __init__(self, chart):
        super().__init__(chart)
        self.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
        self.rubberBandRect = QRectF()

    def mouseReleaseEvent(self, event):
        if self.rubberBandRect.isNull():
            # 没有选区时，调用默认处理
            super().mouseReleaseEvent(event)
            return

        # 选区非空，转换为图表坐标
        rect = self.rubberBandRect.normalized()
        chart = self.chart()

        # 转换屏幕坐标到图表坐标
        topLeft = chart.mapToValue(rect.topLeft())
        bottomRight = chart.mapToValue(rect.bottomRight())

        zoomRect = QRectF(topLeft, bottomRight)
        if zoomRect.width() > 0 and zoomRect.height() > 0:
            chart.zoomIn(zoomRect)

        self.rubberBandRect = QRectF()  # 清空选区
        super().mouseReleaseEvent(event)

    def rubberBandChanged(self, rubberBandRect, fromScenePoint, toScenePoint):
        self.rubberBandRect = rubberBandRect


class tab2_tab0_charts_single_column(ThemedWidget):

    def __init__(self, datas, parent: QVBoxLayout | QHBoxLayout = None, object_name: str = "",
                 title: str = "",
                 is_span=False):
        """

        :param parent:父组件
        :param object_name:图表objectName
        :param charts_type:图表类型
        :param datas [{name:'',data:{x:[],y:[]}},]
        :param is_span:图表是否平滑
        """
        super().__init__()

        # 主题颜色
        self.theme = global_setting.get_setting("theme_manager").get_charts_style()
        # 当前样式名
        self.theme_name = Charts_Style_Name.NORMAL.value
        # 是否平滑图表
        self.is_span = is_span
        self.title = title
        # obejctName
        self.object_name = object_name
        # 父布局
        self.parent_layout = parent
        # 图表对象
        self.chart: QChart = None
        # 数据系列对象 可能有多个数据源 所以设置为列表
        self.series: [QLineSeries | QBarSeries | QPieSeries] = []
        self.set = []
        # x轴
        self.categories = []
        self.x_axis: QBarCategoryAxis = None
        # y轴
        self.y_axis: QValueAxis = None
        # 数据
        self.data = {}
        self.origin_datas = datas
        self.data_origin_nums = len(datas.data.y)
        # 数据的最大值 和最小值
        # self.min_and_max_x = [0, 0]
        self.min_and_max_y = [0, 0]
        self._init_ui()

    def _init_ui(self):
        # 创建布局和图表视图
        self.chart_view = QChartView()
        self.chart_view.setMouseTracking(True)  # 开启鼠标追踪

        self.chart_view.setFixedSize(2600, 400)  # 固定大小
        # self.chart_view.setDragMode(QChartView.DragMode.ScrollHandDrag)  # 开启拖拽模式
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)  # 关键设置 抗锯齿
        # self.chart_view.setRubberBand(QChartView.RubberBand.RectangleRubberBand)
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
        # self.set_style()

        # 添加到视图
        self.chart_view.setChart(self.chart)

    def get_data(self):
        self.data = self.transfer_data(origin_datas=self.origin_datas)
        self.get_max_and_min_data()
        pass

    #   设置图表类型 line 折线图
    def _set_series(self):

        # 添加数据系列
        for i in range(self.data_origin_nums):
            if self.is_span:
                single_series = QStackedBarSeries()
            else:
                single_series = QStackedBarSeries()
            single_series.setObjectName(f"{self.object_name}_series_{i + 1}")

            self.series.append(single_series)
        pass

    # 设置x轴
    def _set_x_axis(self):
        # 将坐标轴关联到图表
        if self.x_axis == None:
            self.x_axis = QBarCategoryAxis()

        # 设置坐标轴范围
        # self.x_axis.setLabelsAngle(90)  # 旋转90°竖着显示日期

        self.chart.removeAxis(self.x_axis)
        for i in self.data.data.x.data:
            result = ','.join(str(x) for x in i)
            self.categories.append(result)
            pass
        self.x_axis.setTitleText(','.join(str(x) for x in self.data.data.x.name))
        self.x_axis.append(self.categories)
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        for i in range(len(self.series)):
            self.series[i].attachAxis(self.x_axis)

        pass

    # 设置y轴
    def _set_y_axis(self):
        # 将坐标轴关联到图表
        if self.y_axis == None:
            # self.y_axis = QValueAxis()
            self.y_axis = QLogValueAxis()
        self.y_axis.setBase(10)
        # 设置坐标轴范围
        self.y_axis.setTitleText("log" + self.data.name)
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

        return origin_datas

    pass

    # 获取数据的最大y最小y
    def get_max_and_min_data(self):
        # 如果没有数据 直接传0为最大最小值
        if self.data == None:
            self.min_and_max_y = [0, 0]
            return

        # 找一个初始值

        max_y = 0

        min_y = 0
        for row in range(len(self.data.data.y)):
            if len(self.data.data.y) != 0:
                for j in range(len(self.data.data.y[row].data)):
                    if len(self.data.data.y[row].data) != 0 and len(self.data.data.y[row].data[j].data) != 0:
                        max_y = self.data.data.y[row].data[j].data[0]
                        min_y = self.data.data.y[row].data[j].data[0]
        for row in range(len(self.data.data.y)):
            for j in range(len(self.data.data.y[row].data)):
                for k in range(len(self.data.data.y[row].data[j].data)):
                    max_y = max(max_y, self.data.data.y[row].data[j].data[k])
                    min_y = min(min_y, self.data.data.y[row].data[j].data[k])
                    pass

        # 如果调整的数据的最大值和最小值都还是比之前的最大值和最小值小或大就不进行改变 大部分时间固定坐标轴 x轴不需要大部分时间固定
        # if min_x < self.min_and_max_x[0]:
        #     self.min_and_max_x[0] = min_x
        # if max_x > self.min_and_max_x[1]:
        #     self.min_and_max_x[1] = max_x

        if min_y < self.min_and_max_y[0]:
            self.min_and_max_y[0] = min_y
        if max_y > self.min_and_max_y[1]:
            self.min_and_max_y[1] = max_y

        logger.info(
            f"{self.object_name}‘s data’s min&max  y=[{self.min_and_max_y[0]},{self.min_and_max_y[1]}]")

    # 将数据放入series中
    def set_data_to_series(self):
        # A\B\C相
        for row in range(len(self.data.data.y)):
            self.chart.removeSeries(self.series[row])
            # 两个device
            for j in range(len(self.data.data.y[row].data)):
                set = QBarSet(f"{self.data.data.y[row].name}{self.data.data.y[row].data[j].name}")
                set.append(self.data.data.y[row].data[j].data)

                self.set.append(set)
                self.series[row].append(set)
            # 在柱头添加数值标签
            # self.series[row].setLabelsVisible(True)
            self.chart.addSeries(self.series[row])
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
