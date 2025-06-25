from PyQt6 import QtCore, QtGui, QtWidgets

from config.global_setting import global_setting


class Ui_left_menu_btn(QtWidgets.QPushButton):

    def __init__(self, parentWidget: QtWidgets.QWidget, parentLayout: QtWidgets.QVBoxLayout, id, title, icon_path,
                 root_object_name):
        self.btn = QtWidgets.QPushButton(parent=parentWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(20)
        sizePolicy.setVerticalStretch(21)
        sizePolicy.setHeightForWidth(self.btn.sizePolicy().hasHeightForWidth())
        self.btn.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(False)
        self.btn.setFont(font)
        self.btn.setStyleSheet(global_setting.get_setting("theme_manager").get_button_style(isSelected=False))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f":/{global_setting.get_setting('style')}/{icon_path}"), QtGui.QIcon.Mode.Normal,
                       QtGui.QIcon.State.Off)
        # 设置图标时附加元数据
        # 存储路径元数据。
        self.btn.setProperty("icon_name", icon_path)

        self.btn.setIcon(icon)
        self.btn.setIconSize(QtCore.QSize(20, 20))
        self.btn.setAutoDefault(False)
        self.btn.setDefault(False)
        self.btn.setFlat(True)
        self.btn.setObjectName("btn" + str(id))
        parentLayout.addWidget(self.btn)
        self.retranslateUi(root_object_name, title)

    def retranslateUi(self, root_object_name, title):
        _translate = QtCore.QCoreApplication.translate
        self.btn.setText(_translate(root_object_name, title))

    def click_connect(self, index: int, frame: QtWidgets.QWidget, tab_ids):
        self.btn.clicked.connect(lambda: self.click_method(index, frame, tab_ids))
        pass

    def click_method(self, index, frame: QtWidgets.QWidget, tab_ids):
        # 设置全局变量当前菜单id
        global_setting.set_setting("menu_id_now", index)
        # 找到与之对应的tab组件
        base_objectname_pre = "tab"
        base_objectname_suff = "_frame"
        current_tab = frame.findChild(QtWidgets.QWidget, base_objectname_pre + str(index) + base_objectname_suff)
        # 并将tab页设为可见
        current_tab.setVisible(True)
        # 将其他tab页设为不可见
        for i in tab_ids:
            if i != index:
                other_tab = frame.findChild(QtWidgets.QWidget,
                                            base_objectname_pre + str(i) + base_objectname_suff)
                other_tab.setVisible(False)
        # 更改当前按钮的样式
        base_objectname_pre_btn = "btn"
        current_btn = frame.findChild(QtWidgets.QPushButton, base_objectname_pre_btn + str(index))
        current_btn.setStyleSheet(global_setting.get_setting("theme_manager").get_button_style(isSelected=True))
        # 更改其他按钮的样式
        for i in tab_ids:
            if i != index:
                other_btn = frame.findChild(QtWidgets.QPushButton, base_objectname_pre_btn + str(i))
                other_btn.setStyleSheet(global_setting.get_setting("theme_manager").get_button_style(isSelected=False))
        pass
