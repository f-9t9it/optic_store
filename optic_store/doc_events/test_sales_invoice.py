# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from toolz import merge

from optic_store.tests import (
    make_sales_invoices,
    make_users,
    make_companies,
    make_customers,
    make_items,
    make_serials,
    remove_test_doc,
)

_si_args = {
    "doctype": "Sales Invoice",
    "customer": frappe.db.exists("Customer", {"customer_name": "Ned Flanders"}),
    "company": "Optix",
    "set_posting_time": 1,
    "posting_date": "2019-02-26",
    "due_date": "2019-02-28",
}


class TestGiftCardSale(unittest.TestCase):
    def setUp(self):
        make_users()
        make_companies()
        make_customers()
        make_items()
        serial_no = make_serials()[0]
        self.item_code = serial_no.item_code
        self.serial_no = serial_no.serial_no
        self.old_user = frappe.session.user
        self.old_expiry_date = frappe.db.get_value(
            "Gift Card", self.serial_no, "expiry_date"
        )
        frappe.set_user("simpson@optix.com")

    def tearDown(self):
        frappe.set_user(self.old_user)
        frappe.db.set_value(
            "Gift Card", self.serial_no, "expiry_date", self.old_expiry_date
        )
        remove_test_doc("Sales Invoice", {"owner": "simpson@optix.com"})

    def test_sets_gift_card_expiry(self):
        si = frappe.get_doc(
            merge(
                _si_args,
                {
                    "items": [
                        {
                            "item_code": self.item_code,
                            "qty": 1,
                            "rate": 100,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                            "cost_center": "Main - O",
                            "enable_deferred_revenue": 1,
                            "serial_no": self.serial_no,
                        }
                    ]
                },
            )
        )
        si.insert()
        si.submit()
        expiry_date = frappe.db.get_value("Gift Card", self.serial_no, "expiry_date")
        self.assertEqual(str(expiry_date), "2019-03-28")

    def test_clears_service_dates_for_gift_card_items(self):
        si = frappe.get_doc(
            merge(
                _si_args,
                {
                    "items": [
                        {
                            "item_code": self.item_code,
                            "qty": 1,
                            "rate": 100,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                            "cost_center": "Main - O",
                            "enable_deferred_revenue": 1,
                            "serial_no": self.serial_no,
                        }
                    ]
                },
            )
        )
        si.insert()
        si.submit()
        self.assertIsNone(si.items[0].service_start_date)
        self.assertIsNone(si.items[0].service_end_date)


class TestPaymentByGiftCard(unittest.TestCase):
    def setUp(self):
        make_users()
        make_companies()
        make_customers()
        self.item_code = make_items()[0].name
        self.gift_card_no = make_serials()[0].name
        make_sales_invoices()
        self.old_user = frappe.session.user
        self.old_balance = frappe.db.get_value(
            "Gift Card", self.gift_card_no, "balance"
        )
        frappe.set_user("simpson@optix.com")

    def tearDown(self):
        frappe.set_user(self.old_user)
        frappe.db.set_value("Gift Card", self.gift_card_no, "balance", self.old_balance)
        remove_test_doc("Sales Invoice", {"owner": "simpson@optix.com"})

    def test_validates_gift_card_balance_against_mop_amount(self):
        si = frappe.get_doc(
            merge(
                _si_args,
                {
                    "is_pos": 1,
                    "items": [
                        {
                            "item_code": self.item_code,
                            "qty": 1,
                            "rate": 101,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                            "cost_center": "Main - O",
                        }
                    ],
                    "os_gift_cards": [{"gift_card": self.gift_card_no, "balance": 100}],
                    "payments": [{"mode_of_payment": "Gift Card", "amount": 101}],
                },
            )
        )
        with self.assertRaises(frappe.ValidationError) as cm:
            si.insert()
        self.assertTrue("insufficient balance" in cm.exception.message)

    def test_validates_gift_card_expiry_date(self):
        si = frappe.get_doc(
            merge(
                _si_args,
                {
                    "posting_date": "2019-04-26",
                    "due_date": "2019-04-28",
                    "is_pos": 1,
                    "items": [
                        {
                            "item_code": self.item_code,
                            "qty": 1,
                            "rate": 100,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                            "cost_center": "Main - O",
                        }
                    ],
                    "os_gift_cards": [{"gift_card": self.gift_card_no, "balance": 100}],
                    "payments": [{"mode_of_payment": "Gift Card", "amount": 100}],
                },
            )
        )
        with self.assertRaises(frappe.ValidationError) as cm:
            si.insert()
        self.assertTrue("expired" in cm.exception.message)

    def test_payment_with_gift_card_reduces_balance(self):
        si = frappe.get_doc(
            merge(
                _si_args,
                {
                    "is_pos": 1,
                    "items": [
                        {
                            "item_code": self.item_code,
                            "qty": 1,
                            "rate": 10,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                            "cost_center": "Main - O",
                        }
                    ],
                    "os_gift_cards": [{"gift_card": self.gift_card_no, "balance": 100}],
                    "payments": [{"mode_of_payment": "Gift Card", "amount": 10}],
                },
            )
        )
        si.insert()
        si.submit()
        balance = frappe.db.get_value("Gift Card", self.gift_card_no, "balance")
        self.assertEqual(balance, 90)

    def test_resets_gift_card_balance_on_cancel(self):
        si = frappe.get_doc(
            merge(
                _si_args,
                {
                    "is_pos": 1,
                    "items": [
                        {
                            "item_code": self.item_code,
                            "qty": 1,
                            "rate": 10,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                            "cost_center": "Main - O",
                        }
                    ],
                    "os_gift_cards": [{"gift_card": self.gift_card_no, "balance": 100}],
                    "payments": [{"mode_of_payment": "Gift Card", "amount": 10}],
                },
            )
        )
        si.insert()
        si.submit()
        frappe.set_user("Administrator")
        si.cancel()
        balance = frappe.db.get_value("Gift Card", self.gift_card_no, "balance")
        self.assertEqual(balance, 100)
