# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

from optic_store.api.gift_card import get_details, write_off
from optic_store.tests import (
    make_sales_invoices,
    make_users,
    make_companies,
    make_customers,
    make_items,
    make_serials,
    remove_test_doc,
)


class TestGiftCardGetDetails(unittest.TestCase):
    def setUp(self):
        make_companies()
        make_customers()
        make_items()
        gift_cards = make_serials()
        self.gift_card_no = gift_cards[0].name
        self.gift_card_unlimited_no = gift_cards[1].name
        make_sales_invoices()

    def tearDown(self):
        pass

    def test_returns_None_when_not_found(self):
        result = get_details("Non Gift Card", "2012-12-12")
        self.assertIsNone(result)

    def test_returns_proper_expired_state(self):
        result = get_details(self.gift_card_no, "2020-12-12")
        self.assertTrue(result.get("has_expired"))
        result = get_details(self.gift_card_no, "2010-12-12")
        self.assertFalse(result.get("has_expired"))

    def test_returns_proper_expired_state_for_unlimited_ones(self):
        result = get_details(self.gift_card_unlimited_no, "2010-12-12")
        self.assertFalse(result.get("has_expired"))


class TestGiftCardWriteOff(unittest.TestCase):
    def setUp(self):
        make_users()
        make_companies()
        make_customers()
        make_items()
        self.gift_card_no = make_serials()[0].name
        make_sales_invoices()
        self.old_user = frappe.session.user
        self.old_balance = frappe.db.get_value(
            "Gift Card", self.gift_card_no, "balance"
        )

    def tearDown(self):
        frappe.set_user(self.old_user)
        frappe.db.set_value("Gift Card", self.gift_card_no, "balance", self.old_balance)
        remove_test_doc(
            "Journal Entry", {"company": "Optix", "posting_date": "2019-03-01"}
        )

    def test_raises_PermissionError_when_not_Sales_Manager(self):
        frappe.set_user("simpson@optix.com")
        with self.assertRaises(frappe.PermissionError):
            write_off(self.gift_card_no, "2019-03-01")

    def test_raises_when_balance_is_zero(self):
        frappe.db.set_value("Gift Card", self.gift_card_no, "balance", 0)
        with self.assertRaises(frappe.ValidationError) as cm:
            write_off(self.gift_card_no, "2019-03-01")
        self.assertTrue("depleted" in cm.exception.message)

    def test_sets_balance_to_zero(self):
        write_off(self.gift_card_no, "2019-03-01")
        balance = frappe.db.get_value("Gift Card", self.gift_card_no, "balance")
        self.assertEqual(balance, 0)

    def test_creates_Journal_Entry(self):
        write_off(self.gift_card_no, "2019-03-01")
        je_name = frappe.db.exists(
            "Journal Entry", {"company": "Optix", "posting_date": "2019-03-01"}
        )
        self.assertIsNotNone(je_name)
        je = frappe.get_doc("Journal Entry", je_name)
        self.assertEqual(je.docstatus, 1)

    def test_sets_proper_values(self):
        write_off(self.gift_card_no, "2019-03-01")
        je_name = frappe.db.exists(
            "Journal Entry", {"company": "Optix", "posting_date": "2019-03-01"}
        )
        je = frappe.get_doc("Journal Entry", je_name)
        self.assertTrue(je.accounts[0].account.startswith("Gift Card"))
        self.assertEqual(je.accounts[0].debit_in_account_currency, self.old_balance)
        self.assertEqual(je.accounts[0].reference_type, "Gift Card")
        self.assertEqual(je.accounts[0].reference_name, self.gift_card_no)

    def test_resets_balances_when_Journal_Entry_is_cancelled(self):
        write_off(self.gift_card_no, "2019-03-01")
        je_name = frappe.db.exists(
            "Journal Entry", {"company": "Optix", "posting_date": "2019-03-01"}
        )
        je = frappe.get_doc("Journal Entry", je_name)
        je.cancel()
        balance = frappe.db.get_value("Gift Card", self.gift_card_no, "balance")
        self.assertEqual(balance, self.old_balance)
