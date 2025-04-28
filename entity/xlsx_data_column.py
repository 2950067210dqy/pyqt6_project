from dataclasses import dataclass, field


@dataclass
class xlsx_datas_device_item():
    """
    csv数据的格式
    """

    name: str = ""  # device name
    data: list = field(default_factory=list)  # 数据[13,313,]


@dataclass
class xlsx_datas_phase_item():
    """
    csv数据的格式
    """
    name: str = ""  # A相
    data: list = field(default_factory=list)  # 数据[xlsx_datas_device_item]


@dataclass
class xlsx_datas_item_x():
    name: list = field(default_factory=list)  # x轴数据 数据项描述
    data: list = field(default_factory=list)  # x轴数据
    pass


@dataclass
class xlsx_datas_item():
    x: xlsx_datas_item_x = field(default_factory=xlsx_datas_item_x)  # x轴数据 xlsx_datas_item_x
    y: list = field(default_factory=list)  # y轴数据 [xlsx_datas_phase_item]
    pass


@dataclass
class xlsx_datas_type_item():
    name: str = ""  # 功率 电压啥的
    data: xlsx_datas_item = field(default_factory=xlsx_datas_item)  # xlsx_datas_item
    pass


@dataclass
class xlsx_data():
    """
    csv数据的格式
    """
    rated_voltage: float = 0  # 额定电压
    rated_voltage_unit: str = ''
    rated_frequency: float = 0  # 额定频率
    rated_frequency_unit: str = ''
    name: str = ""  # 各种描述

    data: list = field(default_factory=list)  # [xlsx_datas_type_item]
