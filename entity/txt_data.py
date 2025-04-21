import dataclasses


@dataclasses
class txt_data():
    """
    txt数据的格式
    """
    id: int
    data: float | str
    date: str | int
