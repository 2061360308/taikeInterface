from .school_calendar import school_calendar
from utils import CookieManager, UserAgent
from datetime import datetime
import requests

def daily_course(cookieManager, date):
    """
    查询某一天的课程表

    :param cookieManager:
    :param date: %Y-%m-%d
    :return:
    """
    url = "https://newjwc.tyust.edu.cn/jwglxt/pkgl/xlglMobile_cxSkxx.html"

    session = requests.Session()
    cookieManager.set(session)

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Content-Length": "13",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "newjwc.tyust.edu.cn",
        "Origin": "https://newjwc.tyust.edu.cn",
        "Referer": "https://newjwc.tyust.edu.cn/jwglxt/pkgl/xlglMobile_cxXlIndexForxs.html",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    data = {
        "rq": date
    }

    response = session.post(url, headers=headers, data=data)

    return response.json()