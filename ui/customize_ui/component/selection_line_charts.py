# 下拉选择框的折线图

import sqlite3
import sys
import threading
import time

from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QScrollArea, QApplication
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, Qt

from dao.SQLite.Monitor_Datas_Handle import Monitor_Datas_Handle
from dao.SQLite.SQliteManager import SQLiteManager
from entity.MyQThread import MyQThread


class DataFetcher(MyQThread):
    data_fetched = pyqtSignal(dict)  # 信号传递时间和值

    def __init__(self, name, table_name, data_type, data_types):
        super().__init__(name=name)
        self.table_name = table_name
        # 选中的数据类型
        self.data_type = data_type
        # 所有的数据类型
        self.data_types = data_types
        # 数据库操作类
        self.handle: Monitor_Datas_Handle = None

    def stop(self):
        super().stop()
        if self.handle is not None:
            self.handle.stop()

    def pause(self):
        super().pause()
        if self.handle is not None:
            self.handle.stop()

    def dosomething(self):
        if self.handle is not None:
            self.handle.stop()
        self.handle = Monitor_Datas_Handle()  # # 创建数据库
        data = {}
        """
                {
                    'temperature':{
                    'desc':'温度',
                    'value':1
                    },
                    'time':{
                    'desc':'获取时间',
                    'value':1
                    },
                }
        """
        for data_type_temp in self.data_types:
            if self.data_type == data_type_temp:
                data = self.handle.query_data_one_column_current(table_name=self.table_name,
                                                                 columns_flag=[data_type_temp,
                                                                               SQLiteManager.TIME_COLUMN_NAME])
                break
        else:
            pass

        self.data_fetched.emit(data)

        time.sleep(1)  # 每秒获取一次数据


class LineChartWidget(QWidget):

    def __init__(self, type, data_type, mouse_cage_number=0):
        """

        :param type:模块类型 UFC,UGC等 枚举类
        :param data_type: 数据类型 比如monitor_data senior_state等
        """
        super().__init__()
        self.mouse_cage_number = mouse_cage_number
        self.type = type
        self.data_type = data_type
        self.columns_desc_combobox_data = []
        if self.mouse_cage_number == 0:
            self.table_name = f"{self.type.value['name']}_{self.data_type}"
        else:
            self.table_name = f"{self.type.value['name']}_{self.data_type}_cage_{self.mouse_cage_number}"

        # 数据库操作类
        self.handle: Monitor_Datas_Handle = None
        self.get_combobox_data()
        self.initUI()

    def get_combobox_data(self):
        """
        获取combobox 下拉框数据
        :return:
        """
        self.handle = Monitor_Datas_Handle()  # # 创建数据库
        self.columns_desc_combobox_data = self.handle.query_meta_table_data(self.table_name)
        # 获取表格column数据

    def initUI(self):
        # 设置布局
        layout = QVBoxLayout(self)

        # 创建下拉框
        self.combo_box = QComboBox()
        self.combo_box.addItems(self.columns_desc_combobox_data)
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
        self.chart.setTitle("Real-time  Data")

        self.series = QLineSeries()
        self.chart.addSeries(self.series)

        # 设置坐标轴
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignLeft)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        # 创建图表视图
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 将图表视图添加到 layout，并添加到滚动区域
        self.chart_layout.addWidget(self.chart_view)
        scroll_area.setWidget(self.chart_widget)

        # 将滚动区域添加到布局
        layout.addWidget(scroll_area)

        # 初始化数据获取线程
        self.data_fetcher_thread: DataFetcher = None
        self.data_points = []  # 用于存储最新数据点

        self.change_data_type(self.combo_box.currentText())  # 初始化为默认数据类型

    @pyqtSlot(str)
    def change_data_type(self, data_type):
        if self.data_fetcher_thread and self.data_fetcher_thread.isRunning():
            self.data_fetcher_thread.stop()

        self.series.clear()  # 清除现有数据
        self.data_points.clear()  # 清除历史数据

        # 启动新线程来获取新的数据类型
        self.data_fetcher_thread = DataFetcher(name="tab_2_tab_0_data_fetch_thread", table_name=self.table_name,
                                               data_type=self.data_type,
                                               data_types=self.columns_desc_combobox_data)
        self.data_fetcher_thread.data_fetched.connect(self.update_chart)
        self.data_fetcher_thread.start()

    @pyqtSlot(dict)
    def update_chart(self, data):
        self.data_points.append((data['time']['value'], data[self.data_type]['value']))
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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建一个示例 SQLite 数据库和表格以进行演示
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            datetime REAL,
            temperature REAL,
            humidity REAL
        )
    ''')
    # 插入一些示例数据
    for i in range(100):
        cursor.execute("INSERT INTO sensor_data (datetime, temperature, humidity) VALUES (?, ?, ?)",
                       (i, 20 + i * 0.1, 50 + i * 0.2))
    conn.commit()
    conn.close()

    main_window = QWidget()
    main_layout = QVBoxLayout(main_window)

    chart_widget = LineChartWidget()
    main_layout.addWidget(chart_widget)

    main_window.setLayout(main_layout)
    main_window.setWindowTitle("Line Chart with Scroll Area")
    main_window.resize(800, 600)
    main_window.show()

    sys.exit(app.exec())
