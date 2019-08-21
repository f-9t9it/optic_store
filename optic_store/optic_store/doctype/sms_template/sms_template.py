# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


class SMSTemplate(Document):
    def validate(self):
        meta = frappe.get_meta(self.ref_doctype)
        if meta.istable or meta.issingle:
            frappe.throw(_("Cannot create template for this Doctype"))
