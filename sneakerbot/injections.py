from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

INJECTIONS = {
    'adidas': {
        "url": "http://www.adidas.co.uk",
        "max_attempts": 10,
        "wait_between_attempts": 0.25,
        "injection": [
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelectorAll('span[data-val={code}_{size_code}]')[0].click()"],
                "sleep": 0,
                # "wait_for": "//div[@class=ffSelectMenuMid]",
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelectorAll('span[data-val=\"{quantity}\"]')[0].click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelectorAll('button[name=add-to-cart-button]')[0].click()"],
                "sleep": 0
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelectorAll('a[data-ci-test-id=CheckOutButton]')[0].click()"],
                "sleep": 0.0,
                # "wait_for": "//a[data-ci-test-id=CheckOutButton)]"
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelectorAll('button[id=dwfrm_cart_checkoutCart]')[0].click()"],
                "sleep": 0,
                # "wait_for": "//button[@id=dwfrm_cart_checkoutCart)]"

            },
            {
                "selenium_calls": ["find_element_by_id", "send_keys"],
                "values": ["dwfrm_shipping_shiptoaddress_shippingAddress_firstName", "{first_name}"],
                "sleep": 0,
                # "wait_for": "//*[@id=dwfrm_shipping_shiptoaddress_shippingAddress_firstName)]"

            },
            {
                "selenium_calls": ["find_element_by_id", "send_keys"],
                "values": ["dwfrm_shipping_shiptoaddress_shippingAddress_lastName", "{last_name}"],
                "sleep": 0
            },
            {
                "selenium_calls": ["find_element_by_id", "send_keys"],
                "values": ["dwfrm_shipping_shiptoaddress_shippingAddress_address1", "{address}"],
                "sleep": 0
            },
            {
                "selenium_calls": ["find_element_by_id", "send_keys"],
                "values": ["dwfrm_shipping_shiptoaddress_shippingAddress_city", "{city}"],
                "sleep": 0
            },
            {
                "selenium_calls": ["find_element_by_id", "send_keys"],
                "values": ["dwfrm_shipping_shiptoaddress_shippingAddress_postalCode", "{postcode}"],
                "sleep": 0
            },
            {
                "selenium_calls": ["find_element_by_id", "send_keys"],
                "values": ["dwfrm_shipping_email_emailAddress", "{email}"],
                "sleep": 0
            },
            {
                "selenium_calls": ["execute_script"],
                "values": [
                    "document.getElementsByClassName('button-primary btn-regular-red co-btn_primary bp-black light-back button-half-width')[0].click()"],
                "sleep": 1,
            },
            {
                "selenium_calls": ["find_element_by_id", "send_keys"],
                "values": ["dwfrm_adyenencrypted_number", "{card_number}"],
                "sleep": 0,
                # "wait_for": "//*[@id=dwfrm_adyenencrypted_number)]"
            },
            {
                "selenium_calls": ["find_element_by_id", "send_keys"],
                "values": ["dwfrm_adyenencrypted_cvc", "{cvv}"],
                "sleep": 0
            },
            {
                "selenium_calls": ["execute_script"],
                "values": [
                    "document.querySelectorAll('span[data-val=\"{expire_month_full}\"]')[0].click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": [
                    "execute_script"
                ],
                "values": [
                    "document.querySelectorAll('span[data-val=\"{expire_year_full}\"]')[0].click()"
                ],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": [
                    "document.getElementsByClassName('co-btn_primary btn_showcart button-full-width button-ctn button-brd adi-gradient-blue button-forward')[0].click()"],
                "sleep": 0,
            },
        ]
    },
    'footpatrol': {
        "url": "http://www.footpatrol.co.uk",
        "max_attempts": 10,
        "wait_between_attempts": 0.25,
        "injection": [
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelectorAll('a[href=\"{size_code}\"]')[0].click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"add-to-basket\").click()"],
                "sleep": 1,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector('input[value=\"Secure Checkout\"]').click()"],
                "sleep": 1,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"invoice_postcode\").value = \"{postcode}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"invoice_firstname\").value = \"{first_name}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"invoice_lastname\").value = \"{last_name}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"invoice_address_1\").value = \"{address}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"invoice_town\").value = \"{city}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"invoice_phonenumber\").value = \"{phone}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"invoice_email_address\").value = \"{email}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"checkout-button\").click()"],
                "sleep": 2,
            },
            {
                "selenium_calls": ["find_element_by_id", 'switch_to.frame'],
                "values": ["datacash_hcc_frame", 'datacash_hcc_frame'],
                "sleep": 0,
            },
            {
                "selenium_calls": ["find_element_by_name", "send_keys"],
                "values": ["card_number", "{card_number}"],
                "sleep": 0
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector('option[value=\"{expire_month_full}\"]').selected = true"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector('option[value=\"{expire_year_full}\"]').selected = true"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector('input[name=\"cv2_number\"]').value = \"{cvv}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById(\"continue\").click()"],
                "sleep": 0,
            }

        ]

    },
    'solebox': {
        "url": "http://www.solebox.com",
        "max_attempts": 10,
        "wait_between_attempts": 0.25,
        "injection": [
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector(\"a[data-size-uk=\'{size}\']\").click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('toBasket').click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('miniBasket').click()"],
                "sleep": 3,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector(\"button[class='submitButton largeButton nextStep']\").click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector(\"input[name='lgn_usr']\").value = \"{username}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector(\"input[name='lgn_pwd']\").value = \"{password}\""],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector(\"button[class='submitButton checkoutLogin']\").click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('userNextStepBottom').click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('payment_gs_kk_saferpay').click()"],
                "sleep": 0,

            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('paymentNextStepBottom').click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector(\"button[class='submitButton nextStep largeButton']\").click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["find_element_by_name", 'switch_to.frame'],
                "values": ["HPiFrame", 'HPiFrame'],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector(\"button[class='btn btn-select btn-card-visa']\").click()"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('CardNumber').value = '{card_number}'"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('ExpMonth').value = '{expire_month}'"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('ExpYear').value = '{expire_year_full}'"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('HolderName').value = '{card_name}'"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.getElementById('VerificationCode').value = '{cvv}'"],
                "sleep": 0,
            },
            {
                "selenium_calls": ["execute_script"],
                "values": ["document.querySelector(\"button[name='SubmitToNext']\").click()"],
                "sleep": 0,
            },

        ]

    }
}