# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import json
import unittest

from optic_store.api.group_discount import get_item_discounts
from optic_store.tests import (
    make_group_discounts,
    make_items,
    make_brands,
    make_brand_categories,
)


class TestGroupDiscount(unittest.TestCase):
    def setUp(self):
        make_brand_categories()
        make_brands()
        items = make_items()[4:7]
        self.item_codes = map(lambda x: x.name, items)
        group_discounts = make_group_discounts()
        self.group_discounts = map(lambda x: x.name, group_discounts)

    def tearDown(self):
        pass

    def test_returns_proper_values(self):
        item_code_1 = self.item_codes[1]
        item_code_2 = self.item_codes[2]
        actual = get_item_discounts(
            self.group_discounts[1], json.dumps([item_code_1, item_code_2])
        )
        self.assertIn({"item_code": item_code_1, "discount_rate": 5}, actual)
        self.assertIn({"item_code": item_code_2, "discount_rate": 10}, actual)

    def test_returns_zero_for_brand_category_not_in_group_discount(self):
        item_code_1 = self.item_codes[1]
        item_code_2 = self.item_codes[2]
        actual = get_item_discounts(
            self.group_discounts[0], json.dumps([item_code_1, item_code_2])
        )
        self.assertIn({"item_code": item_code_1, "discount_rate": 0}, actual)
        self.assertIn({"item_code": item_code_2, "discount_rate": 25}, actual)

    def test_returns_zero_for_items_with_no_brand(self):
        item_code_0 = self.item_codes[0]
        actual = get_item_discounts(self.group_discounts[1], json.dumps([item_code_0]))
        self.assertEqual(actual, [{"item_code": item_code_0, "discount_rate": 0}])
