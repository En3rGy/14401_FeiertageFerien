# coding: UTF-8

import urllib
import urllib2
import ssl
from datetime import datetime
import json
import logging


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class FeiertageFerien_14401_14401(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "14401_FeiertageFerien")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE, ())
        self.PIN_I_COUNTRY_ISO_CODE = 1
        self.PIN_I_SUBDIVISION_CODE = 2
        self.PIN_I_MIDNIGHT = 3
        self.PIN_O_FREI = 1

        ########################################################################################################
        #### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
        ###################################################################################################!!!##

        self.g_out_sbc = {}
        self.holidays = []
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)

    def set_output_value_sbc(self, pin, val):
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print ("# SBC: pin " + str(pin) + " <- data not send / " + str(val).decode("utf-8"))
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val

    # todo
    #  - call next year starting from today with self.check_status,
    #  - check if today is holiday wit self.is_date_in_range,
    #  - remove obsolete entries from self.holidays

    def is_date_in_range(self, start_date, end_date, test_date=None):
        """
        Check if test_date is in the range defined by start_date and end_date

        :param test_date: str, date to test in format 'YYYY-MM-DD'
        :param start_date: str, start date in format 'YYYY-MM-DD'
        :param end_date: str, end date in format 'YYYY-MM-DD'
        :return: bool, True if test_date is in range, False otherwise
        """
        if test_date is None:
            test_date = self.get_date()

        # Define date format
        date_format = "%Y-%m-%d"

        # Convert string dates to datetime objects
        try:
            test_date = datetime.strptime(test_date, date_format)
            start_date = datetime.strptime(start_date, date_format)
            end_date = datetime.strptime(end_date, date_format)
        except ValueError:
            assert "Error: Incorrect date format, should be YYYY-MM-DD"
            return False

        # Check if test_date is in range
        return start_date <= test_date <= end_date

    def get_date(self):
        now = datetime.now()
        time_now = now.strftime("%Y-%m-%d")
        return time_now

    def check_status(self, start_date=None, end_date=None):
        endpoints = ["PublicHolidays",
                     "SchoolHolidays"]

        if start_date is None:
            start_date = self.get_date()
        if end_date is None:
            end_date = start_date

        for endpoint in endpoints:
            res, json_result = self.get_https_response(endpoint,
                                                       self._get_input_value(self.PIN_I_COUNTRY_ISO_CODE),
                                                       self._get_input_value(self.PIN_I_SUBDIVISION_CODE),
                                                       start_date, end_date)

            for holiday in json_result:
                self.holidays[holiday["id"]] = {"startDate": holiday["startDate"], "endDate": holiday["endDate"]}

            if res:
                return True

        return False

    def get_https_response(self, endpoint, country_iso_code, subdivision_code, start_date, end_date=None):
        # Build a SSL Context to disable certificate verification.
        if end_date is None:
            end_date = start_date

        ctx = ssl._create_unverified_context()

        headers = {"accept": "text/json"}
        parameters = {"countryIsoCode": country_iso_code,
                      "validFrom": start_date,
                      "validTo": end_date,
                      "subdivisionCode": subdivision_code}

        encoded_parameters = urllib.urlencode(parameters)
        url = "https://openholidaysapi.org/{}".format(endpoint) + "?" + encoded_parameters

        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request, timeout=3, context=ctx)

        result = response.read()
        ret_code = response.getcode()
        json_result = json.loads(result)
        self.logger.debug("{}: {}".format(endpoint, result))

        if ret_code == 200:
            if len(result) > 0:
                return True, json_result
        else:
            assert "Connecting to {} returns http code {}".format(url, ret_code)

        return False

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.logger.setLevel(logging.INFO)

    def on_input_value(self, index, value):
        if index == self.PIN_I_MIDNIGHT and value:
            try:
                is_holiday = self.check_status()
                self.set_output_value_sbc(self.PIN_O_FREI, is_holiday)
                self.DEBUG.add_message("OK")
            except Exception as e:
                self.DEBUG.add_exception(e)
