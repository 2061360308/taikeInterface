import json
import os
import random
import re
import time
import uuid
from datetime import datetime, timedelta
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import base64
from utils import UserAgent, CookieManager


def login(user: str, password: str, cookie_manager: CookieManager) -> bool:
    """
    操作统一门户的登录过程。
    使用到三个url：
    1. https://sso1.tyust.edu.cn/login  GET 通过访问登录页面提取页面中的execution和croypto值，连接还设置了SESSION这个cookie值
    2. https://sso1.tyust.edu.cn/login  POST 提交登录表单，携带用户名、密码、execution、croypto等参数，链接会被重定向到下一个URL，携带了code参数
    3. https://ronghemenhu.tyust.edu.cn/portal/publish/web/login/loginByOauth  POST 提交code参数，获取JSESSIONID这个cookie值

    正常情况下，最终应该携带的cookie值里必需有：
         JSESSIONID     ronghemenhu.tyust.edu.cn  path = /
         SESSION        sso1.tyust.edu.cn  path = /
         SOURCEID_TGC   sso1.tyust.edu.cn  path = /
         rg_objectid    sso1.tyust.edu.cn  path = /


    :param user: 用户名
    :param password: 密码
    :param cookie_manager: CookieManager 对象
    :return:
    """

    # 密码加密
    def des_encrypt(key, data):
        key_bytes = base64.b64decode(key)
        cipher = DES.new(key_bytes, DES.MODE_ECB)
        padded_data = pad(data.encode('utf-8'), DES.block_size)
        encrypted_bytes = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    # 密码解密
    def des_decrypt(key, encrypted_data):
        key_bytes = base64.b64decode(key)
        cipher = DES.new(key_bytes, DES.MODE_ECB)
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), DES.block_size)
        return decrypted_bytes.decode('utf-8')

    # 返回结果中必须要有的cookie
    result_need = [
        {
            'name': 'JSESSIONID',
            'domain': 'ronghemenhu.tyust.edu.cn',
            'path': '/'
        },
        {
            'name': 'SESSION',
            'domain': 'sso1.tyust.edu.cn',
            'path': '/'
        },
        {
            'name': 'SOURCEID_TGC',
            'domain': 'sso1.tyust.edu.cn',
            'path': '/'
        },
        {
            'name': 'rg_objectid',
            'domain': 'sso1.tyust.edu.cn',
            'path': '/'
        }
    ]

    # 检查cookie中是否有符合要求的值，如果有则直接返回成功
    if cookie_manager.check_up(result_need, error=False):
        return True

    # 创建会话
    session = requests.Session()

    # 定义 URL 和 Headers
    url = "https://sso1.tyust.edu.cn/login"
    headers = {
        "User-Agent": UserAgent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://sso1.tyust.edu.cn/login",
        "Origin": "https://sso1.tyust.edu.cn",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }

    # 使用会话对象发送 GET 请求
    response = session.get(url, headers=headers, allow_redirects=True)  # 这里拿到了SESSION这个cookie值
    # print(response.status_code)

    # 解析 HTML 内容
    soup = BeautifulSoup(response.text, 'lxml')

    # 查找特定元素的内容
    execution_element = soup.find(id="login-page-flowkey")
    execution = execution_element.get_text() if execution_element else "Not found"
    # print("execution:", execution)

    croypto_element = soup.find(id="login-croypto")
    croypto = croypto_element.get_text() if croypto_element else "Not found"

    # 设置请求头
    headers = {
        "User-Agent": UserAgent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://sso1.tyust.edu.cn/login",
        "Origin": "https://sso1.tyust.edu.cn",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1"
    }

    # 设置请求体
    data = {
        "username": user,
        "type": "UsernamePassword",
        "_eventId": "submit",
        "geolocation": "",
        "execution": execution,  # 用空字符串代替具体值
        "captcha_code": "",
        "croypto": croypto,
        "password": des_encrypt(croypto, password)
    }

    # 发送 POST 请求
    response = session.post("https://sso1.tyust.edu.cn/login", headers=headers, data=data)

    code = response.url.split('code=')[1]  # 从重定向的 URL 中获取 code 参数的值

    # 定义 URL 和 Headers
    url = "https://ronghemenhu.tyust.edu.cn/portal/publish/web/login/loginByOauth"

    headers = {
        "User-Agent": UserAgent,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://ronghemenhu.tyust.edu.cn",
        "Referer": response.url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Content-Type": "application/json;charset=utf-8"
    }

    # 定义请求体
    data = {
        "code": code,
        "username": "",
        "password": ""
    }

    # 发送 POST 请求
    session.post(url, headers=headers, json=data)

    # 更新cookie
    cookie_manager.update(session.cookies)

    # 检查必须要的cookie是否存在

    try:
        cookie_manager.check_up(result_need)
        return True
    except ValueError as e:
        print(e)
        raise ValueError(f'登录统一门户失败, {e}')


def get_phoenix_jwt(cookie_manager: CookieManager) -> bool:
    """
    获取 phoenix_jwt 的值。
    phoenix_jwt 类似统一门户和教务系统之间的中间值，
    通过统一门户登录后，获取 phoenix_jwt 的值，然后携带 phoenix_jwt 的值才能获取教务系统的访问令牌。

    需要以下的cookie值：
         SESSION        sso1.tyust.edu.cn  path = /
         SOURCEID_TGC   sso1.tyust.edu.cn  path = /
         rg_objectid    sso1.tyust.edu.cn  path = /

    1. 访问 https://sso1.tyust.edu.cn/login?service=http://zero.tyust.edu.cn/login/casCallback/r3IveGXj/，在重定向的url中获取 ticket 参数的值
    2. 提交 POST 请求到 http://zero.tyust.edu.cn/api/access/auth/finish，携带 ticket 参数的值，获取 phoenix_jwt 的值

    正常情况下，最终应该携带的cookie值里必需有：
         phoenix-jwt     zero.tyust.edu.cn  path = /

    :param cookie_manager: CookieManager 对象
    :return:
    """

    # 返回结果中必须要有的cookie
    result_need = [
        {
            'name': 'phoenix-jwt',
            'domain': 'zero.tyust.edu.cn',
            'path': '/'
        }
    ]

    # 检查cookie中是否有符合要求的值，如果有则直接返回成功
    if cookie_manager.check_up(result_need, error=False):
        return True

    session = requests.Session()

    need = [
        {
            'name': 'SESSION',
            'domain': 'sso1.tyust.edu.cn',
            'path': '/'
        },
        {
            'name': 'SOURCEID_TGC',
            'domain': 'sso1.tyust.edu.cn',
            'path': '/'
        },
        {
            'name': 'rg_objectid',
            'domain': 'sso1.tyust.edu.cn',
            'path': '/'
        }
    ]

    cookie_manager.set(session, need)
    # 设置请求头
    headers = {
        "User-Agent": UserAgent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "http://zero.tyust.edu.cn/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site"
    }

    # 发起请求
    response = session.get(
        "https://sso1.tyust.edu.cn/login?service=http://zero.tyust.edu.cn/login/casCallback/r3IveGXj/",
        headers=headers)

    ticket = response.url.split('ticket=')[1]  # 从重定向的 URL 中获取 ticket 参数的值

    body = {
        "externalId": "r3IveGXj",
        "data": {
            "callbackUrl": "http://zero.tyust.edu.cn/login/casCallback/r3IveGXj/",
            "ticket": ticket,
            "deviceId": uuid.uuid1().hex,
        },
        "wechatSessionId": ""
    }

    # 发起 POST 请求
    session.post(
        "http://zero.tyust.edu.cn/api/access/auth/finish",
        headers=headers,
        json=body
    )

    # session.cookies.set('phoenix-jwt', session.cookies.get('phoenix-jwt'), domain='.tyust.edu.cn', path='/')

    # 更新cookie
    cookie_manager.update(session.cookies)

    # 检查必须要的cookie是否存在
    try:
        cookie_manager.check_up(result_need)
        return True
    except ValueError as e:
        print(e)
        raise ValueError(f'获取"phoenix-jwt"失败, {e}')


def login_jwglxt(cookie_manager: CookieManager) -> bool:
    """
    登录教务系统。

    步骤：
        1. 携带 zero.tyust.edu.cn 域  path = / 的 phoenix-jwt 的 cookie 值
            访问 https://zero.tyust.edu.cn/api/access/user/info
            返回json数据，的 ['data']['token'] 下 的值为 access_token

        2. 访问 f"https://newjwc.tyust.edu.cn/sso/jasiglogin/jwglxt?__access_token={access_token}"
            链接会多次重定向，路径如下
                https://newjwc.tyust.edu.cn/sso/jasiglogin/jwglxt?__access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxMTk5Nzk2MzYxODM1MzE1MjEiLCJhdXRoVHlwZSI6NSwiZXh0ZXJuYWxJZCI6InIzSXZlR1hqIiwic2FsdCI6IjExOTk3OTYzNjI1MDY0MDM4NSIsImV4cCI6MTcyNTE3NDU3MiwiaXNzIjoiZXhwIn0.HLMEQ736ng__DJxpmw6ou0r1slIy284ZG1dz1X1HLJI
                https://newjwc.tyust.edu.cn/sso/jasiglogin/jwglxt
                https://newjwc.tyust.edu.cn/jwglxt/ticketlogin?uid=202220060127&timestamp=1724569773&verify=27FA8B8C22CA71926798D95BEDE7D7BB
                https://newjwc.tyust.edu.cn/jwglxt/xtgl/login_slogin.html

        正常情况下，最终应该携带的cookie值里必需有：
            JSESSIONID     newjwc.tyust.edu.cn  path = /jwglxt
            JSESSIONID     newjwc.tyust.edu.cn  path = /sso
            route          newjwc.tyust.edu.cn  path = /
            __access_token       .tyust.edu.cn  path = /

    :return:
    """

    # 返回结果中必须要有的cookie
    result_need = [
        {
            'name': 'JSESSIONID',
            'domain': 'newjwc.tyust.edu.cn',
            'path': '/jwglxt'
        },
        {
            'name': 'JSESSIONID',
            'domain': 'newjwc.tyust.edu.cn',
            'path': '/sso'
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

    # 检查cookie中是否有符合要求的值，如果有则直接返回成功
    if cookie_manager.check_up(result_need, error=False):
        return True

    session = requests.Session()

    need = [{
        'name': 'phoenix-jwt',
        'domain': 'zero.tyust.edu.cn',
        'path': '/',
    }]

    cookie_manager.set(session, need)

    # 设置请求头
    headers = {
        "User-Agent": UserAgent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "http://zero.tyust.edu.cn/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site"
    }

    data = session.get('https://zero.tyust.edu.cn/api/access/user/info', headers=headers)
    #
    access_token = data.json()['data']['token']

    url = f"https://newjwc.tyust.edu.cn/sso/jasiglogin/jwglxt?__access_token={access_token}"
    session.get(url, headers=headers, allow_redirects=True)

    cookie_manager.update(session.cookies)

    # 检查必须要的cookie是否存在

    try:
        cookie_manager.check_up(result_need)
        return True
    except ValueError as e:
        print(e)
        raise ValueError(f'登录教务系统失败, {e}')


if __name__ == '__main__':


    # 查询空闲教室
    # result = free_room(
    #     cookie_manager,
    #     week=2,
    #     day=1,
    #     selected_jc=[1, 2],
    #     limit=25,
    #     page=1,
    # )

    # 查询校历
    print(current_week_and_weekday(cookie_manager))
    print(tomorrow_course(cookie_manager))

    # pprint(result)
