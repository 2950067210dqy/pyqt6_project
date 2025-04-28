from dataclasses import dataclass, field


@dataclass
class xlsx_datas_item_each_result():
    """
    csv数据的格式
    """

    result: float = 0  # 实际电
    result_error: float = 0  # 实际 误差
    result_unit: str = ''
    result_error_unit = str = ''  # 误差单位


@dataclass
class xlsx_datas_item_each():
    """
    csv数据的格式
    """
    y_counts: int = 0
    rated_current_datas: list = field(default_factory=list)  # 数据[xlsx_datas_item_each_result]

    result_voltage_datas: list = field(default_factory=list)  # 数据[xlsx_datas_item_each_result]
    result_current_datas: list = field(default_factory=list)  # 数据[xlsx_datas_item_each_result]
    result_power_datas: list = field(default_factory=list)  # 数据[xlsx_datas_item_each_result]
    result_phase_datas: list = field(default_factory=list)  # 数据[xlsx_datas_item_each_result]


@dataclass
class xlsx_datas_item_device():
    device_name: str = ''  # 设备名称
    data: xlsx_datas_item_each = field(default_factory=xlsx_datas_item_each)  # 数据[xlsx_datas_item_each]
    pass


@dataclass
class xlsx_datas_item_three_phase_item():
    rated_phase_angle: int = 0  # 额定相角
    rated_phase_angle_unit: str = ''
    data: list = field(default_factory=list)  # 数据[xlsx_datas_item_device]
    pass


@dataclass
class xlsx_datas_item_three_phase():
    """
    csv数据的格式
    """
    phase_name: str = ""  # 电相名称
    data: list = field(default_factory=list)  # 数据[xlsx_datas_item_three_phase_item]


@dataclass
class xlsx_datas():
    """
    csv数据的格式
    """

    rated_voltage: float = 0  # 额定电压
    rated_voltage_unit: str = ''
    rated_frequency: float = 0  # 额定频率
    rated_frequency_unit: str = ''

    datas: list = field(default_factory=list)  # 包括每个设备的相关数据[xlsx_datas_item_three_phase()]
