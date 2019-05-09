# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_naming_series():
    return {
        "sales_order": _get_series("Sales Order"),
        "sales_invoice": _get_series("Sales Invoice"),
    }


def _get_series(doctype):
    series_text = frappe.get_meta(doctype).get_field("naming_series").options or ""
    return series_text.split("\n")
