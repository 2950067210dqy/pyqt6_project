import dataclasses


@dataclasses
class csv_data():
    """
    txt数据的格式
    """
    id: int
    data: float | str
    date: str | int
