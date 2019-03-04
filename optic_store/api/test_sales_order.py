# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

from optic_store.api.sales_order import invoice_qol
from optic_store.tests import make_sales_orders, remove_test_doc


class TestSalesOrder(unittest.TestCase):
    def setUp(self):
        self.sales_orders = make_sales_orders()
        self.test_so_name = self.sales_orders[0].name
        self.test_doc_args = (
            "Sales Invoice",
            {"company": "Optix", "customer": self.sales_orders[0].customer},
        )

    def tearDown(self):
        remove_test_doc(*self.test_doc_args)

    def test_invoice_qol_creates_an_invoice(self):
        invoice_qol(self.test_so_name)
        self.assertIsNotNone(frappe.db.exists(*self.test_doc_args))

    def test_invoice_qol_submits_invoice(self):
        invoice_qol(self.test_so_name)
        docstatus = frappe.db.get_value(
            "Sales Invoice", frappe.db.exists(*self.test_doc_args), "docstatus"
        )
        self.assertEqual(docstatus, 1)

    def test_invoice_qol_sets_payment(self):
        invoice_qol(self.test_so_name, mode_of_payment="Cash", amount=100.0)
        si_name = frappe.db.exists(*self.test_doc_args)
        payments = frappe.db.sql(
            """
                SELECT mode_of_payment, amount
                FROM `tabSales Invoice Payment` WHERE parent=%(parent)s
            """,
            values={"parent": si_name},
            as_dict=1,
        )
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].mode_of_payment, "Cash")
        self.assertEqual(payments[0].amount, 100.0)
