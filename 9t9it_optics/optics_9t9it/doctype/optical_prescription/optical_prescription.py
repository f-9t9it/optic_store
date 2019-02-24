# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import date_diff
from frappe.model.document import Document


class OpticalPrescription(Document):
    def validate(self):
        if self.expiry_date and date_diff(self.expiry_date, self.test_date) < 0:
            frappe.throw("Expiry Date cannot be before Test Date")
