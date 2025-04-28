from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCharts import QChart, QChartView, QBarSet, QStackedBarSeries, QBarCategoryAxis, QValueAxis
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt


class MultiStackedBarChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        categories = ["点1", "点2", "点3", "点4"]

        # 创建三个堆叠柱子系列
        series1 = self.create_stacked_series("系列1", [1, 3, 5, 7], [2, 2, 4, 2])
        series2 = self.create_stacked_series("系列2", [3, 2, 6, 4], [1, 4, 2, 1])
        series3 = self.create_stacked_series("系列3", [2, 5, 3, 6], [3, 1, 2, 3])

        # 创建图表
        chart = QChart()
        chart.addSeries(series1)
        chart.addSeries(series2)
        chart.addSeries(series3)
        chart.setTitle("一个点三个柱子，每柱堆叠两个数据，显示数值")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # 设置类别轴（X轴）
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)

        # 设置数值轴（Y轴）
        axisY = QValueAxis()
        axisY.setRange(0, 15)
        chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)

        # 绑定坐标轴
        for series in [series1, series2, series3]:
            series.attachAxis(axisX)
            series.attachAxis(axisY)

        # 创建图表视图
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 在柱头添加数值标签
        series1.setLabelsVisible(True)
        series2.setLabelsVisible(True)
        series3.setLabelsVisible(True)

        # 设置窗口布局
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(chart_view)
        self.setCentralWidget(widget)
        self.resize(900, 600)

    def create_stacked_series(self, name, data1, data2):
        """ 创建一个堆叠柱状图系列 """
        set1 = QBarSet(f"{name} 数据1")
        set2 = QBarSet(f"{name} 数据2")
        set1.append(data1)
        set2.append(data2)
        series = QStackedBarSeries()
        series.append(set1)
        series.append(set2)
        return series

    def add_value_labels(self, series, data1, data2):
        """ 在柱子上添加数值标签 """
        for i in range(len(data1)):
            value1 = data1[i]
            value2 = data2[i]
            total = value1 + value2
            series.barSets()[0].setLabel(f"{value1}")
            series.barSets()[1].setLabel(f"{value2}")
            # 也可以在这里自定义标签格式


if __name__ == "__main__":
    app = QApplication([])
    window = MultiStackedBarChartWindow()
    window.show()
    app.exec()
