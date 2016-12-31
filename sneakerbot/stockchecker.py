import string
import re
import click
import requests
from bs4 import BeautifulSoup

from config import ADIDAS_SIZE_MAPPING, FOOTPATROL_SIZE_MAPPING
from utils import generate_request_header
from tabulate import tabulate


def check_stock(store, code, size):
    if store == "adidas":
        code = string.upper(code)
        url = "http://www.adidas.co.uk/search?q={code}".format(code=code)
        html = requests.get(url, headers=generate_request_header()).content
        soup = BeautifulSoup(html, "lxml")

        # Check if code is valid by looking for No Results message on page
        invalid_code = soup.find(name="div", attrs={"class": "nohitsmessage"})
        if invalid_code:
            return None

        # Check whether we're directed to a listing page or a detail page.
        #   Sometimes adidas search directs to a listing page displaying similar items
        #   to the product the code refers to and at other times it directly links to the
        #   product so this check is essential.
        is_listing = len(soup.findAll(name="div", attrs={"class": "product-tile"})) > 1
        if is_listing:
            # If we are directed to a listing page, find the listing item for the required product.
            attrs = {"class": re.compile(r".*\bproduct-link\b.*"), "data-track": code}
            url = soup.find(name="a", attrs=attrs)

            # If we can't find the product listing, return None.
            if not url or not hasattr(url, "href"):
                return None

            # Set the url
            url = url["href"]

            html = requests.get(url, headers=generate_request_header()).content
            soup = BeautifulSoup(html, "lxml")

        # Scrape data in html
        name = soup.find("h1", {"itemprop": "name"})
        name = name.text.strip() if name else ''

        price = soup.find("span", {"itemprop": "price"})
        price = price["data-sale-price"] if hasattr(price, "data-sale-price") else ''

        qty_element = soup.find(
            name="option",
            attrs={"value": "{}_{}".format(string.upper(code), ADIDAS_SIZE_MAPPING.get(size))}
        )

        qty_availble = 0
        max_order = 0
        # Check if quantity information exists, otherwise probably not available for that size so leave the default as 0
        if qty_element:
            qty_availble = float(qty_element["data-maxavailable"].strip())
            max_order = float(qty_element["data-maxorderqty"].strip())

        data = {
            "qty_available": qty_availble,
            "max_order": max_order,
            "size": size,
            "name": name,
            "price": price,
            "url": url,
            "code": code

        }
        return data

    if store == 'footpatrol':
        url = "http://www.footpatrol.co.uk/s:{code}/?search={code}".format(code=code)
        html = requests.get(url, headers=generate_request_header()).content
        soup = BeautifulSoup(html, "lxml")

        valid_code = soup.find(name='a', attrs={'class': 'fp-product-thumb-link'})
        if not valid_code:
            return
        url = "http://www.footpatrol.co.uk/{}".format(valid_code["href"])

        html = requests.get(url, headers=generate_request_header()).content
        soup = BeautifulSoup(html, "lxml")

        name = soup.find(name='h1', attrs={'class': 'title'}).text
        name = re.sub(r"\n", ' ', name)
        name = re.sub(r"\\s+", ' ', name)
        name = name.strip()

        price = soup.find(name="div", attrs={"class": "product-heading"}).text
        price = re.findall(ur"\xA3[0-9]+", price)
        price = price[-1][1:]

        size_code = FOOTPATROL_SIZE_MAPPING.get(size)
        size_available = True if soup.find(name="a", attrs={"rel": "nofollow",
                                                            "href": '{}'.format(size_code)}) is not None else False
        qty_availble = 0
        max_order = 0
        if size_available:
            qty_availble = 1
            max_order = 1

        data = {
            "qty_available": qty_availble,
            "max_order": max_order,
            "size": size,
            "name": name,
            "price": price,
            "url": url,
            "code": code

        }

        return data

    if store == 'solebox':
        url = code
        html = requests.get(url, headers=generate_request_header()).content
        soup = BeautifulSoup(html, "lxml")

        size_available = soup.find(name="a", attrs={"data-size-uk": size})

        qty_availble = 1 if size_available else 0
        max_order = 1 if size_available else 0

        name = soup.find(name='h1', attrs={"id": "productTitle"})
        if name:
            name = name.text
        else:
            name = ''
        name = re.sub(r"\n", ' ', name)
        name = re.sub(r"\\s+", ' ', name)
        name = name.strip()
        price = soup.find(name='div', attrs={"id": "productPrice"})
        if price:
            try:
                price = price.text()
            except Exception, e:
                price = ''
        else:
            price = ''

        data = {
            "qty_available": qty_availble,
            "max_order": max_order,
            "size": size,
            "name": name,
            "price": price,
            "url": url,
            "code": ""

        }
        return data


def tabulate_data(content):
    print "Found {} products.".format(len(content))
    if len(content):
        headers = content[0].keys()
        data = []
        for c in content:
            data.append(c.values())

        return tabulate(data, headers=headers)


#
# @click.command()
# @click.option('--store', prompt='Product store', help='Product store. e.g. adidas, footpatrol')
# @click.option('--codes', prompt='Product codes (e.g. BB4314,S80682)', help='Product codes')
# @click.option('--sizes', prompt='Size (e.g. 6.5,8,9.0)', help='Trainer sizes')
def main(store="solebox", codes="https://www.solebox.com/en/Footwear/Running/NMD-XR1-PK.html", sizes="6.5"):
    data = []
    for code in codes.split(","):
        for size in sizes.split(","):
            code = code.strip()
            size = size.strip()
            stock_info = check_stock(store, code, size)
            if stock_info:
                data.append(stock_info)

    print tabulate_data(data)


if __name__ == '__main__':
    main()
