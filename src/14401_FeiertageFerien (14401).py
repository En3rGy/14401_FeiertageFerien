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
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_COUNTRY_ISO_CODE=1
        self.PIN_I_SUBDIVISION_CODE=2
        self.PIN_I_MIDNIGHT=3
        self.PIN_I_GET_HOLIDAYS=4
        self.PIN_O_IS_HOLIDAY=1

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

        self.g_out_sbc = {}
        self.holidays = {}
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)

    DATE_FORMAT = "%Y-%m-%d"

    def set_output_value_sbc(self, pin, val):
        self.logger.debug("set_output_value_sbc({}, {})".format(pin, val))
        if pin in self.g_out_sbc:
            if self.g_out_sbc[pin] == val:
                print ("# SBC: pin " + str(pin) + " <- data not send / " + str(val).decode("utf-8"))
                return

        self._set_output_value(pin, val)
        self.g_out_sbc[pin] = val

    def get_356d(self, start_date_str=None):
        self.logger.debug("get_356d({})".format(start_date_str))
        if start_date_str is None:
            start_date = datetime.now()
        else:
            start_date = datetime.strptime(start_date_str, self.DATE_FORMAT)

        try:
            end_date = start_date.replace(year=start_date.year + 1)
        except ValueError:
            end_date = start_date.replace(day=start_date.day - 1, year=start_date.year + 1)

        return end_date.strftime(self.DATE_FORMAT)

    def is_date_in_range(self, start_date, end_date, test_date=None):
        """
        Check if test_date is in the range defined by start_date and end_date

        :param test_date: str, date to test in format 'YYYY-MM-DD'
        :param start_date: str, start date in format 'YYYY-MM-DD'
        :param end_date: str, end date in format 'YYYY-MM-DD'
        :return: bool, True if test_date is in range, False otherwise
        """
        self.logger.debug("is_date_in_range({}, {}, {})".format(start_date, end_date, test_date))
        if test_date is None:
            test_date = self.get_date()

        # Convert string dates to datetime objects
        try:
            test_date = datetime.strptime(test_date, self.DATE_FORMAT)
            start_date = datetime.strptime(start_date, self.DATE_FORMAT)
            end_date = datetime.strptime(end_date, self.DATE_FORMAT)
        except ValueError:
            assert "Error: Incorrect date format, should be YYYY-MM-DD"
            return False

        # Check if test_date is in range
        return start_date <= test_date <= end_date

    def get_date(self):
        self.logger.debug("get_date()")
        now = datetime.now()
        time_now = now.strftime(self.DATE_FORMAT)
        return time_now

    def remove_outdated_holidays(self):
        self.logger.debug("remove_outdated_holidays()")
        today = self.get_date()
        for holiday in self.holidays:
            if holiday["endDate"] < today:
                self.holidays.remove(holiday["id"])

    def get_holidays(self, start_date=None, end_date=None):
        self.logger.debug("get_holidays({}, {})".format(start_date, end_date))
        endpoints = ["PublicHolidays",
                     "SchoolHolidays"]

        self.remove_outdated_holidays()

        if start_date is None:
            start_date = self.get_date()
        if end_date is None:
            end_date = self.get_356d()

        for endpoint in endpoints:
            json_result = self.get_https_response(endpoint,
                                                  self._get_input_value(self.PIN_I_COUNTRY_ISO_CODE),
                                                  self._get_input_value(self.PIN_I_SUBDIVISION_CODE),
                                                  start_date, end_date)

            for holiday in json_result:
                self.holidays[holiday["id"]] = {"startDate": holiday["startDate"], "endDate": holiday["endDate"]}

        self.DEBUG.set_value("Last date holidays received", self.get_date())
        self.DEBUG.set_value("Holiday entries in storage", len(self.holidays))

    def check_date(self, test_date):
        self.logger.debug("check_date({})".format(test_date))
        if len(self.holidays) == 0:
            self.get_holidays(test_date, self.get_356d(test_date))

        for holiday in self.holidays:
            res = self.is_date_in_range(holiday["startDate"], holiday["endDate"], test_date)
            if res:
                return True

        return False

    def get_https_response(self, endpoint, country_iso_code, subdivision_code, start_date, end_date=None):
        self.logger.debug("get_https_response({}, {}, {}, {}, {})".format(endpoint,
                                                                          country_iso_code,
                                                                          subdivision_code,
                                                                          start_date,
                                                                          end_date))
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
            self.DEBUG.add_message("OK")
            if len(result) > 0:
                return json_result
        else:
            assert "Connecting to {} returns http code {}".format(url, ret_code)

        return []

    def on_init(self):
        self.logger.setLevel(logging.INFO)
        self.logger.debug("on_init()")
        self.DEBUG = self.FRAMEWORK.create_debug_section()

    def on_input_value(self, index, value):
        self.logger.debug("on_input_value({}, {})".format(index, value))
        if index == self.PIN_I_MIDNIGHT and value:
            try:
                is_holiday = self.check_date(self.get_date())
                self.set_output_value_sbc(self.PIN_O_IS_HOLIDAY, is_holiday)
            except Exception as e:
                self.DEBUG.add_exception(e)

        elif index == self.PIN_I_GET_HOLIDAYS and value:
            try:
                start_date = self.get_date()
                end_date = self.get_356d()
                self.get_holidays(start_date, end_date)
            except Exception as e:
                self.DEBUG.add_exception(e)
