import os
from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from utils import generate_request_header


def get_adidas_captcha_token():
    """
    Prompt captcha code screen to retrieve captcha token for adidas
    """

    # Preload adidas.co.uk as the recaptcha sitekey is registered to this domain and is required to generate a valid token
    options = webdriver.ChromeOptions()
    options.add_argument("--app=https://adidas.co.uk/on/demandware.store/")
    driver = webdriver.Chrome(chrome_options=options)

   # driver.get("https://www.adidas.co.uk/on/demandware.store/")

    # Get recaptcha injection script and execute it
    captcha_injection = file("templates/adidas_recaptcha.js").read()
    driver.execute_script(captcha_injection)

    # Wait for the recaptcha content to load before we continue
    WebDriverWait(driver, 60).until(
        expected_conditions.presence_of_element_located((By.XPATH, "//iframe[@title='recaptcha widget']")))

    # Switch to the recaptcha iframe
    captcha_widget_iframe = driver.find_element_by_xpath("//iframe[@title='recaptcha widget']")
    driver.switch_to.frame(captcha_widget_iframe)

    # Click the recaptcha tick box
    captcha_element = driver.find_element_by_id("recaptcha-anchor")
    if captcha_element:
        captcha_element.click()

    # Wait until recaptcha is solved before we continue
    while captcha_element.get_attribute("aria-checked") == "false":
        sleep(1)

    driver.switch_to.parent_frame()


    WebDriverWait(driver, 60).until(
        expected_conditions.presence_of_element_located((By.XPATH, "//iframe[@title='recaptcha challenge']")))

    captcha_challenge_iframe = driver.find_element_by_xpath("//iframe[@title='recaptcha challenge']")
    driver.switch_to.frame(captcha_challenge_iframe)

    # Find element that contains the recatcha token and return
    captcha_element = driver.find_element_by_id("recaptcha-token")

    if captcha_element:
        captcha_value = captcha_element.get_attribute("value")
        driver.close()
        return captcha_value
    driver.close()
