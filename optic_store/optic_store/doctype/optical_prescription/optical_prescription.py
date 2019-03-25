# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import re
import frappe
from frappe.utils import date_diff, flt
from frappe.model.document import Document


class OpticalPrescription(Document):
    def validate(self):
        if self.expiry_date and date_diff(self.expiry_date, self.test_date) < 0:
            frappe.throw("Expiry Date cannot be before Test Date")

    def before_insert(self):
        self.sph_reading_right = flt(self.sph_right) + flt(self.add_right)
        self.sph_reading_left = flt(self.sph_left) + flt(self.add_left)
        self.pd_total = flt(self.pd_right) + flt(self.pd_left)

    def before_save(self):
        self.cyl_right = scrub("cyl", self.cyl_right)
        self.cyl_left = scrub("cyl", self.cyl_left)
        self.axis_right = scrub("axis", self.axis_right)
        self.axis_left = scrub("axis", self.axis_left)
        self.va_right = scrub("va", self.va_right)
        self.va_left = scrub("va", self.va_left)


def scrub(param, value):
    if value:
        if param == "cyl":
            return round(value * 4) / 4.0
        if param == "axis":
            if value < 0:
                return 0
            return max(value, 180)
        if param == "va":
            return re.sub(r"/[^0-9\/]*/g", "", value)
    return value
