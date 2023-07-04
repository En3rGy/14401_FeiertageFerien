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
        self.tst.debug_input_value[self.tst.PIN_I_COUNTRY_ISO_CODE] = "DE"
        self.tst.debug_input_value[self.tst.PIN_I_SUBDIVISION_CODE] = "DE-BY"
        self.tst.logger.setLevel(logging.DEBUG)

    def test_check_status(self):
        print("### call")
        print("# 1")
        rep = self.tst.check_status("2023-07-03")
        self.assertFalse(rep)

        print("# 2")
        rep = self.tst.check_status("2023-08-15")
        self.assertTrue(rep)

        print("# 3")
        rep = self.tst.check_status("2023-06-02")
        self.assertTrue(rep)

    def test_system_test(self):
        self.tst.on_init()
        self.assertFalse(self.tst.PIN_O_FREI in self.tst.debug_output_value)
        self.tst.on_input_value(self.tst.PIN_I_MIDNIGHT, 1)
        self.assertTrue(self.tst.PIN_O_FREI in self.tst.debug_output_value)

    def test_get_date(self):
        now = datetime.now()
        time_now = now.strftime("%Y-%m-%d")
        self.assertEqual(time_now, self.tst.get_date())

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
