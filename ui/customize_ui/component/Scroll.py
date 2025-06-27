from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout


class Scroll(QObject):
    def __init__(self):
        super().__init__()

    @classmethod
    def set_scroll_to_component(cls, component, component_parent_layout, scroll_object_name):
        """
        添加滑动条到组件
        :return:
        """

        # 找到 scrollarea
        scrollArea: QScrollArea = QScrollArea()
        scrollArea.setObjectName(scroll_object_name)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(component)
        component_parent_layout.addWidget(scrollArea)
