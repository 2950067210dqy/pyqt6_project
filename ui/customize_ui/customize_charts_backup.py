# 自定义图表类
import enum
import traceback
from datetime import datetime

from PyQt6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis, QBarSeries, QPieSeries, QSplineSeries, \
    QDateTimeAxis
from PyQt6.QtCore import Qt, QPointF, QTimer, QObject, QEvent, QDateTime, QRunnable
from PyQt6.QtGui import QFont, QColor, QBrush, QPainter, QPen
from PyQt6.QtWidgets import QVBoxLayout, QToolTip
from PyQt6 import QtCore
from loguru import logger

from config.global_setting import global_setting
from dao.data_read import data_read
from theme.ThemeManager import Charts_Style_Name
from theme.ThemeQt6 import ThemedWidget
from util.folder_util import File_Types


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
        self.theme = global_setting.get_setting("theme_manager").get_charts_style()
        # 当前样式名
        self.theme_name = Charts_Style_Name.NORMAL.value
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
        # 图表上次读取的数据量
        self.data_last_read_counts = []
        # 读取数据的方式
        self.data_func_choose = []
        for i in range(data_origin_nums):
            self.data.append([])
            self.data_all_counts.append(0)
            self.data_last_read_counts.append(0)
            self.data_func_choose.append(True)
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

        self.chart_view.setFixedSize(500, 400)  # 固定大小

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
        if self.x_axis == None:
            self.x_axis = QDateTimeAxis()
            self.x_axis.setFormat("HH:mm:ss.zzz")  # 设置日期时间格式，可以根据需求调整

        # 设置坐标轴范围
        # self.x_axis.setLabelsAngle(90)  # 旋转90°竖着显示日期
        self.x_axis.setRange(QDateTime.fromSecsSinceEpoch(int(self.min_and_max_x[0])),
                             QDateTime.fromSecsSinceEpoch(int(self.min_and_max_x[1])))
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
        self.y_axis.setRange(self.min_and_max_y[0], self.min_and_max_y[1])
        self.y_axis.setLabelFormat("%.1f")
        self.chart.removeAxis(self.y_axis)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        for i in range(len(self.series)):
            self.series[i].attachAxis(self.y_axis)

        pass

    # 转换数据 将读取的数据格式转换成[[QPointF(1, 1 + 1 * 200), QPointF(2, 2 - 1 * 200), QPointF(3, 3 + 1 * 200)],
    #         #              [QPointF(1, 1 + 2 * 200), QPointF(2, 2 - 2 * 200), QPointF(3, 3 + 2 * 200)]]
    def transfer_data(self, origin_datas):
        new_datas = []
        # 存放数据id
        new_datas_id = []
        for origin_datas_row in origin_datas:
            new_datas_row = []
            new_datas_id_row = []
            for origin_data in origin_datas_row:
                # 使用match
                if global_setting.get_setting('serial_config')['Storage']['file_type'] == File_Types.TXT.value:
                    if self.object_name == "charts_tab1_left_bottom_1":
                        logger.error(f"{self.object_name}|{origin_data.id}|{origin_data.data}|{origin_data.date}")
                        logger.error(
                            f"{self.data_all_counts}|{self.data_last_read_counts}|{self.data_func_choose}")
                    q_point = QPointF(
                        int(datetime.strptime(origin_data.date, "%Y-%m-%d/%H:%M:%S.%f").timestamp() * 1000),
                        float(origin_data.data))
                else:
                    pass
                new_datas_id_row.append(int(origin_data.id))
                new_datas_row.append(q_point)
            pass
            new_datas.append(new_datas_row)
            new_datas_id.append(new_datas_id_row)
        return new_datas, new_datas_id

    pass

    # 获取数据
    def get_data(self):
        # 第一次根据几秒前开始获取数据
        # 然后在根据index获取数据
        # 定时器，每delay毫秒更新一次数据
        # ！！！！！！！！！！！！！！！！！！！！！！用线程池 不然卡死！
        self.timer = QTimer()
        self.timer.timeout.connect(self.get_data_func_from_times_start)
        # self.timer.timeout.connect(self.start_read_data_task)
        self.timer.start(global_setting.get_setting("configer")['graphic'][
                             'delay'])
        pass

    # def start_read_data_task(self):
    #     self.task = read_data_task(chart=self)
    #     global_setting.get_setting('thread_pool').start(self.task)
    #     pass

    def get_data_func_from_index_start(self):
        # 从index来开始读取数据
        try:
            data_temp, data_ids = self.transfer_data(
                self.data_read.read_service.read_range_datas_seq_from_index_start(
                    data_origin_port=self.data_origin_ports,
                    times=datetime.now(),
                    data_start=[x + 1 for x in self.data_all_counts],
                    data_nums=[self.data_read_counts for i in
                               self.data_origin_ports],
                    data_step=[1 for i in self.data_origin_ports]))


        except Exception as e:
            logger.error(
                f"图表{self.object_name}读取数据源{self.data_origin_ports}数据失败，失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")

        # 插入数据
        for origin_data_index in range(len(data_temp)):
            # logger.info(
            #     f"图表{self.object_name}读取数据源{origin_data_index}数据长度为{len(data_temp[origin_data_index])}，data_start={self.data_all_counts}data_nums={self.data_read_counts - 1}")
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
                    # logger.info(f"图表{self.object_name}持数据源{origin_data_index}长度为{len(self.data[origin_data_index])}")
                    self.data[origin_data_index].pop(0)  # 保持数据长度为show_nums


        except Exception as e:
            logger.error(
                f"图表{self.object_name}持数据长度为show_nums失败，series[0]数据长度{len(self.data[0])}，失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")
        try:
            # 获取 x 和y值的最大值和最小值来确定坐标轴范围
            self.get_max_and_min_data()
            self.update_series()
            # 设置坐标轴范围
            self._set_x_axis()
            self._set_y_axis()
            # 更新样式
            self.set_series_lenged_style()
        except Exception as e:
            logger.error(
                f"图表{self.object_name}更新series失败，series[0]数据长度{len(self.data[0])}，失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")
        pass

    # 获取数据的函数
    def get_data_func_from_times_start(self):
        # 根据时间的前几秒来开始读取
        # 读取数据
        try:
            # 如果没读取到数据 优先从times位置开始读取 否则从index位置开始读取
            self.data_func_choose = [len(self.data[i]) == 0 or self.data_last_read_counts[i] == 0 for i in
                                     range(len(self.data))]
            # 不同方式的data_start
            data_start = [
                datetime.now() if self.data_func_choose[choose_index] else self.data_all_counts[choose_index] + 1
                for choose_index in range(len(self.data_func_choose))]
            data_temp, data_ids = self.transfer_data(
                self.data_read.read_service.read_range_datas_seq_from_times_index_start(
                    data_origin_port=self.data_origin_ports,
                    times=datetime.now(),
                    data_start=data_start,
                    data_func_choose=self.data_func_choose,
                    data_nums=[self.data_read_counts for i in
                               self.data_origin_ports],
                    data_step=[1 for i in self.data_origin_ports]))


        except Exception as e:
            logger.error(
                f"图表{self.object_name}读取数据源{self.data_origin_ports}数据失败，失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")

        # 插入数据
        for origin_data_index in range(len(data_temp)):
            # 把读取的数据量存储
            self.data_last_read_counts[origin_data_index] = len(data_temp[origin_data_index])
            # 把这次获取的数据的最大id放入我们的data_all_counts
            if len(data_ids[origin_data_index]) != 0:
                self.data_all_counts[origin_data_index] = data_ids[origin_data_index][
                    len(data_ids[origin_data_index]) - 1]
                pass
            else:
                self.data_all_counts[origin_data_index] = 0
                pass
            # 插入数据
            for data_index in range(len(data_temp[origin_data_index])):
                self.data[origin_data_index].append(data_temp[origin_data_index][data_index])
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
                    # logger.info(f"图表{self.object_name}持数据源{origin_data_index}长度为{len(self.data[origin_data_index])}")
                    self.data[origin_data_index].pop(0)  # 保持数据长度为show_nums
        except Exception as e:
            logger.error(
                f"图表{self.object_name}持数据长度为show_nums失败，series[0]数据长度{len(self.data[0])}，失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")
        try:
            # 获取 x 和y值的最大值和最小值来确定坐标轴范围
            self.get_max_and_min_data()
            self.update_series()
            # 设置坐标轴范围
            self._set_x_axis()
            self._set_y_axis()
            # 更新样式
            self.set_series_lenged_style()
        except Exception as e:
            logger.error(
                f"图表{self.object_name}更新series失败，series[0]数据长度{len(self.data[0])}，失败原因：{e} |  异常堆栈跟踪：{traceback.print_exc()}")
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
        # 将毫秒转换成秒
        self.min_and_max_x[0] = min_x / 1000.0
        self.min_and_max_x[1] = max_x / 1000.0
        if min_y < self.min_and_max_y[0]:
            self.min_and_max_y[0] = min_y
        if max_y > self.min_and_max_y[1]:
            self.min_and_max_y[1] = max_y

        logger.info(
            f"{self.object_name}‘s data’s min&max x=[{self.min_and_max_x[0]},{self.min_and_max_x[1]}] y=[{self.min_and_max_y[0]},{self.min_and_max_y[1]}]")

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
    def set_legend_style(self, align=Qt.AlignmentFlag.AlignTop,
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
            self.series[i].setPen(QPen(font_colors[i], i + 2))
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
        self.set_series_style(font_colors=[QColor(self.theme[self.theme_name]['series']['series_color']),
                                           QColor(self.theme[self.theme_name]['series']['series_color'])])
        self.set_legend_style(font_colors=[QColor(self.theme[self.theme_name]['legend']['legend_font_color']),
                                           QColor(self.theme[self.theme_name]['legend']['legend_font_color'])
                                           ])
        pass

    # 设置样式
    def set_style(self):
        self.theme = global_setting.get_setting("theme_manager").get_charts_style()
        self.set_chart_style(
            backgroud_color=QBrush(QColor(QColor(self.theme[self.theme_name]['chart']['chart_background_color']))),
            plotarea_color=QBrush(QColor(self.theme[self.theme_name]['chart']['plot_area_color'])),
            title_font_color=QColor(self.theme[self.theme_name]['chart']['title_font_color']),
            title_font_style=QFont("Arial", 8, QFont.Weight.Bold))
        self.set_series_lenged_style()
        self.set_x_axis_style(root_object_name=self.parent_layout.objectName(),
                              labels_color=QColor(self.theme[self.theme_name]['axis']['axis_label_color']),
                              grid_line_color=QColor(self.theme[self.theme_name]['axis']['axis_grid_line_color']))
        self.set_y_axis_style(root_object_name=self.parent_layout.objectName(),
                              labels_color=QColor(self.theme[self.theme_name]['axis']['axis_label_color']),
                              grid_line_color=QColor(self.theme[self.theme_name]['axis']['axis_grid_line_color']))

        pass

# class read_data_task(QRunnable):
#     def __init__(self, chart: charts = charts()):
#         super().__init__()
#         self.chart = chart
#         pass
#
#     # 读取数据任务线程池
#     def run(self):
#         self.get_data_func_from_times_start()
#
#     # 获取数据的函数
#     def get_data_func_from_times_start(self):
#         # 根据时间的前几秒来开始读取
#         # 读取数据
#         try:
#             # 如果没读取到数据 优先从times位置开始读取 否则从index位置开始读取
#             self.data_func_choose = [len(self.chart.data[i]) == 0 or self.chart.data_last_read_counts[i] == 0 for i in
#                                      range(len(self.chart.data))]
#             # 不同方式的data_start
#             data_start = [
#                 datetime.now() if self.data_func_choose[choose_index] else self.chart.data_all_counts[choose_index] + 1
#                 for choose_index in range(len(self.data_func_choose))]
#             data_temp, data_ids = self.chart.transfer_data(
#                 self.chart.data_read.read_service.read_range_datas_seq_from_times_index_start(
#                     data_origin_port=self.chart.data_origin_ports,
#                     times=datetime.now(),
#                     data_start=data_start,
#                     data_func_choose=self.data_func_choose,
#                     data_nums=[self.chart.data_read_counts for i in
#                                self.chart.data_origin_ports],
#                     data_step=[1 for i in self.chart.data_origin_ports]))
#
#
#         except Exception as e:
#             logger.error(f"图表{self.chart.object_name}读取数据源{self.chart.data_origin_ports}数据失败，失败原因：{ traceback.print_exc()}")
#
#         # 插入数据
#         for origin_data_index in range(len(data_temp)):
#             # 把读取的数据量存储
#             self.chart.data_last_read_counts[origin_data_index] = len(data_temp[origin_data_index])
#             # 把这次获取的数据的最大id放入我们的data_all_counts
#             if len(data_ids[origin_data_index]) != 0:
#                 self.chart.data_all_counts[origin_data_index] = data_ids[origin_data_index][
#                     len(data_ids[origin_data_index]) - 1]
#                 pass
#             else:
#                 self.chart.data_all_counts[origin_data_index] = 0
#                 pass
#             # 插入数据
#             for data_index in range(len(data_temp[origin_data_index])):
#                 self.chart.data[origin_data_index].append(data_temp[origin_data_index][data_index])
#             pass
#         # 插入数据之后的数据长度
#         show_nums = global_setting.get_setting("configer")['graphic'][
#             'data_show_nums']
#         try:
#             for origin_data_index in range(len(self.chart.data)):
#                 # 不同数据源在图表显示的时候需要同步 只要有一方数据源的数量一直是show_nums，而其他数据源出现数据更新暂停 则在图表移除数据
#                 if len(data_temp[origin_data_index]) == 0 and len(self.chart.data[origin_data_index]) != 0:
#                     self.chart.data[origin_data_index].pop(0)
#                 # 每个数据源需要遵守的规则
#                 while len(self.chart.data[origin_data_index]) >= show_nums and len(
#                         self.chart.data[origin_data_index]) != 0:
#                     # logger.info(f"图表{self.object_name}持数据源{origin_data_index}长度为{len(self.data[origin_data_index])}")
#                     self.chart.data[origin_data_index].pop(0)  # 保持数据长度为show_nums
#         except Exception as e:
#             logger.error(f"图表{self.chart.object_name}持数据长度为show_nums失败，series[0]数据长度{len(self.chart.data[0])}，失败原因：{ traceback.print_exc()}")
#         try:
#             # 获取 x 和y值的最大值和最小值来确定坐标轴范围
#             self.chart.get_max_and_min_data()
#             self.chart.update_series()
#             # 设置坐标轴范围
#             self.chart._set_x_axis()
#             self.chart._set_y_axis()
#             # 更新样式
#             self.chart.set_series_lenged_style()
#         except Exception as e:
#             logger.error(f"图表{self.chart.object_name}更新series失败，series[0]数据长度{len(self.chart.data[0])}，失败原因：{ traceback.print_exc()}")
#         pass
