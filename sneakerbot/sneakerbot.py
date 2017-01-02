# -*- coding: utf-8 -*-

import ConfigParser
from time import sleep

import re

import sys
from win32api import GetSystemMetrics

import click
from selenium import webdriver

import ConfigParser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException, WebDriverException

from config import Config
from stockchecker import check_stock


class SneakerBot(object):
    def __init__(self, config):
        self.CONFIG = config

    def _execute_injection(self, driver, calls, values, params):
        res = None
        for i in range(0, len(calls)):
            value = values[i]
            if isinstance(value, str) or isinstance(value, unicode):
                value = value.format(**params)
            call = calls[i]
            if self.CONFIG.debug:
                print "\t\t", call, value
            if call == 'execute_script':
                res = driver.execute_script(value)
            elif call == 'find_element_by_id':
                res = driver.find_element_by_id(value)
            elif call == 'send_keys':
                res.send_keys(value)
            elif call == 'find_element_by_xpath':
                res = driver.find_element_by_xpath(value)
            elif call == 'find_element_by_name':
                res = driver.find_element_by_name(value)
            elif call == 'switch_to.frame':
                driver.switch_to.frame(res)
            elif call == 'get':
                driver.get(value)

    def _initialise_driver(self):
        # Initialise selenium driver
        driver_name = self.CONFIG.driver
        if driver_name == 'chrome':
            self.driver = webdriver.Chrome()
        elif driver_name == 'phantomjs':
            self.driver = webdriver.PhantomJS()
        else:
            self.driver = webdriver.PhantomJS()

    def run(self):
        print "Initialising driver...\n"
        url = None

        if not self.CONFIG.bypass_stock_check:
            print "Finding product information...\n"

            stock_info = check_stock(self.CONFIG.store, self.CONFIG.code, self.CONFIG.size)

            if not stock_info:
                print "Could not find product matching code '{}' for store '{}'. Make sure the product code is correct!".format(
                    self.CONFIG.code, self.CONFIG.store)

            url = stock_info.get("url")
            max_order = int(stock_info.get("max_order"))

            qty_available = int(stock_info.get("qty_available"))
            product_name = stock_info.get("name")
            print "Product information:"
            print "\tURL: {}\n\tName: {}\n\tSize: {}\n\tAvailable Quantity: {}\n\tMaximum Order: {}\n".format(
                url,
                product_name,
                self.CONFIG.size,
                qty_available,
                max_order
            )

            # Ensure stock is available before attempting to inject script. End program if unavailable.
            print "Checking stock levels...\n"
            if qty_available == 0:
                print "Product '{}' in size '{}' is unavailable...\nEnding script...".format(self.CONFIG.code,
                                                                                             self.CONFIG.size)
                return
            max_quantity = qty_available
            if qty_available > max_order:
                max_quantity = max_order
            if int(self.CONFIG.quantity) > int(max_quantity) + 1:
                print "Cannot purchase {} units of {}({}). Setting purchase to max order limit of {}.".format(
                    self.CONFIG.quantity, product_name, self.CONFIG.code, max_quantity)
                self.CONFIG.update_quantity(max_quantity)
            else:
                print "Quantity OK.\n"
        else:
            print "bypass_stock_check set to False. Bypassing stock levels may throw an error if size and quantity not available or if quantity is set to more than the maximum order limit. It's recommended you set this to true\n"
            if not self.CONFIG.url:
                stock_info = check_stock(self.CONFIG.store, self.CONFIG.code, self.CONFIG.size)
                url = stock_info.get("url")

            else:
                url = self.CONFIG.url
        # Get list of javascript injection_info to call
        injections = self.CONFIG.injection_info.get("injection")
        max_attempts = self.CONFIG.injection_info.get("max_attempts")

        sec_between_attempts = self.CONFIG.injection_info.get("wait_between_attempts")

        # Get injection parameters
        params = self.CONFIG.injection_params

        self._initialise_driver()
        if not url:
            url = self.CONFIG.code

        self.driver.get(url)

        print "Starting injection...\n"
        if self.CONFIG.debug == False:
            print "Debug is set to False, not showing injection information."
        for inj_info in injections:

            calls = inj_info.get("selenium_calls")

            values = inj_info.get("values")

            assert len(calls) == len(values)

            sleep_duration = inj_info.get("sleep")

            wait_for = inj_info.get("wait_for", None)

            if wait_for:
                wait_for_call, wait_for_value = wait_for

                wait_for_value = wait_for_value.format(**params)
                print wait_for_call, wait_for_value
                if wait_for_call == 'xpath':
                    WebDriverWait(self.driver, 60).until(
                        expected_conditions.presence_of_element_located((By.XPATH, wait_for_value)))
                elif wait_for_call == 'id':
                    WebDriverWait(self.driver, 60).until(
                        expected_conditions.presence_of_element_located((By.ID, wait_for_value)))
                elif wait_for_call == 'name':
                    WebDriverWait(self.driver, 60).until(
                        expected_conditions.presence_of_element_located((By.NAME, wait_for_value)))
                elif wait_for_call == 'class':
                    WebDriverWait(self.driver, 60).until(
                        expected_conditions.presence_of_element_located((By.CLASS_NAME, wait_for_value)))

            attempt = 0
            while attempt < max_attempts:

                try:
                    attempt += 1
                    if self.CONFIG.debug:
                        print "\tInjecting js...attempt {}".format(attempt)
                    self._execute_injection(self.driver, calls, values, params)
                    break
                except WebDriverException, e:
                    if self.CONFIG.debug:
                        print "\t\t", e
                sleep(sec_between_attempts)

            sleep(sleep_duration)

        sleep(150)


@click.command()
@click.option('--config', default='../sample.cfg', prompt='Config file path', help='Config file path')
def main(config):
    c = Config(config)
    bot = SneakerBot(c)
    bot.run()


if __name__ == '__main__':
    main()
