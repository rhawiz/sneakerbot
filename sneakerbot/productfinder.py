import string

import re

import click
import requests
from utils import generate_request_header, print_progress, scrape_tag_contents, is_url
from utils import propercase
from tabulate import tabulate


class ProductFinder(object):
    """
    Find product information
    """

    CONFIGS = {
        "adidas": {

            # URL Format
            # Current search query options, all of which in proper case (e.g. Men, Women):
            #   colour: Trainer colours (e.g. Blue, Green, Purple)
            #   name: Trainer name (e.g. yeezys)
            #   gender: Gender name (e.g. Men, Women)
            "search_url_format": 'http://www.adidas.co.uk/search?q={name}&sz=120&start=0&prefn1=productType&prefn2=searchColor&prefv1=Trainers&prefv2={colours}',
            "options": {
                "colours": ["White", "Black", "Blue", "Grey", "Red", "Green", "Pink", "Purple", "Orange", "Yellow",
                            "Gold", "Silver", "Beige", "Turquoise"],
                "genders": ['Men', 'Women', 'Kids']
            },
            "next_page_tags": [
                ("a", {"class": "paging-arrow pagging-next-page"}),
                ("", "href")
            ],
            "listing_unit_tag": [("div", {"class": "hockeycard originals "})],
            "total_units_tags": [
                ("div", {"class": "rbk-page-heading"}),
                ("regex", "[0-9]+(?:\,[0-9]+)? Products")
            ],
            "listing_info_tags": {
                "name": [
                    ("a", {"class": re.compile(r".*\bproduct-link\b.*")}),
                    ("", ""),

                ],
                "url": [
                    ("a", {"class": re.compile(r".*\bproduct-link\b.*")}),
                    ("", "href"),
                ],
                "code": [
                    ("a", {"class": re.compile(r".*\bproduct-link\b.*")}),
                    ("", "data-track"),

                ],
                "price": [
                    ("div", {"class": "clearfix product-info-price-rating "}),
                    ("span", {"class": "salesprice"}),
                    ("", ""),

                ]
            },
            "detail_info_tags": {
                "name": [
                    ("h1", {"itemprop": "name"}),
                    ("", ""),

                ],
                "url": [
                    ("input", {"name": "pageUrl"}),
                    ("", "value"),
                ],
                "code": [
                    ("segment", {"class": "product-segment MainProductSection"}),
                    ("", "id"),

                ],
                "price": [
                    ("span", {"class": re.compile(r".*\bsale\-price\b.*")}),
                    ("", "data-sale-price"),

                ]
            }
        }
    }

    def find_product_info(self, store, name, colours=None, gender=None):
        if not self.CONFIGS.get(store, None):
            return None

        if not name:
            return None

        url = self._construct_url({
            'name': name,
            'store': store,
            'colours': colours,
            'gender': gender,

        })

        print "Searching for products..."
        content = self.scrape_content(store, url)
        self._print_output(content)

    def scrape_content(self, store, url):

        unit_tag = self.CONFIGS.get(store).get("listing_unit_tag")
        next_page_tags = self.CONFIGS.get(store).get("next_page_tags")
        listing_info_tags = self.CONFIGS.get(store).get("listing_info_tags")
        detail_info_tags = self.CONFIGS.get(store).get("detail_info_tags")
        total_units_tags = self.CONFIGS.get(store).get("total_units_tags")
        html = requests.get(url, headers=generate_request_header()).content
        total_units = scrape_tag_contents(total_units_tags, html)
        total_units = total_units[0] if len(total_units) else '1'

        total_units = re.sub("[\,|\.]+", "", total_units)
        total_units = re.findall("[0-9]+", total_units)
        total_units = total_units[0] if len(total_units) else '1'
        try:
            total_units = int(total_units)
        except ValueError:
            total_units = 1

        content = []
        print 'Gathering product information...'

        info_tags = listing_info_tags
        if total_units == 1:
            info_tags = detail_info_tags
            unit_tag = [("html", "")]

        progress = 0
        while url:

            if progress:
                html = requests.get(url, headers=generate_request_header()).content
            units_html = scrape_tag_contents(unit_tag, html)
            for idx, unit in enumerate(units_html):
                progress += 1
                print_progress(progress, total_units)
                values = {}
                for field, field_tags in info_tags.iteritems():
                    value = self._clean_text(scrape_tag_contents(field_tags, unit))
                    values[field] = value
                content.append(values)
            next_page = scrape_tag_contents(next_page_tags, html)
            url = next_page[0] if len(next_page) and is_url(next_page[0]) else None
        return content

    def _construct_url(self, params):
        store = params.pop('store', None)
        name = params.pop('name', None)
        colours = params.pop('colours', None)
        gender = params.pop('gender', None)
        url_format = self.CONFIGS.get(store).get("search_url_format")

        if store == 'adidas':
            name = re.sub(" ", "%20", name)
            url_params = {
                'store': store,
                'name': name,

            }

            gender = re.sub("both", "", gender)
            gender = None if gender == "" else gender
            if gender:
                gender = string.lower(gender)
                gender = re.sub("male", "men", gender)
                gender = re.sub("boy", "men", gender)
                gender = re.sub("female", "women", gender)
                gender = re.sub("girl", "women", gender)

                gender = propercase(gender)
                gender_options = self.CONFIGS.get(store).get("options").get("genders")
                if gender in gender_options:
                    url_format = re.sub("searchColor", "searchColor&prefn3=gender", url_format)
                    url_format += '&prefv3={gender}'
                    url_params['gender'] = gender

            colour_options = self.CONFIGS.get(store).get("options").get("colours")

            if not colours:
                colours = ''
                for c in colour_options:
                    colours += ",{}".format(c)

            colours = propercase(colours)
            colours = re.sub("[\\s]", "", colours)
            for idx, col in enumerate(colours.split(",")):

                if col not in colour_options:
                    colours = re.sub(col, "", colours)

            colours = re.sub("\,$", "", colours)
            colours = re.sub("\,", "%7C", colours)
            url_params['colours'] = colours

            return url_format.format(**url_params)

    def _print_output(self, content):
        print "Found {} products.".format(len(content))
        if len(content):
            headers = content[0].keys()
            data = []
            for c in content:
                data.append(c.values())

            print tabulate(data, headers=headers)

    def _clean_text(self, text):
        value = text[0] if len(text) else ''
        value = re.sub("\n", " ", value)
        value = re.sub("\\s+", " ", value)
        value = value.strip()
        return value


@click.command()
@click.option('--store', default='adidas', prompt='Store',
              help='Store. e.g. Adidas, nike, puma, etc...')
@click.option('--name', prompt='Product name', help='Name of the product e.g. Yeezys')
@click.option('--colours', default="", prompt='Product colour (e.g. red,green,purple)', help='Product colour')
@click.option('--gender', default="", prompt='Gender (male/female/kids/both)', help='Gender')
def main(store, name, colours, gender):
    finder = ProductFinder()
    finder.find_product_info(store, name, colours, gender)


if __name__ == '__main__':
    main()
