# 自定义图表类
import enum
from datetime import datetime

from PyQt6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis, QBarSeries, QPieSeries, QSplineSeries
from PyQt6.QtCore import Qt, QPointF, QTimer, QObject, QEvent
from PyQt6.QtGui import QFont, QColor, QBrush, QPainter, QPen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QToolTip
from PyQt6 import QtCore
from loguru import logger

from config.global_setting import global_setting
from dao.data_read import data_read
from theme.ThemeQt6 import ThemedWidget
from util.folder_util import File_Types


class MouseFilter(QObject):
    def __init__(self, chart_view):
        super().__init__()

        self.chart_view = chart_view

    def eventFilter(self, obj, event):
        # 如果是图表view 且事件是鼠标移动时
        logger.error("---------------------------------------------------------------")
        if obj == self.chart_view and event.type() == QEvent.Type.MouseMove:

            pos = event.pos()
            chart_pos = self.chart_view.mapToScene(pos)
            chart = self.chart_view.chart()
            chart_item_pos = chart.mapToValue(chart_pos)

            threshold = 0.5  # 距离阈值，视数据范围调整
            tooltip_texts = []

            # 遍历所有系列
            for series in self.chart_view.chart().series():
                if not isinstance(series, QLineSeries):
                    continue
                closest_point = None
                min_dist = float('inf')
                for point in series.points():
                    dx = point.x() - chart_item_pos.x()
                    dy = point.y() - chart_item_pos.y()
                    dist = (dx * dx + dy * dy) ** 0.5  # 欧氏距离
                    if dist < min_dist:
                        min_dist = dist
                        closest_point = point

                if min_dist < threshold and closest_point is not None:
                    # 这里可以加上系列名称或索引
                    name = series.name() if series.name() else f"Series {chart.series().index(series) + 1}"
                    tooltip_texts.append(f"{name}: x={closest_point.x():.2f}, y={closest_point.y():.2f}")

            if tooltip_texts:
                global_pos = self.chart_view.mapToGlobal(pos)
                QToolTip.showText(global_pos, "\n".join(tooltip_texts))
            else:
                QToolTip.hideText()

            return False

        return super().eventFilter(obj, event)


class charts(ThemedWidget):
    # 折线图
    Line = 1
    # 柱状图
    Column = 2
    # 饼图
    Pie = 3

    def __init__(self, parent: QVBoxLayout = None, object_name: str = "", charts_type=Line, data_origin_nums=1,
                 data_origin_ports=['COM3'], data_read_counts=10,
                 is_span=False):
        """

        :param parent:父组件
        :param object_name:图表objectName
        :param charts_type:图表类型
        :param data_origin_nums:数据源数量
        :param data_origin_ports: 数据源串口[]
        :param data_counts:图表数据展示的总数量
        :param is_span:图表是否平滑
        """
        super().__init__()
        # 数据获取器
        self.data_read = data_read(file_type=global_setting.get_setting('serial_config')['Storage']['file_type'],
                                   data_origin_port=data_origin_ports)
        # 主题颜色
        self.theme = global_setting.get_setting("theme_manager").get_themes_color(mode=1)
        # 是否平滑图表
        self.is_span = is_span
        # 数据源数量
        self.data_origin_nums = data_origin_nums
        # 数据源端口号
        self.data_origin_ports = data_origin_ports
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
        # 图表一共读取的数据总数量
        self.data_all_counts = []
        for i in range(data_origin_nums):
            self.data.append([])
            self.data_all_counts.append(0)
        # 图表每次读取的数据数量
        self.data_read_counts = data_read_counts
        # 定时器
        self.timer = None
        # 数据的最大值 和最小值
        self.min_and_max_x = [0, 0]
        self.min_and_max_y = [0, 0]
        self._init_ui()

    def _init_ui(self):
        # 创建布局和图表视图
        self.chart_view = QChartView()
        self.chart_view.setMouseTracking(True)  # 开启鼠标追踪

        # 安装事件过滤器 图表鼠标移动显示数值
        filter = MouseFilter(self.chart_view)
        self.chart_view.installEventFilter(filter)
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
        # 将数据放入series中 更新数据
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
                single_series.setName(f"源{self.data_origin_ports[i]}")
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

    # 转换数据 将读取的数据格式转换成[[QPointF(1, 1 + 1 * 200), QPointF(2, 2 - 1 * 200), QPointF(3, 3 + 1 * 200)],
    #         #              [QPointF(1, 1 + 2 * 200), QPointF(2, 2 - 2 * 200), QPointF(3, 3 + 2 * 200)]]
    def transfer_data(self, origin_datas):
        new_datas = []
        for origin_datas_row in origin_datas:
            new_datas_row = []
            for origin_data in origin_datas_row:
                # 使用match
                if global_setting.get_setting('serial_config')['Storage']['file_type'] == File_Types.TXT.value:
                    q_point = QPointF(float(origin_data.id), float(origin_data.data))
                else:
                    pass
                new_datas_row.append(q_point)
            pass
            new_datas.append(new_datas_row)
        return new_datas

    pass

    # 获取数据
    def get_data(self):

        # 定时器，每delay毫秒更新一次数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.get_data_func)
        self.timer.start(global_setting.get_setting("configer")['graphic'][
                             'delay'])

    # 获取数据的函数
    def get_data_func(self):
        # self.data = [[QPointF(1, 1 + 1 * 200), QPointF(2, 2 - 1 * 200), QPointF(3, 3 + 1 * 200)],
        #              [QPointF(1, 1 + 2 * 200), QPointF(2, 2 - 2 * 200), QPointF(3, 3 + 2 * 200)]]
        # 读取数据
        try:
            data_temp = self.transfer_data(
                self.data_read.read_service.read_range_datas_seq(data_origin_port=self.data_origin_ports,
                                                                 times=datetime.now(),
                                                                 data_start=[x + 1 for x in self.data_all_counts],
                                                                 data_nums=[self.data_read_counts for i in
                                                                            self.data_origin_ports],
                                                                 data_step=[1 for i in self.data_origin_ports]))
        except Exception as e:
            logger.error(f"图表{self.object_name}读取数据源{self.data_origin_ports}数据失败，失败原因：{e}")

        # 插入数据
        for origin_data_index in range(len(data_temp)):
            logger.info(
                f"图表{self.object_name}读取数据源{origin_data_index}数据长度为{len(data_temp[origin_data_index])}，data_start={self.data_all_counts}data_nums={self.data_read_counts - 1}")
            # 把每次获取的数据数量记录起来
            self.data_all_counts[origin_data_index] += len(data_temp[origin_data_index])
            for data_index in range(len(data_temp[origin_data_index])):
                self.data[origin_data_index].append(data_temp[origin_data_index][data_index])
                pass
            pass
        # 插入数据之后的数据长度
        show_nums = global_setting.get_setting("configer")['graphic'][
            'data_show_nums']
        try:

            for origin_data_index in range(len(self.data)):
                # 不同数据源在图表显示的时候需要同步 只要有一方数据源的数量一直是show_nums，而其他数据源出现数据更新暂停 则在图表移除数据
                if len(data_temp[origin_data_index]) == 0 and len(self.data[origin_data_index]) != 0:
                    self.data[origin_data_index].pop(0)
                # 每个数据源需要遵守的规则
                while len(self.data[origin_data_index]) >= show_nums and len(self.data[origin_data_index]) != 0:
                    logger.info(f"图表{self.object_name}持数据源{origin_data_index}长度为{len(self.data[origin_data_index])}")
                    self.data[origin_data_index].pop(0)  # 保持数据长度为show_nums


        except Exception as e:
            logger.error(f"图表{self.object_name}持数据长度为show_nums失败，series[0]数据长度{len(self.data[0])}，失败原因：{e}")
        try:
            # 获取 x 和y值的最大值和最小值来确定坐标轴范围
            self.get_max_and_min_data()
            self.update_series()
            # 设置坐标轴范围
            self.x_axis.setRange(self.min_and_max_x[0], self.min_and_max_x[1])
            self.y_axis.setRange(self.min_and_max_y[0], self.min_and_max_y[1])
        except Exception as e:
            logger.error(f"图表{self.object_name}更新series失败，series[0]数据长度{len(self.data[0])}，失败原因：{e}")
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
            f"{self.object_name}‘s data’s min&max x=[{self.min_and_max_x[0]},{self.min_and_max_x[1]}] y=[{self.min_and_max_y[0]},{self.min_and_max_x[1]}]")

    # 更新series中的数据
    def update_series(self):
        for i in range(self.data_origin_nums):
            self.series[i].replace(
                self.data[i])
            # 移出该序列
            self.chart.removeSeries(self.series[i])
            # 添加该序列
            self.chart.addSeries(self.series[i])
        pass

    # 将数据放入series中
    def set_data_to_series(self):
        for i in range(self.data_origin_nums):
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
