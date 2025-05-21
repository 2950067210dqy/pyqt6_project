from datetime import datetime


class time_util():
    """
    时间工具类
    """
    def __init__(self):
        pass
    @classmethod
    def get_current_week_info(cls):
        """
        获取当前日期的年份 所属第几周 这周的第几天
        :return: year, week_number, weekday
        """
        # 获取当前日期
        now = datetime.now()
        # 获取 ISO 日历信息
        year, week_number, weekday = now.isocalendar()
        # weekday: 1=Monday, 2=Tuesday, ..., 7=Sunday
        return year, week_number, weekday
    pass