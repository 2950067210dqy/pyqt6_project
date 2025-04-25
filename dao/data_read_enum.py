# 数据读取从哪开始的方式
from enum import Enum


class Data_Read_Where_Start_Func(Enum):
    DELAY_CONFIG = 0  # 采用配置里的delay秒前开始读取
    INDEX = 1  # 从index 开始读取
    DELAY_1 = 2  # 读取1秒前的数据
    pass
