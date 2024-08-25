from utils import CookieManager, UserAgent
from datetime import datetime, timedelta
from .daily_course import daily_course


def recent_courses(cookieManager: CookieManager):
    """
    查询近日的课程表（今天和明天两天的课程）

    :param cookieManager:
    :return:
    """

    date = datetime.now().strftime("%Y-%m-%d")
    today = daily_course(cookieManager, date)

    date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = daily_course(cookieManager, date)

    return {
        'today': today,
        'tomorrow': tomorrow
    }