import re
from time import sleep

import click
from multiprocessing import Process
from selenium import webdriver

from config import Config


def selenium_request(driver, path, params, method, debug=False):
    """
    To overcome seleniums inability to send post requests. We inject contents of form.js into the html with the
        required data and call the submit method on that form.
    """

    # Read contents of form.js and inject into document head
    post_js = file("form.js", "rb").read()
    add_form_injection = "var s=document.createElement('script');\n\
                                   s.type = 'text/javascript';\n\
                                   s.innerHTML=\n{}\n;\n\
                                  document.head.appendChild(s)".format(post_js)
    if debug:
        print "Injecting javascript...\n{}".format(add_form_injection)
    driver.execute_script(add_form_injection)

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
    print "Buying from footpatrol.co.uk."
    options1 = webdriver.ChromeOptions()
    options1.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome(chrome_options=options1)  # service_args=["--verbose", "--log-path=C:\\Users\\rawan\\PycharmProjects\\sneakerbot\\bin\\chromedriverxx.log"]
    driver.desired_capabilities = options1.to_capabilities()


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
    hps_session_id = re.findall("HPS_SessionID=[a-zA-Z0-9\-]+", driver.page_source)
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


def worker(config):
    print "Starting worker thread..."
    if config.store == 'footpatrol':
        footpatrol(config)


@click.command()
@click.option('--config', default='../sample.cfg', prompt='Config file path', help='Config file path')
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
