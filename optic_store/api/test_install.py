# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

from optic_store.api.install import setup_defaults
from optic_store.tests import make_employees


class TestInstall(unittest.TestCase):
    def setUp(self):
        make_employees()
        self.old_user = frappe.session.user
        frappe.set_user("simpson@optix.com")

    def tearDown(self):
        frappe.set_user(self.old_user)

    def test_setup_defaults_raises_when_not_system_manager(self):
        with self.assertRaises(frappe.PermissionError):
            setup_defaults()
