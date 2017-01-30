# -*- coding: utf-8 -*-

import copy
import random
import re
import string

import sys
from bs4 import BeautifulSoup
from bs4 import ResultSet
from bs4 import Tag


def propercase(text):
    """
    Converts text to proper case.
        E.g. hello WORLD -> Hello World
            hello,world -> Hello,World
    """
    words = re.finditer("[a-zA-Z]+", text)

    for w in words:
        start = w.start(0)
        end = w.end(0)
        new_part = "{}{}".format(string.upper(text[start]), string.lower(text[start + 1:end]))
        text = re.sub(w.group(), new_part, text)

    return text


def clean_text(text):
    value = text[0] if len(text) else ''
    value = re.sub("\n", " ", value)
    value = re.sub("\\s+", " ", value)
    value = value.strip()
    return value


def scrape_tag_contents(tags, html):
    tag_list = copy.copy(tags)
    if isinstance(html, Tag):
        soup = html
    else:
        soup = BeautifulSoup(html, "lxml")
    results = []
    content_tag, content_attr = tag_list.pop()
    if not len(tag_list):
        return list(soup.findAll(name=content_tag, attrs=content_attr))
    first_tag, first_attr = tag_list.pop(0)
    element_list = soup.findAll(name=first_tag, attrs=first_attr)

    for tag, attr in tag_list:
        temp = ResultSet([], ())
        for element in element_list:
            if isinstance(attr, dict):
                temp += element.findAll(name=tag, attrs=attr)
            elif isinstance(attr, unicode) or isinstance(attr, str):
                if element.has_attr(attr):
                    temp.append(element[attr])

        element_list = temp

    for element in element_list:
        if content_tag == "regex":
            pattern = content_attr
            text = element
            if not isinstance(text, str):
                text = element.text
            if text:
                match = re.findall(pattern, text)
                if match:
                    results.append(match[0])
        elif content_attr is None or content_attr == "":
            if content_tag is None or content_tag == "":
                text = element
            else:
                text = element.find(content_tag)
            if text:
                results.append(text.text)
        elif content_tag is None or content_tag == "":
            if element.has_attr(content_attr):
                results.append(element[content_attr])
        else:
            info_container = element.findAll(name=content_tag)
            for container in info_container:
                if isinstance(content_attr, dict):
                    results.append(container)
                elif info_container.has_attr(content_attr):
                    results.append(container[content_attr])
    return results


def is_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    match = regex.match(url)
    return True if match else None



def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_len=100, colour=None):
    """Call in a loop to create terminal progress bar

    Parameters
    ----------
    iteration: int
        Current iteration
    total: int
        Total iterations
    prefix: str
        Prefix string
    suffix: str
        Suffix string
    decimals: int
        Positive number of decimals in percent complete
    bar_len: int
        Character length of bar

    """
    format_str = "{0:." + str(decimals) + "f}"
    percents = format_str.format(100 * (iteration / float(total)))
    filled_len = int(round(bar_len * iteration / float(total)))
    bar = '█' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


"""
Network Utils


"""

"""
List of various browser User-Agent headers
"""
USER_AGENT_HEADER_LIST = [

    # I.E. 11.0
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",

    # I.E. 10.0
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 7.0; InfoPath.3; .NET CLR 3.1.40767; Trident/6.0; en-IN)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/4.0; InfoPath.2; SV1; .NET CLR 2.0.50727; WOW64)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)",
    "Mozilla/4.0 (Compatible; MSIE 8.0; Windows NT 5.2; Trident/6.0)",
    "Mozilla/4.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/1.22 (compatible; MSIE 10.0; Windows 3.1)",

    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",

    # Chrome 41.0.2227.1


    # Chrome 41.0.2228.0
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",

    # Chrome 41.0.2227.1
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",

    # Chrome 41.0.2227.0
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",

    # Chrome 41.0.2226.0
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",

    # Chrome 41.0.2225.0
    "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",

    # Chrome 41.0.2224.3
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",

    # Firefox 40.1
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",

    # Firefox 36.0
    "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",

    # Firefox 33.0
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0",

    # Firefox 31.0
    "Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0",
    "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",

    # Firefox 29.0
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0",

]

BASE_REQUEST_HEADER = {
    'Accept-Language': 'en-GB,en;q=0.8,en-US;q=0.6',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}

PROXY_PORTS = [
    "1080",
    "1085",
    "1090"
]

PROXY_USERNAME = "user4344221"
PROXY_PASSWORD = "IBJbGIFF"

PROXY_IPS = [
    'proxy.torguard.org'
    'proxy.torguard.io'
    "46.166.137.66",
    "46.166.137.67",
    "46.166.137.68",
    "46.166.137.69",
    "46.166.137.70",
    "46.166.137.71",
    "46.166.137.72",
    "46.166.137.73",
    "46.166.137.74",
    "199.19.94.93",
    "199.19.94.126",
    "199.19.94.41",
    "199.19.94.24",
    "199.21.149.101",
    "199.21.149.141",
    "199.21.149.94",
    "199.21.149.90",
    "199.21.149.61",
    "184.75.220.26",
    "184.75.220.186",
    "184.75.220.178",
    "184.75.220.170",
    "184.75.215.26",
    "184.75.209.250",
    "184.75.220.122",
    "184.75.220.34",
    "184.75.220.42",
    "184.75.215.34",
    "184.75.220.50",
    "184.75.221.138",
    "184.75.210.138",
    "184.75.221.146",
    "184.75.221.154",
    "184.75.208.74",
    "162.219.179.138",
    "162.219.179.146",
    "162.219.179.154",
    "162.219.178.10",
    "162.219.178.34",
    "162.219.178.18",
    "162.219.178.26",
    "184.75.215.58",
    "184.75.215.178",
    "162.219.178.146",
    "162.253.128.18",
    "162.253.128.26",
    "162.253.128.34",
    "162.253.128.42",
    "184.75.209.90",
    "162.219.178.218",
    "184.75.220.114",
    "184.75.220.138",
    "184.75.220.226",
    "184.75.220.82",
    "184.75.220.106",
    "184.75.220.146",
    "184.75.220.154",
    "184.75.220.202",
    "184.75.220.210",
    "173.44.37.114",
    "173.44.37.90",
    "173.44.37.98",
    "173.44.37.82",
    "173.44.37.106",
    "96.44.144.114",
    "96.44.144.122",
    "96.44.147.42",
    "96.44.147.106",
    "96.44.148.66",
    "96.44.189.114",
    "173.254.222.178",
    "173.254.222.170",
    "173.254.222.162",
    "173.254.222.154",
    "173.254.222.146",
    "46.246.124.91",
    "46.246.124.42",
    "46.246.124.92",
    "46.246.124.20",
    "46.246.124.4",
    "46.246.124.44",

]


def generate_proxy():
    port = random.choice(PROXY_PORTS)
    ip = random.choice(PROXY_IPS)
    proxy = "socks5://{username}:{password}@{ip}:{port}".format(
        username=PROXY_USERNAME,
        password=PROXY_PASSWORD,
        ip=ip,
        port=port,
    )

    return dict(http=proxy, https=proxy)

def generate_selenium_proxy():
    port = random.choice(PROXY_PORTS)
    ip = random.choice(PROXY_IPS)
    proxy = "{}:{}".format(ip, port)

    service_args = [
        "--proxy={}".format(proxy),
        "--proxy-type=socks5",
        "--proxy-auth={}:{}".format(PROXY_USERNAME, PROXY_PASSWORD),
    ]
    return service_args

def generate_request_header():
    header = BASE_REQUEST_HEADER
    header["User-Agent"] = random.choice(USER_AGENT_HEADER_LIST)
    return header
