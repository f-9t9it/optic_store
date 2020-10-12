# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute():
    for doctype in ["Sales Order Item", "Sales Invoice Item"]:
        frappe.delete_doc_if_exists(
            "Custom Field", "{}-os_ignore_min_price_validation".format(doctype)
        )
