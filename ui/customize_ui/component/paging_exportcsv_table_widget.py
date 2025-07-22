import csv
import sys
import sqlite3
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem


class TableWidgetExample(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # 数据库初始化
        self.conn = sqlite3.connect('data.db')  # 请根据需要修改数据库文件名
        self.create_table_if_not_exists()

        # 表格和分页控制
        self.table_widget = QtWidgets.QTableWidget()
        self.current_page = 0
        self.rows_per_page = 10
        self.total_rows = 0
        self.total_columns = 3  # 设置列数为 3

        # 设置表头
        self.table_widget.setColumnCount(self.total_columns)
        self.table_widget.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

        # 控制按钮
        self.first_button = QtWidgets.QPushButton("First")
        self.prev_button = QtWidgets.QPushButton("Previous")
        self.next_button = QtWidgets.QPushButton("Next")
        self.last_button = QtWidgets.QPushButton("Last")
        self.export_button = QtWidgets.QPushButton("Export to CSV")

        # 分页指示器
        self.page_info_label = QtWidgets.QLabel()

        # 连接信号
        self.first_button.clicked.connect(self.go_to_first_page)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        self.last_button.clicked.connect(self.go_to_last_page)
        self.export_button.clicked.connect(self.export_to_csv)

        # 布局设置
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table_widget)

        # 加载控件到布局
        self.pagination_layout = QtWidgets.QHBoxLayout()
        self.pagination_layout.addWidget(self.first_button)
        self.pagination_layout.addWidget(self.prev_button)
        self.pagination_layout.addWidget(self.page_info_label)
        self.pagination_layout.addWidget(self.next_button)
        self.pagination_layout.addWidget(self.last_button)
        self.pagination_layout.addWidget(self.export_button)

        self.layout.addLayout(self.pagination_layout)
        self.setLayout(self.layout)

        self.setWindowTitle("QTableWidget with Pagination and Export")

        # 获取数据并填充表格
        self.update_table()

    def create_table_if_not_exists(self):
        """创建表格，如果表格不存在的话。"""
        cursor = self.conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS data_table
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY,
                           column1
                           TEXT,
                           column2
                           TEXT,
                           column3
                           TEXT
                       )
                       ''')
        # 示例数据（确保只在数据库为空时插入数据）
        cursor.execute("SELECT COUNT(*) FROM data_table")
        if cursor.fetchone()[0] == 0:
            for i in range(1, 101):  # 添加100行示例数据
                cursor.execute("INSERT INTO data_table (column1, column2, column3) VALUES (?, ?, ?)",
                               (f"Row {i}, Col 1", f"Row {i}, Col 2", f"Row {i}, Col 3"))
        self.conn.commit()
        cursor.close()

    def update_table(self):
        """从数据库更新表格以显示当前页面数据"""
        cursor = self.conn.cursor()

        # 获取当前页面的数据
        start_row = self.current_page * self.rows_per_page
        cursor.execute(f"SELECT * FROM data_table ORDER BY id DESC LIMIT {self.rows_per_page} OFFSET {start_row}")
        rows = cursor.fetchall()

        # 如果没有新数据，保持当前表格数据不变
        if not rows:
            cursor.close()
            self.update_page_info()
            return

        # 清空表格并插入获取的数据
        self.table_widget.setRowCount(0)  # 清空表格
        for row in rows:
            self.table_widget.insertRow(self.table_widget.rowCount())
            for col in range(self.total_columns):
                self.table_widget.setItem(self.table_widget.rowCount() - 1, col,
                                          QTableWidgetItem(str(row[col + 1])))  # +1 跳过 ID 列
        cursor.close()

        # 更新分页信息
        self.update_page_info()

    def update_page_info(self):
        """更新分页信息显示"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM data_table")
        self.total_rows = cursor.fetchone()[0]  # 获取总行数
        cursor.close()

        total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page  # 计算总页数
        self.first_button.setEnabled(self.current_page > 0)
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)
        self.last_button.setEnabled(self.current_page < total_pages - 1)

        # 更新分页信息标签
        self.page_info_label.setText(f"Page {self.current_page + 1} of {total_pages}, Total Rows: {self.total_rows}")

    def go_to_first_page(self):
        """切换到第一页"""
        self.current_page = 0
        self.update_table()

    def prev_page(self):
        """切换到上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def next_page(self):
        """切换到下一页"""
        if (self.current_page + 1) * self.rows_per_page < self.total_rows:
            self.current_page += 1
            self.update_table()

    def go_to_last_page(self):
        """切换到最后一页"""
        self.current_page = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page - 1
        self.update_table()

    def export_to_csv(self):
        """导出表格数据到 CSV 文件"""
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)",
                                                             options=options)
        if file_path:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # 写入表头
                headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.total_columns)]
                writer.writerow(headers)

                # 写入数据
                for row in range(self.table_widget.rowCount()):
                    row_data = []
                    for column in range(self.total_columns):
                        item = self.table_widget.item(row, column)
                        row_data.append(item.text() if item is not None else "")
                    writer.writerow(row_data)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    example = TableWidgetExample()
    example.resize(500, 400)
    example.show()
    sys.exit(app.exec())