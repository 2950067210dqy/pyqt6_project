from dataclasses import dataclass


@dataclass
class xlsx_data():
    """
    csv数据的格式
    """
    id: int = 1
    data: float | str = 1
    date: str | int = 1
