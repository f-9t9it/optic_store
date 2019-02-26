# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from toolz import merge

from optics_9t9it.tests import make_users, make_companies, make_customers, make_items

_so_args = {
    "doctype": "Sales Order",
    "customer": frappe.db.exists("Customer", {"customer_name": "Ned Flanders"}),
    "company": "Optix",
    "transaction_date": "2019-02-26",
    "delivery_date": "2019-02-28",
}


class TestSalesOrder(unittest.TestCase):
    def setUp(self):
        make_users()
        make_companies()
        make_customers()[0]
        make_items()
        self.old_user = frappe.session.user
        frappe.set_user("simpson@optix.com")

    def tearDown(self):
        frappe.set_user(self.old_user)
        name = frappe.db.exists("Sales Order", {"owner": "simpson@optix.com"})
        if name:
            frappe.delete_doc("Customer", name, ignore_permissions=True)

    def test_validation_for_specs_frame(self):
        so = frappe.get_doc(
            merge(
                _so_args,
                {
                    "orx_type": "Spectacles",
                    "items": [
                        {
                            "item_code": frappe.db.exists(
                                "Item", {"item_name": "Green Lens"}
                            ),
                            "qty": 2,
                            "rate": 100,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                        }
                    ],
                },
            )
        )
        with self.assertRaises(frappe.ValidationError) as cm:
            so.insert()
        self.assertTrue("without a Frame" in cm.exception.message)

    def test_validation_for_specs_lens(self):
        so = frappe.get_doc(
            merge(
                _so_args,
                {
                    "orx_type": "Spectacles",
                    "items": [
                        {
                            "item_code": frappe.db.exists(
                                "Item", {"item_name": "Yellow Frame"}
                            ),
                            "qty": 1,
                            "rate": 100,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                        },
                        {
                            "item_code": frappe.db.exists(
                                "Item", {"item_name": "Green Lens"}
                            ),
                            "qty": 1,
                            "rate": 100,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                        },
                    ],
                },
            )
        )
        with self.assertRaises(frappe.ValidationError) as cm:
            so.insert()
        self.assertTrue("without Lenses" in cm.exception.message)
