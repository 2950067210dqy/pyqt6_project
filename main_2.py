from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCharts import QChart, QChartView, QBarSet, QStackedBarSeries, QBarCategoryAxis, QValueAxis
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt


class MultiStackedBarChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        categories = ["0,20", "0,40", "60,50", "点4"]

        # 创建三个堆叠柱子系列
        series1 = self.create_stacked_series("A相", [1, 3, 5, 7], [2, 2, 4, 2])
        series2 = self.create_stacked_series("B相", [3, 2, 6, 4], [1, 4, 2, 1])
        series3 = self.create_stacked_series("C相", [2, 5, 3, 6], [3, 1, 2, 3])

        # 创建图表
        chart = QChart()
        chart.addSeries(series1)
        chart.addSeries(series2)
        chart.addSeries(series3)
        chart.setTitle("一个点三个柱子，每柱堆叠两个数据")
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

        # 设置窗口布局
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(chart_view)
        self.setCentralWidget(widget)
        self.resize(900, 600)

    def create_stacked_series(self, name, data1, data2):
        """ 创建一个堆叠柱状图系列 """
        set1 = QBarSet(f"{name} TK123")
        set2 = QBarSet(f"{name} TK123B")
        set1.append(data1)
        set2.append(data2)
        # 显示数值标签
        set1.setLabelVisible(True)
        set2.setLabelVisible(True)
        series = QStackedBarSeries()
        series.append(set1)
        series.append(set2)
        return series


if __name__ == "__main__":
    app = QApplication([])
    window = MultiStackedBarChartWindow()
    window.show()
    app.exec()
