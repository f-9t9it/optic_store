# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

from optic_store.tests import (
    make_users,
    make_companies,
    make_customers,
    make_items,
    make_serials,
    remove_test_doc,
)

_test_serial_no = "GC0001"

_si_args = {
    "doctype": "Sales Invoice",
    "customer": frappe.db.exists("Customer", {"customer_name": "Ned Flanders"}),
    "company": "Optix",
    "set_posting_time": 1,
    "posting_date": "2019-02-26",
    "due_date": "2019-02-28",
    "items": [
        {
            "item_code": frappe.db.exists("Item", {"item_name": "Gift Card"}),
            "qty": 1,
            "rate": 500,
            "conversion_factor": 1,
            "warehouse": "Stores - O",
            "cost_center": "Main - O",
            "enable_deferred_revenue": 1,
            "serial_no": _test_serial_no,
        }
    ],
}


class TestSalesInvoice(unittest.TestCase):
    def setUp(self):
        make_users()
        make_companies()
        make_customers()
        make_items()
        make_serials()
        self.old_user = frappe.session.user
        self.old_expiry_date = frappe.db.get_value(
            "Gift Card", _test_serial_no, "expiry_date"
        )
        frappe.set_user("simpson@optix.com")

    def tearDown(self):
        frappe.set_user(self.old_user)
        frappe.db.set_value(
            "Gift Card", _test_serial_no, "expiry_date", self.old_expiry_date
        )
        remove_test_doc("Sales Invoice", {"owner": "simpson@optix.com"})

    def test_sets_gift_card_expiry(self):
        si = frappe.get_doc(_si_args)
        si.insert()
        si.submit()
        expiry_date = frappe.db.get_value("Gift Card", _test_serial_no, "expiry_date")
        self.assertEqual(str(expiry_date), "2019-03-28")

    def test_clears_service_dates_for_gift_card_items(self):
        si = frappe.get_doc(_si_args)
        si.insert()
        si.submit()
        self.assertIsNone(si.items[0].service_start_date)
        self.assertIsNone(si.items[0].service_end_date)
