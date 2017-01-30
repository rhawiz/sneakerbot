import abc
import json
import os
import random
import re
from HTMLParser import HTMLParser
from time import sleep

import click
import datetime

import demjson
import requests
from bs4 import BeautifulSoup
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from config import Config
from harvester import get_adidas_captcha_token
from utils import generate_request_header, generate_proxy, USER_AGENT_HEADER_LIST, generate_selenium_proxy


def selenium_request(driver, path, params, method):
    """
    To overcome seleniums inability to send post requests. We inject contents of form.js into the html with the
        required data and call form submit.
    """

    # Read contents of form.js and inject into document head
    post_js = file("templates/request.js", "rb").read()

    driver.execute_script(post_js)

    payload = "{}"
    if params.keys():
        payload = "{"

        for key, value in params.iteritems():
            if not isinstance(value, int) or not isinstance(value, float):
                value = "'{}'".format(value)
            payload += "'{}':{},".format(key, value)

        payload = "{}}}".format(payload[:-1])

    call_request_injection = "HTMLFormElement.prototype.submit.call(post('{}', {}, '{}'))".format(path, payload, method)

    driver.execute_script(call_request_injection)

    return driver


# def send_request(session, url, method, data=None, headers=None, proxy=False):
#     if not isinstance(session, requests.Session):
#         return
#
#     if not headers:
#         headers = generate_request_header()
#
#     proxy_dict = {}
#     if proxy:
#         proxy_dict = generate_proxy_dict()
#
#     if not data:
#         data = {}
#
#     if method == "POST":
#         return session.post(url, data=data, headers=headers, proxies=proxy_dict)
#     elif method == "GET":
#         return session.get(url, data=data, headers=headers, proxies=proxy_dict)


class SneakerbotBase(object):
    __metaclass__ = abc.ABCMeta
    BASKET_ERROR = "Failed to add product to basket: {}."
    SHIPPING_ERROR = "Failed to send shipping details: {}."
    PAYMENT_ERROR = "Failed to make payment: {}."

    OUT_OF_STOCK_ERROR = "Product {} not available in size {}."

    BASKET = False
    SHIPPING = False
    PAYMENT = False

    def __init__(self, config):
        assert isinstance(config, Config)
        self.config = config
        self.session = requests.session()
        self.last_log = []
        self.log = []
        self.responses = []

    def _log(self, output):
        self.last_log.append(output)
        self.log.append(output)

    def _send_request(self, url, method, data=None):

        if method not in ("POST", "GET"):
            return

        headers = generate_request_header()

        proxy_dict = generate_proxy() if self.config.use_proxy else {}

        data = {} if not data else data

        attempts = 0
        while attempts < 10:

            try:
                if method == "POST":
                    res = self.session.post(url, data=data, headers=headers, proxies=proxy_dict)
                    self.responses.append(res)
                elif method == "GET":
                    res = self.session.get(url, data=data, headers=headers, proxies=proxy_dict)
                    self.responses.append(res)
                return res
            except Exception, e:
                if self.config.debug:
                    print e
                attempts += 1

    def get_last_log(self):
        output = self.last_log
        self.last_log = []
        return output

    @abc.abstractmethod
    def basket(self):
        """Add product to basket"""
        return

    @abc.abstractmethod
    def shipping(self):
        """Send shipping details"""
        return

    @abc.abstractmethod
    def payment(self):
        """Make payment"""
        return


class FootpatrolBot(SneakerbotBase):
    def basket(self):
        # Create product payload and send add to basket request
        basket_data = {
            "attributes[2]": self.config.size_code,
            "product_quantity": 1,
            "submit": '',
            "product_id": self.config.code,
            "show_image_variations": 0,
            "product_thumbnails_pagination": 10,
        }

        res = self._send_request("http://www.footpatrol.co.uk/basket", "POST", data=basket_data)
        html = res.content
        html = re.sub("\\s", " ", html)
        js_obj = re.search("var dataObject = .*?</script>", html)
        if not js_obj:
            self._log("Could not find dataObject")
            return False

        js_obj = re.search("\{.*\}", js_obj.group()).group()
        basket_obj = demjson.decode(js_obj)
        basket_items = basket_obj.get("items", None)
        if not basket_items:
            self._log(self.OUT_OF_STOCK_ERROR.format(self.config.code, self.config.size))
            return False

        item = basket_items[0]
        h = HTMLParser()
        self._log("\tAdded {} item \"{} - {}\" in size {} to basket.".format(
            item.get("category"),
            item.get("brand"),
            h.unescape(item.get("description")),
            self.config.size
        ))

        self._log("\tTotal price including shipping: {} {}".format(basket_obj.get("orderTotal"),
                                                                   basket_obj.get("orderCurrency")))
        self.BASKET = True
        return True

    def shipping(self):

        shipping_data = {
            "shipping_country": "82",
            "invoice_postcode": self.config.postcode,
            "invoice_title": "Mr",
            "invoice_firstname": self.config.first_name,
            "invoice_lastname": self.config.last_name,
            "invoice_address_1": self.config.address,
            "invoice_address_2": "",
            "invoice_town": self.config.city,
            "invoice_country": "82",
            "invoice_phonenumber": self.config.phone,
            "invoice_email_address": self.config.email,
            "shiptowhere": "bill",
            "delivery_postcode": "",
            "delivery_firstname": "",
            "delivery_lastname": "",
            "delivery_address_1": "",
            "delivery_address_2": "",
            "delivery_town": "",
            "delivery_country": 82,
            "delivery_option": 46,
            "payment_type": "credit_card",
            "submit_order": "true",
        }

        res = self._send_request("https://www.footpatrol.co.uk/checkout", "POST", data=shipping_data)
        html = res.content

        errors = BeautifulSoup(html, "html.parser").findAll(name="div", attrs={"id": re.compile("invoice_.*?_error")})

        if errors:
            self._log(self.SHIPPING_ERROR.format("Invalid input:"))
            for error in errors:
                self._log("\t{}: {}".format(error["id"], re.sub("\\s+", " ", error.text.strip())))
            return False
        self.SHIPPING = True
        return True

    def payment(self):
        res = self.responses[-1]
        # Retrieve session ID for secure checkout
        hps_session_id = re.findall(r"HPS_SessionID=[a-zA-Z0-9\-]+", res.content)
        if not hps_session_id:
            print "\tFailed to make payment\n\t\tCould not find HPS_SessionID"

        hps_session_id = hps_session_id[0][len("HPS_SessionID="):]

        # Create payment payload
        payment_data = {
            "card_number": self.config.card_no,
            "exp_month": self.config.expire_month_full,
            "exp_year": self.config.expire_year_full,
            "cv2_number": self.config.cvv,
            "issue_number": "",
            "HPS_SessionID": hps_session_id,
            "action": "confirm",
            "continue": "Place Order & Pay",
        }

        # Initialise chrome driver to complete purchase
        options = webdriver.ChromeOptions()
        options.add_argument("--app=https://www.footpatrol.co.uk")
        driver = webdriver.Chrome(chrome_options=options)

        # Wait 1 second before transferring cookies to chrome driver
        sleep(1)
        for key, value in self.session.cookies.get_dict().iteritems():
            cookie = {"name": key, "value": value}
            driver.add_cookie(cookie)

        selenium_request(driver, path="https://hps.datacash.com/hps/?", params=payment_data, method="POST")
        self.PAYMENT = True
        return True


class AdidasBot(SneakerbotBase):
    """
    Not working right now
    """

    def basket(self):
        captcha_value = None
        while not captcha_value:
            captcha_value = get_adidas_captcha_token()

        if not captcha_value:
            self._log("Did not retrieve captcha token")
            return False

        basket_payload = {
            "layer": "Add To Bag overlay",
            "pid": "{}_{}".format(self.config.code, "500"),  # self.config.size_code),
            "Quantity": 1,
            "g-recaptcha-response": captcha_value,
            "masterPid": self.config.code,
            'responseformat': 'json',
            "sessionSelectedStoreID": "null",
            "ajax": "true",
        }

        res = self._send_request(
            "http://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/Cart-MiniAddProduct", "POST",
            data=basket_payload)

        return True

    def shipping(self):
        res = self._send_request(
            "https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/CODelivery-Start", "POST")

        # Adidas are annoying and implement security features during checkout so this is essential
        soup = BeautifulSoup(res.content, "html.parser")

        # Get value for shipping security key
        shipping_securekey = soup.find(name="input", attrs={"name": "dwfrm_shipping_securekey"})

        if not shipping_securekey:
            self._log(self.SHIPPING_ERROR.format("Unable to find shipping_securekey"))
            return False

        shipping_securekey = shipping_securekey["value"]

        shipping_suboption_name = re.findall(
            "dwfrm_shipping_shiptoaddress_shippingDetails_selectedShippingOption_[a-zA-Z0-9]+", res.content)
        shipping_option_name = re.findall(
            "dwfrm_shipping_shiptoaddress_shippingDetails_selectedShippingSubOption_[a-zA-Z0-9]+", res.content)

        # Get value for shipping security key
        shipping_suboptionkey = soup.find(name="input", attrs={"name": shipping_suboption_name})["value"]
        shipping_optionkey = soup.find(name="input", attrs={"name": shipping_option_name})["value"]

        shipping_data = {
            "dwfrm_shipping_securekey": shipping_securekey,
            "dwfrm_shipping_selectedDeliveryMethodID_d0vkzoldnkra": "shiptoaddress",
            "dwfrm_shipping_selectedShippingType_d0vefxdisfla": "shiptoaddress",
            "dwfrm_shipping_shiptoaddress_shippingAddress_firstName_d0cqrwjglnio": self.config.first_name,
            "dwfrm_shipping_shiptoaddress_shippingAddress_lastName_d0wmbolqcybn": self.config.last_name,
            "dwfrm_shipping_shiptoaddress_shippingAddress_address1_d0fvuadkdsbr": self.config.address,
            "dwfrm_shipping_shiptoaddress_shippingAddress_address2_d0lmezudsurn": "",
            "dwfrm_shipping_shiptoaddress_shippingAddress_city_d0kgjqgmrwrj": self.config.city,
            "dwfrm_shipping_shiptoaddress_shippingAddress_postalCode_d0syclozgntz": self.config.postcode,
            "dwfrm_shipping_shiptoaddress_shippingAddress_country_d0ibrhrplunh": "GB",
            "dwfrm_shipping_shiptoaddress_shippingAddress_phone_d0bhxueslamh": self.config.phone,
            "dwfrm_shipping_email_emailAddress_d0exhqmxddcm": self.config.email,
            "dwfrm_shipping_shiptoaddress_shippingAddress_useAsBillingAddress_d0ipzzlmvjui": "true",
            "dwfrm_shipping_shiptoaddress_shippingAddress_ageConfirmation_d0cugoambrxs": "true",
            "dwfrm_shipping_shiptoaddress_shippingDetails_selectedShippingOption_d0suldkeqbmh": shipping_optionkey,
            "dwfrm_shipping_shiptoaddress_shippingDetails_selectedShippingSubOption_d0uahhkhgkqv": shipping_suboptionkey,
            "shippingMethodType_0": "inline",
            "dwfrm_cart_selectShippingMethod": "ShippingMethodID",
            "dwfrm_cart_shippingMethodID_0": "Standard",
            "referer": "Cart-Show",
            "shipping-option-me": "20170017",
            "dwfrm_shipping_submitshiptoaddress": "Review & Pay",
            "dwfrm_shipping_shiptostore_search_country_d0nqqzrhorjw": "GB",
            "dwfrm_shipping_shiptostore_search_maxdistance_d0rljaxwdvlo": "50",
            "dwfrm_shipping_shiptostore_search_latitude_d0aamymocmxs": "",
            "dwfrm_shipping_shiptostore_search_longitude_d0fckfuhovjy": "",
            "dwfrm_shipping_shiptostore_search_country_d0qnchytytnr": "GB",
            "dwfrm_shipping_shiptostore_search_maxdistance_d0nqdmyxtygc": "50",
            "dwfrm_shipping_shiptostore_search_latitude_d0grvnamlvob": "",
            "dwfrm_shipping_shiptostore_search_longitude_d0xffbnczexf": "",
            "dwfrm_shipping_shiptostore_shippingDetails_selectedShippingMethod_d0arysgzgayb": "",
            "dwfrm_shipping_shiptostore_shippingDetails_storeId_d0slbjugurxe": "",
            "dwfrm_shipping_shiptopudo_search_country_d0xkabbrgyqx": "GB",
            "dwfrm_shipping_shiptopudo_search_maxdistance_d0rrywqvzunj": "10",
            "dwfrm_shipping_shiptopudo_search_country_d0goerjreoyc": "GB",
            "dwfrm_shipping_shiptopudo_search_maxdistance_d0daqpwdwjkh": "10",
            "dwfrm_shipping_shiptopudo_shippingDetails_selectedShippingMethod_d0crknozfrst": "",
            "dwfrm_shipping_shiptopudo_shippingDetails_pudoId_d0dntxsyxumh": "",
        }

        res = self._send_request(
            "https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/COShipping-Submit", "POST",
            data=shipping_data)

        if not res.content:
            self._log(self.SHIPPING_ERROR.format("Unknown reason"))
            return False
        return True

    def payment(self):

        key = "10001|AB71F7DC18325B18331FC8184009C971CD1871219B3EFA91FEA12E957201A53240D8F21E262F141DCF25A0FD6F87B37B87E31B251BBB498FF42F305597A3EB3A0E36D0215C6568EB1E28AC0267E51ADAEF22CAC9E55F73A7644027CC02F1FA3350060F7387A9C732E5BD88DBD6530D5C82C46D27027DCDF8C572A05B787B92FF0CFAA1F4B1AC0A88724DBC4E68E9339624A2772395CFE2A08A21BBB75E73DE777FF65FC7DE4E086D8D22D1D5E335BACD4B3F061363BF6F37131B3C6C9FECED0C556651900DA4277694C467DF2A8423074A0C4F4D3CBB8A8A7989526238C2964F9527061057FF244A4C23C1B97D8F1A3FB10EA9FFD763F79112B98C74DB49E9F5";
        now = datetime.datetime.today()

        # Generation time requires the format YYYY-MM-DDTHH:mm:ss.000Z e.g. 2017-01-13T20:47:25.390Z
        generation_time = re.sub(" ", "T", now.__str__())
        generation_time = generation_time[:-3] + "Z"

        options = webdriver.ChromeOptions()
        options.add_argument("--app=file:///{}".format(os.path.abspath("templates/adyen_encrypt.html")))
        options.add_argument("window-size=1,1")
        driver1 = webdriver.Chrome(chrome_options=options)

        driver1.execute_script(
            "adyenEncrypt('{}','{}','{}','{}','{}','{}','{}')".format(
                self.config.card_no, self.config.cvv, self.config.card_name, self.config.expire_month_full,
                self.config.expire_year_full,
                generation_time, key))

        while BeautifulSoup(driver1.page_source, "html.parser").find(name="input", attrs={"id": "fingerprint"})[
            "value"] == "":
            pass

        html = driver1.page_source
        driver1.close()

        soup = BeautifulSoup(html, "html.parser")

        fingerprint = soup.find(name="input", attrs={"id": "fingerprint"})["value"]
        encrypted_data = soup.find(name="div", attrs={"id": "encrypted"})["value"]

        payment_payload = {
            "selectedPaymentMethodID": "CREDIT_CARD",
            "installments": 1,
            "fingerprint": fingerprint,
            "creditCardType": "visa",
            "adyen-encrypted-data": encrypted_data
        }

        options = webdriver.ChromeOptions()
        options.add_argument("--app=https://www.adidas.co.uk")
        driver2 = webdriver.Chrome(chrome_options=options)

        sleep(1)
        for key, value in self.session.cookies.get_dict().iteritems():
            cookie = {"name": key, "value": value}
            driver2.add_cookie(cookie)

        driver2.get("https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/COSummary-Start")

        html = driver2.page_source

        print html

        payment_url = re.search(
            "www\.adidas\.co\.uk\/on\/demandware\.store\/Sites\-adidas\-GB\-Site\/en_GB\/COSummary\-Start\/C[0-9]+",
            html)

        if not payment_url:
            self._log(self.PAYMENT_ERROR.format("Could not find payment url."))
            return False

        payment_url = "https://{}".format(payment_url.group())
        print payment_url

        selenium_request(driver2, payment_url, payment_payload, "POST")

        print driver2.page_source


class OffspringBot(SneakerbotBase):
    def basket(self):
        basket_data = {
            "productCode": "{}{}".format(self.config.code, self.config.size_code)
        }

        res = self._send_request("http://www.offspring.co.uk/view/basket/add", "POST", data=basket_data)

        response = json.loads(res.content)

        if not response.get("cartCode", None):
            self._log(self.OUT_OF_STOCK_ERROR.format(self.config.code, self.config.size))
            return False

        self._log("\tAdded item \"{}\" in size {} to basket.".format(
            response.get("entry").get("product").get("name"),
            self.config.size
        ))

        self._log("\tTotal price including shipping: {} {}".format(response.get("entry").get("totalPrice").get("value"),
                                                                   response.get("entry").get("totalPrice").get(
                                                                       "currencyIso")))

        return True

    def shipping(self):

        res = self._send_request("http://www.offspring.co.uk/view/content/basket", "GET")


        checkout_data = {
            "componentUid": "basketComponent",
            "pageLabel": "basket",
            "checkout": "Checkout"
        }
        res = self._send_request("https://www.offspring.co.uk/view/basket/proceedCheckout", "POST", data=checkout_data)

        print res.content
        sleep(10)

        login_data = {
            "email": "rawandhawiz@gmail.com",
        }
        res = self._send_request(
            "https://www.offspring.co.uk/view/checkout/content/checkoutLogin/submit", "POST",
            data=login_data
        )

        shipping_addr_data = {
            "id": "",
            "selectedAddressType": "uk",
            "title": "Mr",
            "firstname": self.config.first_name,
            "lastname": self.config.last_name,
            "companyname": "",
            "line1": self.config.address,
            "line2": "",
            "town": self.config.city,
            "postcode": self.config.postcode,
            "country": "GB",
        }
        res = self._send_request(
            "https://www.offspring.co.uk/view/component/checkoutDelivery/address/submit", "POST",
            data=shipping_addr_data
        )


        delivery_type_data = {
            "deliveryMode": "standarduk"

        }
        res = self._send_request(
            "https://www.offspring.co.uk/view/component/checkoutDeliveryType/mode/submit", "POST",
            data=delivery_type_data
        )

        billing_details_data = {
            "pageLabel": "checkoutBilling",
            "sameAsDeliveryAddress": "",
            "address.id": "",
            "address.title": "mr",
            "address.firstname": self.config.first_name,
            "address.lastname": self.config.last_name,
            "address.line1": self.config.address,
            "address.line2": "",
            "address.town": self.config.city,
            "address.country": "GB",
            "address.companyname": "",
            "address.postcode": self.config.password,
            "address.phone": self.config.phone,
            "checkoutRegisterForm.password": "",
            "checkoutRegisterForm.confirmPassword": "",
            "paymentMode": "sagepay",
            "_emailOptIn": "off",
            "_newsAlerts": "off"
        }
        res = self._send_request(
            "https://www.offspring.co.uk/view/component/checkoutBilling/submit", "POST",
            data=billing_details_data
        )
        print res.content
        sleep(10)

        return True

    def payment(self):
        pass


class_mapping = {
    "footpatrol": FootpatrolBot,
    "adidas": AdidasBot,
    "offspring": OffspringBot,
}


def worker(config):
    print "\nStarting worker thread..."
    _class = class_mapping.get(config.store, None)
    if not _class:
        print "{} not supported.".format(config.store)
        return False

    bot = _class(config)

    print "\nAdding product to basket..."
    if not bot.basket():
        print "\tFailed to add product to basket..."
        for output in bot.get_last_log():
            print "\t\t", output
        return False

    print "\tSuccessfully added product to basket..."
    for output in bot.get_last_log():
        print "\t", output

    print "\nSending shipping details..."
    if not bot.shipping():
        print "\tFailed to send shipping details..."
        for output in bot.get_last_log():
            print "\t\t", output
        return False
    print "\tSuccessfully sent shipping details..."

    print "\nSending payment details"
    if not bot.payment():
        print "\tFailed to send payment details..."
        for output in bot.get_last_log():
            print "\t\t", output
        return False
    print "\tSuccessfully sent payment details..."


@click.command()
@click.option('--config', default='../sample2.cfg', prompt='Config file path', help='Config file path')
@click.option('--instances', default=1, prompt='Number of instances to run per config file', help='Number of instances')
def main(config, instances):
    config_files = config.split(",")
    for file in config_files:
        file = file.strip()
        for i in range(0, instances):
            c = Config(file)
            p = Process(target=worker, args=(c,))
            p.start()


if __name__ == '__main__':
    main()
