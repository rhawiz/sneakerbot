import re
from time import sleep

import click
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


def selenium_request(driver, path, params, method):
    """
    To overcome seleniums inability to send post requests. We inject contents of form.js into the html with the
        required data and call the submit method on that form.
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


def footpatrol(config):
    if not isinstance(config, Config):
        return

    print "Buying product {} from footpatrol.co.uk".format(config.code)

    # Initialise driver
    options = webdriver.ChromeOptions()

    # Option to disable loading of images
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(
        chrome_options=options)  # service_args=["--verbose", "--log-path=chromedriverxx.log"]

    # Create product payload and send add to basket request
    basket_payload = {
        "attributes[2]": config.size_code,
        "product_quantity": 1,
        "submit": '',
        "product_id": config.code,
        "show_image_variations": 0,
        "product_thumbnails_pagination": 10,
    }

    selenium_request(driver, "http://www.footpatrol.co.uk/basket", basket_payload, "POST")

    checkout_payload = {
        "shipping_country": "82",
        "invoice_postcode": config.postcode,
        "invoice_title": "Mr",
        "invoice_firstname": config.first_name,
        "invoice_lastname": config.last_name,
        "invoice_address_1": config.address,
        "invoice_address_2": "",
        "invoice_town": config.city,
        "invoice_country": "82",
        "invoice_phonenumber": config.phone,
        "invoice_email_address": config.email,
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

    selenium_request(driver, "https://www.footpatrol.co.uk/checkout", checkout_payload, "POST")

    # Retrieve session ID for secure checkout
    hps_session_id = re.findall(r"HPS_SessionID=[a-zA-Z0-9\-]+", driver.page_source)
    if hps_session_id:
        hps_session_id = hps_session_id[0][len("HPS_SessionID="):]

    # Create payment payload
    payment_payload = {
        "card_number": config.card_no,
        "exp_month": config.expire_month_full,
        "exp_year": config.expire_year_full,
        "cv2_number": config.cvv,
        "issue_number": "",
        "HPS_SessionID": hps_session_id,
        "action": "confirm",
        "continue": "Place Order & Pay",
    }

    selenium_request(driver, "https://hps.datacash.com/hps/?", payment_payload, "POST")

    sleep(1000)


def adidas(config):
    if not isinstance(config, Config):
        return

    print "Buying product {} from adidas.co.uk\n".format(config.code)

    print "Retrieving captcha code...\n"

    captcha_value = None
    while not captcha_value:
        captcha_value = get_adidas_captcha_token()

    # captcha_value = get_token()
    print "Building cart payload...\n"

    # Create product payload and send add to basket request
    basket_payload = {
        "layer": "Add To Bag overlay",
        "pid": "{}_{}".format(config.code, config.size_code),
        "Quantity": 1,
        "g-recaptcha-response": captcha_value,
        "masterPid": config.code,
        'responseformat': 'json',
        "sessionSelectedStoreID": "null",
        "ajax": "true",
    }

    print basket_payload

    # Initialise driver
    options = webdriver.ChromeOptions()
    options.add_argument("--app=https://www.adidas.co.uk")
    # options.add_argument("--no-startup-window")
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(chrome_options=options)
    sleep(3)
    cookie1 = {"name": "yisqiiriqnrk", "value": "true"}
    driver.add_cookie(cookie1)

    print "Attempting to cart product...\n"
    selenium_request(driver,
                     "http://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/Cart-MiniAddProduct",
                     basket_payload, "POST")

    print "Sending shipping information...\n"
    selenium_request(driver, "https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/CODelivery-Start",
                     {}, "POST")

    # Adidas are annoying and implement security features during checkout so this is essential
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Get value for shipping security key
    shipping_securekey = soup.find(name="input", attrs={"name": "dwfrm_shipping_securekey"})

    if not shipping_securekey:
        print "Unable to purchase product, are you sure available in size {}?".format(config.size)
        return

    print "Successfully added product to cart...\n"

    print "Building payment payload...\n"
    shipping_securekey = shipping_securekey["value"]
    # Find the name for shipping sub option and option as it changes for every session
    shipping_suboption_name = re.findall(
        "dwfrm_shipping_shiptoaddress_shippingDetails_selectedShippingOption_[a-zA-Z0-9]+", driver.page_source)
    shipping_option_name = re.findall(
        "dwfrm_shipping_shiptoaddress_shippingDetails_selectedShippingSubOption_[a-zA-Z0-9]+", driver.page_source)

    # Get value for shipping security key
    shipping_suboptionkey = soup.find(name="input", attrs={"name": shipping_suboption_name})["value"]
    shipping_optionkey = soup.find(name="input", attrs={"name": shipping_option_name})["value"]

    delivery_payload = {
        "dwfrm_shipping_securekey": shipping_securekey,
        "dwfrm_shipping_selectedDeliveryMethodID_d0vkzoldnkra": "shiptoaddress",
        "dwfrm_shipping_selectedShippingType_d0vefxdisfla": "shiptoaddress",
        "dwfrm_shipping_shiptoaddress_shippingAddress_firstName_d0cqrwjglnio": config.first_name,
        "dwfrm_shipping_shiptoaddress_shippingAddress_lastName_d0wmbolqcybn": config.last_name,
        "dwfrm_shipping_shiptoaddress_shippingAddress_address1_d0fvuadkdsbr": config.address,
        "dwfrm_shipping_shiptoaddress_shippingAddress_address2_d0lmezudsurn": "",
        "dwfrm_shipping_shiptoaddress_shippingAddress_city_d0kgjqgmrwrj": config.city,
        "dwfrm_shipping_shiptoaddress_shippingAddress_postalCode_d0syclozgntz": config.postcode,
        "dwfrm_shipping_shiptoaddress_shippingAddress_country_d0ibrhrplunh": "GB",
        "dwfrm_shipping_shiptoaddress_shippingAddress_phone_d0bhxueslamh": config.phone,
        "dwfrm_shipping_email_emailAddress_d0exhqmxddcm": config.email,
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

    selenium_request(driver,
                     "https://www.adidas.co.uk/on/demandware.store/Sites-adidas-GB-Site/en_GB/COShipping-Submit",
                     delivery_payload, "POST")

    # Wait for the form element to load before continuing
    WebDriverWait(driver, 60).until(expected_conditions.presence_of_element_located((By.ID,
                                                                                     "dwfrm_adyenencrypted_number")))

    # Input payment method as a user would (i.e. by entering each field manually) due to adidas using adyen encryption
    driver.find_element_by_id("dwfrm_adyenencrypted_number").send_keys(config.card_no)
    driver.find_element_by_id("dwfrm_adyenencrypted_cvc").send_keys(config.cvv)
    driver.execute_script(
        "document.querySelectorAll('span[data-val=\"{}\"]')[0].click()".format(config.expire_month_full))
    driver.execute_script(
        "document.querySelectorAll('span[data-val=\"{}\"]')[0].click()".format(config.expire_year_full))

    print "Attempting to make purchase...\n"

    driver.execute_script(
        "document.getElementsByClassName('co-btn_primary btn_showcart button-full-width button-ctn button-brd adi-gradient-blue button-forward')[0].click()")

    payment_success = BeautifulSoup(driver.page_source, "html.parser").find(name="div", attrs={
        "class": "alert-box ab-warning"}) == None

    if payment_success:
        print "Payment success\n"
    else:
        print "Payment failed\n"

    print "Ending."

    if not config.keep_window_open:
        driver.close()


def worker(config):
    print "Starting worker thread..."
    if config.store == 'footpatrol':
        footpatrol(config)
    elif config.store == 'adidas':
        adidas(config)


@click.command()
@click.option('--config', default="s7,s7.5,s8,s8.5,s9,s9.5,s10,s10.5,s11", prompt='Config file path', help='Config file path')
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
