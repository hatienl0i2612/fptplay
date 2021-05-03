import hashlib
import json
import os
import time
from urllib.parse import urlencode
import re
import requests

session = requests.Session()
api_token = "WEBv6Dkdsad90dasdjlALDDDS"
suffix = "/api/v6.2_w/"
domain = "https://api.fptplay.net"


def generate_stoken(path):
    a = int(time.time()) + 10800
    o = path
    token = "%s%s%s%s" % (api_token, a, suffix, o)

    m = hashlib.md5()
    m.update(token.encode())
    return encrypt(m.hexdigest()), a


def encrypt(e):
    n = []
    t = e.upper()
    r = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    for o in range(int(len(t) / 2)):
        i = t[2 * o:2 * o + 2]
        num = '0x%s' % i
        n.append(int(num, 16))

    def convert(e):
        t = ""
        n = 0
        o = 0
        i = [0, 0, 0]
        a = [0, 0, 0, 0]
        s = len(e)
        c = 0
        for z in range(s, 0, -1):
            if n <= 3:
                i[n] = e[c]
            n += 1
            c += 1
            if 3 == n:
                a[0] = (252 & i[0]) >> 2
                a[1] = ((3 & i[0]) << 4) + ((240 & i[1]) >> 4)
                a[2] = ((15 & i[1]) << 2) + ((192 & i[2]) >> 6)
                a[3] = (63 & i[2])
                for v in range(4):
                    t += r[a[v]]
                n = 0
        if n:
            for o in range(n, 3, 1):
                i[o] = 0

            for o in range(n + 1):
                a[0] = (252 & i[0]) >> 2
                a[1] = ((3 & i[0]) << 4) + ((240 & i[1]) >> 4)
                a[2] = ((15 & i[1]) << 2) + ((192 & i[2]) >> 6)
                a[3] = (63 & i[2])
                t += r[a[o]]
            n += 1
            while n < 3:
                t += "="
                n += 1
        return t
    return convert(n).replace('+', '-').replace('/', '_').replace('=', '')


class authentication():
    def __init__(self, path_cookies='', username='', password=''):
        self._path_cookies = path_cookies
        self._username = username
        self._password = password
        self._session = session

    def auth_with_cookies(self):
        file = open(self._path_cookies, 'r', encoding='utf-8')
        cookies = {}
        out = ''
        auth_bearer = ""
        for line in file:
            line = line.strip()
            if '#' not in line:
                item = re.findall(r'[0-9]\s(.*)', line)
                if item:
                    item = item[0].split('\t')
                    if len(item) == 1:
                        cookies[item[0]] = ''
                        out += "%s=''; " % item[0]
                    else:
                        if item[0] == "token":
                            auth_bearer = item[1]
                        cookies[item[0]] = item[1]
        self._session.cookies.update(cookies)
        return auth_bearer


class extractFptPlay():
    def __init__(self, *args, **kwargs):
        self._url = kwargs.get("url")
        self._regex_url = r'''(?x)^((?:http[s]?|fpt):)\/?\/(?:www\.|m\.|)fptplay\.vn.*?\/xem-video\/(?P<slug>.*?)(\/.*?tap\-(?P<ep>\d+)|(\.|$))'''
        self._session = session

    def run(self):
        return self.real_extract()

    def real_extract(self):
        mobj = re.match(self._regex_url, self._url)
        if not mobj:
            return "Invalid url."
        slug = mobj.group("slug")
        ep = mobj.group("ep") or 1
        movie_id = slug.split("-")[-1]
        path = 'stream/vod/%s/%s/auto_vip' % (movie_id, int(ep) - 1)
        token, timestamp = generate_stoken(path)
        url = '%s%s%s?' % (domain, suffix, path) + urlencode({
            "st": token,
            "e": timestamp,
        })
        info = session.get(url)
        return info.json()


url = input(" - url >> ").strip()
data = extractFptPlay(
    url=url).run()
print(json.dumps(data, indent=4, ensure_ascii=False))
