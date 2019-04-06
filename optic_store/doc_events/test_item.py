# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

from optic_store.tests import remove_test_doc


class TestItem(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        remove_test_doc("Item", {"item_name": "Test Green Solution"})

    def test_item_code_contains_group(self):
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_name": "Test Green Solution",
                "item_group": "Solutions",
            }
        ).insert()
        self.assertTrue(item.item_code.startswith("SL"))

    def test_item_code_contains_default_group(self):
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_name": "Test Green Solution",
                "item_group": "Products",
            }
        ).insert()
        self.assertTrue(item.item_code.startswith("XX"))

    def test_item_code_contains_correct_length(self):
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_name": "Test Green Solution",
                "item_group": "Solutions",
            }
        ).insert()
        self.assertEqual(len(item.item_code), 11)

    def test_item_code_can_be_overridden(self):
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": "Overridden",
                "manual_item_code": 1,
                "item_name": "Test Green Solution",
                "item_group": "Solutions",
            }
        ).insert()
        self.assertEqual(item.item_code, "Overridden")

    def test_gift_card_item_requires_value(self):
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_name": "Test Green Solution",
                "item_group": "Products",
                "is_gift_card": 1,
            }
        )
        with self.assertRaises(frappe.ValidationError) as cm:
            item.insert()
        self.assertTrue("value is required" in cm.exception.message)

    def test_gift_card_item_sets_serial_no_and_enable_deferred_revenue(self):
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_name": "Test Green Solution",
                "item_group": "Products",
                "is_gift_card": 1,
                "gift_card_value": 1,
            }
        ).insert()
        self.assertEqual(item.has_serial_no, 1)
        self.assertEqual(item.enable_deferred_revenue, 1)

    def test_gift_card_item_sets_deferred_revenue_account_from_settings(self):
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_name": "Test Green Solution",
                "item_group": "Products",
                "is_gift_card": 1,
                "gift_card_value": 1,
            }
        ).insert()
        deferred_revenue_account = frappe.db.get_single_value(
            "Optical Store Settings", "gift_card_deferred_revenue"
        )
        self.assertEqual(item.deferred_revenue_account, deferred_revenue_account)

    def test_gift_card_item_requires_zero_deferred_no_of_months(self):
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_name": "Test Green Solution",
                "item_group": "Products",
                "is_gift_card": 1,
                "gift_card_value": 1,
                "no_of_months": 1,
            }
        )
        with self.assertRaises(frappe.ValidationError) as cm:
            item.insert()
        self.assertTrue("needs to be zero" in cm.exception.message)
