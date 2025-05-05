# -*- coding: utf-8 -*-

import unittest
import datetime
import dately as dtly 

class TestParseRegression(unittest.TestCase):

    def test_literal_date(self):
        result = dtly.parse("2025-01-01")
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result.date(), datetime.date(2025, 1, 1))

    def test_next_week_range(self):
        result = dtly.parse("next week")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(d, datetime.date) for d in result))

    def test_relative_phrase(self):
        result = dtly.parse("first Monday of next month")
        self.assertIsInstance(result, datetime.date)

    def test_quarter_expression(self):
        result = dtly.parse("Q3 of next year")
        self.assertIsInstance(result, tuple)

    def test_fallback_literal(self):
        result = dtly.parse("03/14/2025")
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result.date(), datetime.date(2025, 3, 14))

    def test_unrecognized_input(self):
        result = dtly.parse("completely invalid date phrase")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()

