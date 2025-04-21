from datetime import datetime, timedelta


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

    @classmethod
    def get_times_week_info(cls, times: datetime = datetime.now()):
        """
        获取日期的年份 所属第几周 这周的第几天
        :param times datetime类型
        :return: year, week_number, weekday
        """
        # 获取 ISO 日历信息
        year, week_number, weekday = times.isocalendar()
        # weekday: 1=Monday, 2=Tuesday, ..., 7=Sunday
        return year, week_number, weekday

    @classmethod
    def get_times_before_days(cls, times: datetime = datetime.today(), before_days: int = 1):
        """
        获取times的几天前的日期信息
        :param times datetime类型
        :param before_days 几天前
        :return: days_ago (int)日期的int值 和 格式化的日期字符串days_ago.strftime("%Y-%m-%d")
        """
        days_ago = times - timedelta(days=before_days)
        # weekday: 1=Monday, 2=Tuesday, ..., 7=Sunday
        return days_ago, days_ago.strftime("%Y-%m-%d")

    pass
