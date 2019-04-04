# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

from optic_store.tests import make_items, remove_test_doc


class TestSerialNo(unittest.TestCase):
    def setUp(self):
        self.test_item_name = make_items()[2].name

    def tearDown(self):
        remove_test_doc("Gift Card", {"gift_card_no": "Test Serial No"})
        remove_test_doc("Serial No", {"serial_no": "Test Serial No"})

    def test_serial_no_creates_gift_card(self):
        frappe.get_doc(
            {
                "doctype": "Serial No",
                "serial_no": "Test Serial No",
                "item_code": self.test_item_name,
            }
        ).insert()
        gift_card = frappe.db.exists("Gift Card", {"gift_card_no": "Test Serial No"})
        self.assertEqual(gift_card, "Test Serial No")

    def test_gift_card_has_correct_value(self):
        frappe.get_doc(
            {
                "doctype": "Serial No",
                "serial_no": "Test Serial No",
                "item_code": self.test_item_name,
            }
        ).insert()
        gift_card_value = frappe.db.get_value(
            "Item", self.test_item_name, "gift_card_value"
        )
        amount = frappe.db.get_value("Gift Card", "Test Serial No", "amount")
        self.assertEqual(gift_card_value, amount)

    def test_gift_card_on_serial_no_delete(self):
        serial_no = frappe.get_doc(
            {
                "doctype": "Serial No",
                "serial_no": "Test Serial No",
                "item_code": self.test_item_name,
            }
        ).insert()
        serial_no.delete()
        gift_card = frappe.db.exists("Gift Card", {"gift_card_no": "Test Serial No"})
        self.assertIsNone(gift_card)
