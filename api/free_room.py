from datetime import datetime
import requests
from utils import UserAgent, CookieManager


def free_room(cookie_manager: CookieManager, week, day, selected_jc: list, limit=15, page=1, year=None) -> dict:
    """
    查询空闲教室。
    :return:
    """

    def calculate_jcd(selected_jc: list) -> str:
        """
        计算用户选择的节次值。

        参数:
        selected_jc (list of int): 用户选择的节次列表，每个元素为节次的索引值（从1开始）。

        返回:
        int: 计算得到的节次值。
        """
        jcd = 0
        for jc in selected_jc:
            jcd += 2 ** (jc - 1)
        return str(jcd)

    if year is None:
        year = datetime.now().year

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
        }
    ]

    cookie_manager.set(session, need)

    jcd = calculate_jcd(selected_jc)

    # 定义请求头
    headers = {
        "User-Agent": UserAgent,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://newjwc.tyust.edu.cn",
        "Referer": "https://newjwc.tyust.edu.cn/jwglxt/cdjy/cdjy_cxKxcdlb.html?gnmkdm=N2155&layout=default",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    # 定义请求数据
    data = {
        "fwzt": "cx",
        "xqh_id": "4",
        "xnm": str(year),  # 学年
        "xqm": "3",
        "cdlb_id": "",
        "cdejlb_id": "",
        "qszws": "",
        "jszws": "",
        "cdmc": "",
        "lh": "",
        "jyfs": "0",
        "cdjylx": "",
        "zcd": str(week),  # 第n周
        "xqj": str(day),  # 星期几
        "jcd": jcd,
        "_search": "false",
        "nd": "1724436533249",
        "queryModel.showCount": str(limit),  # 返回数据的最大条数
        "queryModel.currentPage": str(page),  # 当前页数
        "queryModel.sortName": "cdbh",
        "queryModel.sortOrder": "asc",
        "time": "1"
    }

    # 发送POST请求
    response = session.post("https://newjwc.tyust.edu.cn/jwglxt/cdjy/cdjy_cxKxcdlb.html?doType=query&gnmkdm=N2155",
                            headers=headers, data=data)

    return response.json()