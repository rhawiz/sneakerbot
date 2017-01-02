import ConfigParser, os

import re

from injections import INJECTIONS

ADIDAS_SIZE_MAPPING = {
    "3.5": "530",
    "4": "540",
    "4.5": "550",
    "5": "560",
    "5.5": "570",
    "6": "580",
    "6.5": "590",
    "7": "600",
    "7.5": "610",
    "8": "620",
    "8.5": "630",
    "9": "640",
    "9.5": "650",
    "10": "660",
    "10.5": "670",
    "11": "680",
    "11.5": "690",
    "12": "700",
    "12.5": "710",
    "13": "720",
    "13.5": "730",
}

FOOTPATROL_SIZE_MAPPING = {
    "3": "289",
    "3.5": "290",
    "4": "175",
    "4.5": "262",
    "5": "176",
    "5.5": "198",
    "6": "187",
    "6.5": "201",
    "7": "174",
    "7.5": "199",
    "8": "181",
    "8.5": "197",
    "9": "188",
    "9.5": "183",
    "10": "184",
    "10.5": "185",
    "11": "180",
    "11.5": "210",
    "12": "189",
    "12.5": "191",
    "13": "208",
    "14": "291",
}

CONFIG_TYPE_MAPPING = {
    'store': str,
    'size': float,
    'code': str,
    'quantity': int,
    'first_name': str,
    'last_name': str,
    'address': str,
    'city': str,
    'postcode': str,
    'email': str,
    'card_no': str,
    'name': str,
    'expiry': str,
    'cvv': str,
    'debug': bool,
    'phone': str,
}


class Config(object):
    def __init__(self, config_file):
        self.load_config(config_file)

    def load_config(self, config_file):
        config = ConfigParser.ConfigParser()
        config.readfp(open(config_file))

        self._validate(config)

        self.store = config.get("products", "store")
        self.injection_info = INJECTIONS.get(self.store, None)

        if not self.injection_info:
            raise ValueError("Store '{}' not currently supported.".format(self.store))

        self.injections = self.injection_info.get("injection")

        self.url = None
        if config.has_option("products", "url"):
            self.url = config.get("products", "url")

        self.code = self.url
        if config.has_option("products", "code"):
            self.code = config.get("products", "code")

        self.size = config.get("products", "size")

        if self.store == 'adidas':
            self.size_code = ADIDAS_SIZE_MAPPING.get(self.size, None)
        elif self.store == 'footpatrol':
            self.size_code = FOOTPATROL_SIZE_MAPPING.get(self.size, None)
        elif self.store == 'solebox':
            self.size_code = self.size
        if not self.size_code:
            raise ValueError("Not a valid size '{}'.".format(self.size))

        self.quantity = config.get("products", "quantity")

        self.first_name = config.get("delivery", "first_name")
        self.last_name = config.get("delivery", "last_name")
        self.address = config.get("delivery", "address")
        self.city = config.get("delivery", "city")
        self.postcode = config.get("delivery", "postcode")
        self.email = config.get("delivery", "email")
        self.phone = config.get("delivery", "phone")

        self.card_no = config.get("payment", "card_no")
        self.card_name = config.get("payment", "name")
        self.expiry = config.get("payment", "expiry")
        expiry_parts = self.expiry.split("/")
        if len(expiry_parts) != 2:
            raise ValueError("Invalid expiry date format. Expected mm/yy")
        self.expire_month_full = expiry_parts[0]
        self.expire_month = int(self.expire_month_full)
        self.expire_year = expiry_parts[1]
        self.expire_year_full = "20{}".format(self.expire_year)
        self.username = ''
        self.password = ''
        if self.store == 'solebox':
            assert config.has_option("login",
                                     "username"), "Missing 'username' parameter in login section in config for store ''.".format(
                self.store)
            assert config.has_option("login",
                                     "password"), "Missing 'password' parameter in login section in config for store ''.".format(
                self.store)

            self.username = config.get("login", "username")
            self.password = config.get("login", "password")

        self.cvv = config.get("payment", "cvv")

        # Check if driver has been defined, default to chrome
        self.driver = "chrome"
        self.debug = False
        self.bypass_stock_check = False
        if config.has_section("settings"):
            if config.has_option("settings", "driver"):
                if config.get("settings", "driver") in ("chrome", "phantomjs", "firefox"):
                    self.driver = config.get("settings", "driver")

            if config.has_option("settings", "debug"):
                self.debug = config.get("settings", "debug")

                self.debug = True if self.debug == 'True' else False

            if config.has_option("settings", "bypass_stock_check"):
                self.bypass_stock_check = config.get("settings", "bypass_stock_check")

                self.bypass_stock_check = True if self.bypass_stock_check == 'True' else False

        # Create dictionary of parameters to be passed into the injection script
        self.injection_params = {
            "store": self.store,
            "size": self.size,
            "size_code": self.size_code,
            "quantity": self.quantity,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "city": self.city,
            "postcode": self.postcode,
            "email": self.email,
            "card_number": self.card_no,
            "card_name": self.card_name,
            "expiry": self.expiry,
            "expire_month": self.expire_month,
            "expire_month_full": self.expire_month_full,
            "expire_year": self.expire_year,
            "expire_year_full": self.expire_year_full,
            "cvv": self.cvv,
            "code": self.code,
            "url": self.url,
            "phone": self.phone,
            "username": self.username,
            "password": self.password,
        }

    def _validate(self, config):
        """
        Validate the configuration file and raise exception if invalid.

        """
        assert config.has_section("products"), "Missing 'products' section in config."
        assert config.has_option("products", "store"), "Missing 'store' parameter in products section in config."
        self._check_type(config.get("products", "store"), "store")

        assert config.has_option("products", "size"), "Missing 'store' parameter in products section in config."
        self._check_type(config.get("products", "size"), "size")

        if not config.has_option("products", "url"):
            assert config.has_option("products",
                                     "code"), "Missing 'url' or 'code' parameter in products section in config."

        # assert config.has_option("products", "code"), "Missing 'code' parameter in products section in config."
        # self._check_type(config.get("products", "code"), "code")

        assert config.has_option("products", "quantity"), "Missing 'quantity' parameter in products section in config."
        self._check_type(config.get("products", "quantity"), "quantity")

        assert config.has_section("delivery"), "Missing 'delivery' section in config."
        assert config.has_option("delivery",
                                 "first_name"), "Missing 'first_name' parameter in delivery section in config."
        self._check_type(config.get("delivery", "first_name"), "first_name")

        assert config.has_option("delivery",
                                 "last_name"), "Missing 'last_name' parameter in delivery section in config."
        self._check_type(config.get("delivery", "last_name"), "last_name")

        assert config.has_option("delivery", "address"), "Missing 'address' parameter in delivery section in config."
        self._check_type(config.get("delivery", "address"), "address")

        assert config.has_option("delivery", "city"), "Missing 'city' parameter in delivery section in config."
        self._check_type(config.get("delivery", "city"), "city")

        assert config.has_option("delivery", "postcode"), "Missing 'postcode' parameter in delivery section in config."
        self._check_type(config.get("delivery", "postcode"), "postcode")

        assert config.has_option("delivery", "email"), "Missing 'email' parameter in delivery section in config."
        self._check_type(config.get("delivery", "email"), "email")

        assert config.has_option("delivery", "phone"), "Missing 'phone' parameter in delivery section in config."
        self._check_type(config.get("delivery", "phone"), "phone")

        assert config.has_section("payment"), "Missing 'payment' section in config."

        assert config.has_option("payment", "card_no"), "Missing 'card_no' parameter in payment section in config."
        self._check_type(config.get("payment", "card_no"), "card_no")

        assert config.has_option("payment", "name"), "Missing 'name' parameter in payment section in config."
        self._check_type(config.get("payment", "name"), "name")

        assert config.has_option("payment", "expiry"), "Missing 'expiry' parameter in payment section in config."
        self._check_type(config.get("payment", "expiry"), "expiry")

        assert config.has_option("payment", "cvv"), "Missing 'cvv' parameter in payment section in config."
        self._check_type(config.get("payment", "cvv"), "cvv")

    def _check_type(self, value, param):
        _type = CONFIG_TYPE_MAPPING.get(param)
        try:
            if _type == bool:
                if value in ('True', 'False'):
                    return
                else:
                    raise ValueError(
                        "Invalid type for parameter '{}'."
                        " Inputted value '{}'. Expected type {} and got type {}".format(param, value, _type,
                                                                                        type(value)))
            v = _type(value)
        except ValueError:
            raise ValueError(
                "Invalid type for parameter '{}'."
                " Inputted value '{}'. Expected type {} and got type {}".format(param, value, _type, type(value)))

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity
        self.injection_params["quantity"] = self.quantity
