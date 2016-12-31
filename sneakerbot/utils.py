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


class Format:
    RESET = '\033[0m'
    BOLD = '\033[01m'
    DISABLE = '\033[02m'
    UNDERLINE = '\033[04m'
    REVERSE = '\033[07m'
    INVISIBLE = '\033[08m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    ORANGE = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    LIGHT_GREY = '\033[37m'
    DARK_GREY = '\033[90m'
    LIGHT_RED = '\033[91m'
    LIGHT_GREEN = '\033[92m'
    YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    PINK = '\033[95m'
    LIGHT_CYAN = '\033[96m'


def _format(string, format):
    format_code = format
    if format.find('\033') == -1:
        format_code = getattr(Format, format, '')
    return '{0}{1}{2}'.format(format_code, string, Format.RESET)


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

BASE_REQUEST_HEADER = {
    'ACCEPT_LANGUAGE': 'en-GB,en;q=0.8,en-US;q=0.6'
}

HTTP_PROXIES = [
    '88.159.152.98:80',
    '88.159.152.98:80',
    '83.128.190.244:80',
    '80.57.110.15:80',
    '92.109.93.49:80',
    '84.195.104.126:80',
    '213.136.79.122:80',
    '78.23.240.168:80',
    '91.183.124.41:80',
    '81.30.69.3:80',
    '77.174.184.148:80',
    '62.181.8.120:80',
    '80.112.143.63:80',
    '82.204.105.220:80',
    '46.231.117.154:80',
    '93.72.105.188:8090',
    '86.14.249.58:80',
    '188.214.23.47:80',
    '188.214.23.104:80',
    '188.214.23.59:80',
    '82.165.151.230:80',
    '94.23.158.49:80',
    '95.215.52.150:8080',
    '188.214.23.115:80',
    '85.114.54.87:80',
    '37.187.60.61:80',
    '92.222.237.9:8888',
    '213.136.79.124:80',
    '37.187.7.213:8118',
    '78.129.146.9:8118',
    '195.40.6.43:8080',
    '85.216.41.254:80',
]

HTTPS_PROXIES = [
    '178.32.87.230:3128',
    '137.135.166.225:8146',
    '46.162.195.42:3128',
    '94.100.63.2:8080',
    '62.23.106.13:80',
    '188.213.170.107:80',
    '80.96.203.117:9999',
    '51.255.161.222:80',
    '217.130.250.107:80',
    '185.50.215.116:8080',
    '195.3.113.170:8080',
    '195.3.113.170:3128',
    '31.173.74.73:8080',
    '149.202.249.227:3128',
    '89.249.207.65:3128',
    '51.254.103.206:3128',
    '37.187.253.39:8172',
    '128.199.129.179:3128',
    '176.31.239.33:8121',

]

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


def generate_proxy_dict():
    proxy_dict = {
        'http': HTTP_PROXIES[random.randint(0, len(HTTP_PROXIES) - 1)],
        'https': HTTPS_PROXIES[random.randint(0, len(HTTPS_PROXIES) - 1)],
    }

    return proxy_dict


def generate_request_header():
    header = BASE_REQUEST_HEADER
    header["User-Agent"] = USER_AGENT_HEADER_LIST[random.randint(0, len(USER_AGENT_HEADER_LIST) - 1)]
    return header
