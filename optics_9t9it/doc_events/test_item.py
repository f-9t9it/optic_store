# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest


class TestItem(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        name = frappe.db.exists("Item", {"item_name": "Test Green Solution"})
        if name:
            frappe.delete_doc("Item", name, ignore_permissions=True)

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
