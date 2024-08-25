import random
import json
import os
from requests.cookies import RequestsCookieJar
import requests

def random_ua():
    user_agents = [
        # Chrome User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.3.5211 SLBChan/152"
        "Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 "
        "Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",

        # Firefox User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",

        # Safari User Agents
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 "
        "Safari/605.1.15",

        # Edge User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 "
        "Safari/537.36 Edg/91.0.864.59",

        # Opera User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 "
        "Safari/537.36 OPR/77.0.4054.172"
    ]
    return random.choice(user_agents)

UserAgent = random_ua()


class CookieManager:
    """
    Cookie 管理器
    """
    current_path = os.path.dirname(os.path.abspath(__file__))
    cookies_json_path = os.path.join(current_path, 'cookies.json')

    def __init__(self):

        if not os.path.exists(self.cookies_json_path):
            self.cookies = {}
        else:
            with open('cookies.json', 'r', encoding='utf-8') as f:
                self.cookies = json.loads(f.read())

    def update(self, cookies: RequestsCookieJar):
        """
        更新cookie
        传入session.cookies对象，更新当前保存的cookie

        :param cookies: requests.cookies.RequestsCookieJar 对象
        :return:
        """
        for cookie in cookies:
            name = cookie.name
            value = cookie.value
            expires = cookie.expires
            domain = cookie.domain
            path = cookie.path
            if domain not in self.cookies:
                self.cookies[domain] = {}

            key = f'{name}_{path}'

            self.cookies[domain][key] = {
                'name': name,
                'value': value,
                'expires': expires,
                'path': path
            }

        self.__save()

    def add(self, name, value, expires=None, domain=None, path='/'):
        """
        设置一条cookie

        :param name:
        :param value:
        :param expires:
        :param domain:
        :param path:
        :return:
        """
        if domain not in self.cookies:
            self.cookies[domain] = {}

        key = f'{name}_{path}'

        self.cookies[domain][key] = {
            'name': name,
            'value': value,
            'expires': expires,
            'path': path
        }

        self.__save()

    def set(self, session: requests.Session, need=None) -> None:
        """
        使用当前保存的cookie更新session对象

        :param session: requests.Session
        :param need: 如果给出则在设置前先检查是否有这些cookie，need是一个列表，每个元素是一个字典，字典包含name, domain（可选）, path（可选）
        :return:
        """

        if need:
            self.check_up(need)

        for domain in self.cookies:
            for key in self.cookies[domain]:
                cookie = self.cookies[domain][key]
                session.cookies.set(cookie['name'], cookie['value'], domain=domain, path=cookie['path'],
                                    expires=cookie['expires'])

    def __save(self):
        with open(self.cookies_json_path, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(self.cookies, indent=4, ensure_ascii=False))

    def has(self, name, domain=None, path=None):
        """
        检查是否存在某个cookie
        :param name: 必选 cookie名
        :param domain: 可选 域名
        :param path: 可选 路径
        :return:
        """
        for item_domain in self.cookies:
            for key in self.cookies[item_domain]:
                cookie = self.cookies[item_domain][key]

                if cookie['name'] == name:

                    if domain and domain != item_domain:
                        continue

                    if path and path != cookie['path']:
                        continue
                    # 查找成功
                    return True
        return False

    def check_up(self, need, error=True):
        """
        检查是否有某些cookie

        :param need:
        :param error: 是否抛出异常, 设置为False则返回True 和 False
        :return:
        """

        for item in need:
            name = item.get('name', None)
            if name is None:
                continue

            domain = item.get('domain', None)
            path = item.get('path', None)
            if not self.has(name, domain, path):
                if error:
                    raise ValueError(f"缺少cookie: 在 {domain} 域下的 {name}  path = {path}")
                else:
                    return False

        if not error:
            return True