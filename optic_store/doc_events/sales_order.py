# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def validate(doc, method):
    if len(doc.items) > 5:
        frappe.throw(_("Number of items cannot be greater than 5"))
