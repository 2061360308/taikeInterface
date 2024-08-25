from .school_calendar import school_calendar
from utils import CookieManager, UserAgent
from datetime import datetime
import requests


def current_week_and_weekday(cookie_manager: CookieManager, start: datetime | None = None,
                             end: datetime | None = None) -> (int, int):
    """
    查询当前是第几周

    :param cookie_manager:
    :param start: 开始日期
    :param end: 结束日期
    :return:
    """

    if start is None or end is None:
        calendar = school_calendar(cookie_manager)
        start = calendar['start_date']
        end = calendar['end_date']

    # 查看给出的日期是否在学期内
    if start > datetime.now() or end < datetime.now():
        raise ValueError("当前日期不在学期内")

    now = datetime.now()

    delta = now - start
    week_number = delta.days // 7 + 1
    weekday_number = now.weekday() + 1  # Python的weekday()方法返回0-6，0表示星期一，这里加1使其返回1-7
    return week_number, weekday_number