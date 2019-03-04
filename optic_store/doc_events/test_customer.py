# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

from optic_store.tests import make_employees, remove_test_doc


class TestCustomer(unittest.TestCase):
    def setUp(self):
        make_employees()
        self.old_user = frappe.session.user
        frappe.set_user("simpson@optix.com")

    def tearDown(self):
        remove_test_doc("Customer", {"customer_name": "Test Barney Gumble"})
        frappe.set_user(self.old_user)

    def test_customer_id_contains_branch(self):
        customer = frappe.get_doc(
            {"doctype": "Customer", "customer_name": "Test Barney Gumble"}
        ).insert()
        self.assertTrue("Moe's Tavern" in customer.name)
