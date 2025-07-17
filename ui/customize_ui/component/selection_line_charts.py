# 下拉选择框的折线图

import sqlite3
import threading

from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QScrollArea
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from entity.MyQThread import MyQThread


class DataFetcher(MyQThread):
    data_fetched = pyqtSignal(float, float)  # 信号传递时间和值

    def __init__(self, data_type):
        super().__init__()
        self.data_type = data_type
        self.stop_thread = False

    def run(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        while not self.stop_thread:
            if self.data_type == "Temperature":
                cursor.execute("SELECT datetime, temperature FROM sensor_data ORDER BY datetime DESC LIMIT 1")
            elif self.data_type == "Humidity":
                cursor.execute("SELECT datetime, humidity FROM sensor_data ORDER BY datetime DESC LIMIT 1")

            data = cursor.fetchone()
            if data:
                time, value = data
                self.data_fetched.emit(time, value)

            time.sleep(1)  # 每秒获取一次数据

        conn.close()


class LineChartWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置布局
        layout = QVBoxLayout(self)

        # 创建下拉框
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Temperature", "Humidity"])
        self.combo_box.currentTextChanged.connect(self.change_data_type)

        # 添加下拉框到布局
        layout.addWidget(QLabel("Select Data Type:"))
        layout.addWidget(self.combo_box)

        # 创建 QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # 创建一个新的 QWidget 用于图表
        self.chart_widget = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_widget)

        # 创建图表
        self.chart = QChart()
        self.chart.setTitle("Real-time Temperature and Humidity Data")

        self.series = QLineSeries()
        self.chart.addSeries(self.series)

        # 设置坐标轴
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        self.chart.setAxisX(self.axis_x, self.series)
        self.chart.setAxisY(self.axis_y, self.series)

        # 创建图表视图
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 将图表视图添加到 layout，并添加到滚动区域
        self.chart_layout.addWidget(self.chart_view)
        scroll_area.setWidget(self.chart_widget)

        # 将滚动区域添加到布局
        layout.addWidget(scroll_area)

        # 初始化数据获取线程
        self.data_fetcher = None
        self.thread = None
        self.data_points = []  # 用于存储最新数据点

        self.change_data_type(self.combo_box.currentText())  # 初始化为默认数据类型

    @pyqtSlot(str)
    def change_data_type(self, data_type):
        if self.data_fetcher and self.data_fetcher.isRunning():
            self.data_fetcher.stop_thread = True
            self.thread.join()

        self.series.clear()  # 清除现有数据
        self.data_points.clear()  # 清除历史数据

        # 启动新线程来获取新的数据类型
        self.data_fetcher = DataFetcher(data_type)
        self.data_fetcher.data_fetched.connect(self.update_chart)

        self.thread = threading.Thread(target=self.data_fetcher.run)
        self.data_fetcher.stop_thread = False
        self.thread.start()

    @pyqtSlot(float, float)
    def update_chart(self, time, value):
        self.data_points.append((time, value))
        # 保持最多 10 个数据点
        if len(self.data_points) > 10:
            self.data_points.pop(0)

        self.series.clear()
        for time, value in self.data_points:
            self.series.append(time, value)

        # 更新坐标轴范围
        self.axis_x.setRange(max(0, time - 10), time)  # X轴范围设置为最近10个数据点
        self.axis_y.setRange(min(val for _, val in self.data_points) - 1,
                             max(val for _, val in self.data_points) + 1)
