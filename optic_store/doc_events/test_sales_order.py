# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from toolz import merge

from optic_store.tests import (
    make_users,
    make_companies,
    make_customers,
    make_prescriptions,
    make_items,
    remove_test_doc,
)

_so_args = {
    "doctype": "Sales Order",
    "customer": frappe.db.exists("Customer", {"customer_name": "Ned Flanders"}),
    "company": "Optix",
    "transaction_date": "2019-02-26",
    "delivery_date": "2019-02-28",
    "items": [
        {
            "item_code": frappe.db.exists("Item", {"item_name": "Green Lens"}),
            "qty": 1,
            "rate": 100,
            "conversion_factor": 1,
            "warehouse": "Stores - O",
        }
    ],
}


class TestSalesOrder(unittest.TestCase):
    def setUp(self):
        make_users()
        make_companies()
        make_customers()
        self.orx_name = make_prescriptions()[0].name
        make_items()
        self.old_user = frappe.session.user
        frappe.set_user("simpson@optix.com")

    def tearDown(self):
        frappe.set_user(self.old_user)
        remove_test_doc("Sales Order", {"owner": "simpson@optix.com"})

    def test_validation_to_limit_items_to_5(self):
        so = frappe.get_doc(
            merge(
                _so_args,
                {
                    "items": [
                        {
                            "item_code": frappe.db.exists(
                                "Item", {"item_name": "Green Lens"}
                            ),
                            "qty": 1,
                            "rate": 100,
                            "conversion_factor": 1,
                            "warehouse": "Stores - O",
                        }
                        for x in range(0, 6)
                    ]
                },
            )
        )
        with self.assertRaises(frappe.ValidationError) as cm:
            so.insert()
        self.assertTrue("cannot be greater than 5" in cm.exception.message)

    def test_validation_to_limit_qty_to_1_for_first_3(self):
        so = frappe.get_doc(
            merge(
                _so_args,
                {
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
                    ]
                },
            )
        )
        with self.assertRaises(frappe.ValidationError) as cm:
            so.insert()
        self.assertTrue("cannot exceed 1" in cm.exception.message)

    def test_validation_for_Prescription_when_order_type_is_Sales(self):
        so = frappe.get_doc(merge(_so_args, {"os_order_type": "Sales"}))
        with self.assertRaises(frappe.ValidationError) as cm:
            so.insert()
        self.assertTrue("Prescription is required" in cm.exception.message)

    def test_validation_for_Prescription_when_order_type_is_Repair(self):
        so = frappe.get_doc(
            merge(_so_args, {"os_order_type": "Repair", "orx_name": self.orx_name})
        )
        with self.assertRaises(frappe.ValidationError) as cm:
            so.insert()
        self.assertTrue("Prescription is not allowed" in cm.exception.message)

    def test_validation_for_Prescription_when_order_type_is_Eye_Test(self):
        so = frappe.get_doc(merge(_so_args, {"os_order_type": "Eye Test"}))
        with self.assertRaises(frappe.ValidationError) as cm:
            so.insert()
        self.assertTrue("Prescription is required" in cm.exception.message)

    def test_validation_for_service_Item_when_order_type_is_Eye_Test(self):
        so = frappe.get_doc(
            merge(
                _so_args,
                {
                    "os_order_type": "Eye Test",
                    "orx_name": self.orx_name,
                    "items": [
                        {
                            "item_code": frappe.db.exists(
                                "Item", {"item_name": "Green Lens"}
                            ),
                            "qty": 1,
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
        self.assertTrue("required to be a Service Item" in cm.exception.message)
