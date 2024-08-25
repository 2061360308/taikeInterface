from datetime import datetime

from bs4 import BeautifulSoup

from utils import UserAgent, CookieManager
import requests
import time, re


def school_calendar(cookie_manager: CookieManager) -> dict:
    url = "https://newjwc.tyust.edu.cn/jwglxt/xtgl/index_cxAreaFive.html?localeKey=zh_CN&gnmkdm=index"

    session = requests.Session()

    need = [
        {
            'name': 'JSESSIONID',
            'domain': 'newjwc.tyust.edu.cn',
            'path': '/jwglxt'
        },
        {
            'name': 'route',
            'domain': 'newjwc.tyust.edu.cn',
            'path': '/'
        },
        {
            'name': '__access_token',
            'domain': '.tyust.edu.cn',
            'path': '/'
        },
        {
            'name': 'phoenix-jwt',
            'domain': 'zero.tyust.edu.cn',
            'path': '/'
        }
    ]

    cookie_manager.set(session, need)

    headers = {
        "Host": "newjwc.tyust.edu.cn",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Accept": "text/html, */*; q=0.01",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": UserAgent,
        "sec-ch-ua-platform": '"Windows"',
        "Origin": "https://newjwc.tyust.edu.cn",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": f"https://newjwc.tyust.edu.cn/jwglxt/xtgl/index_initMenu.html?jsdm=&_t={int(time.time())}",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    response = session.post(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    data = soup.find('tr', class_='tab-th-1').find_all('th')[1].text

    pattern = r"(\d{4}-\d{4})学年(\d)学期\((\d{4}-\d{2}-\d{2})至(\d{4}-\d{2}-\d{2})\)"

    # 使用正则表达式匹配
    match = re.search(pattern, data)

    if match:
        academic_year = match.group(1)  # 学年
        semester = match.group(2)  # 学期
        start_date = datetime.strptime(match.group(3), "%Y-%m-%d")  # 开始日期
        end_date = datetime.strptime(match.group(4), "%Y-%m-%d")  # 结束日期

        return {
            "academic_year": academic_year,
            "semester": semester,
            "start_date": start_date,
            "end_date": end_date
        }
    else:
        raise ValueError("解析校历失败")