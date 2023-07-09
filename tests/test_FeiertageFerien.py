# coding: UTF-8

import unittest
import logging
from datetime import datetime


################################
# get the code
with open('framework_helper.py', 'r') as f1, open('../src/14401_FeiertageFerien (14401).py', 'r') as f2:
    framework_code = f1.read()
    debug_code = f2.read()

exec (framework_code + debug_code)

################################################################################


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        print("\n###setUp")

        self.tst = FeiertageFerien_14401_14401(0)
        self.tst.on_init()
        self.tst.debug_input_value[self.tst.PIN_I_COUNTRY_ISO_CODE] = "DE"
        self.tst.debug_input_value[self.tst.PIN_I_SUBDIVISION_CODE] = "DE-BY"
        self.tst.logger.setLevel(logging.DEBUG)

    def test_check_status(self):
        print("### call")
        print("# 1")
        rep = self.tst.check_date("2023-07-03")
        self.assertFalse(rep)

        print("# 2")
        rep = self.tst.check_date("2023-08-15")
        self.assertTrue(rep)

        print("# 3")
        rep = self.tst.check_date("2023-11-02")
        self.assertTrue(rep)

    def test_get_holidays(self):
        print("# test_get_holidays")
        self.tst.on_init()
        self.assertEqual({}, self.tst.holidays)
        self.tst.get_holidays()
        print(self.tst.holidays)
        self.assertGreater(self.tst.holidays, 0)
        logging.debug(self.tst.holidays)

    def test_date_365(self):
        res = self.tst.get_356d("2112-03-15")
        self.assertEqual("2113-03-15", res)
        res = self.tst.get_356d("2020-02-29")
        self.assertEqual("2021-02-28", res)
        res = False
        try:
            res = self.tst.get_356d("2020-13-32")
        except ValueError:
            res = True
        self.assertTrue(res)

    def test_system_test_midnight(self):
        self.tst.on_init()
        self.assertFalse(self.tst.PIN_O_IS_HOLIDAY in self.tst.debug_output_value)
        self.tst.on_input_value(self.tst.PIN_I_MIDNIGHT, 0)
        self.assertFalse(self.tst.PIN_O_IS_HOLIDAY in self.tst.debug_output_value)
        self.tst.on_input_value(self.tst.PIN_I_MIDNIGHT, 1)
        self.assertTrue(self.tst.PIN_O_IS_HOLIDAY in self.tst.debug_output_value)

    def test_system_test_get_holidays(self):
        self.tst.on_init()
        self.assertTrue(len(self.tst.holidays) == 0)
        self.tst.on_input_value(self.tst.PIN_I_GET_HOLIDAYS, 0)
        self.assertTrue(len(self.tst.holidays) == 0)
        self.tst.on_input_value(self.tst.PIN_I_GET_HOLIDAYS, 1)
        self.assertTrue(len(self.tst.holidays) > 0)

    def test_get_date(self):
        now = datetime.now()
        time_now = now.strftime("%Y-%m-%d")
        self.assertEqual(time_now, self.tst.get_date())

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
