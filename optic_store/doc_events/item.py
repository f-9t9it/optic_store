# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def before_naming(doc, method):
    """
        item_group_abbr: used in Item naming_series
        forced_name: temporary field to handle manual_item_code
    """
    doc.item_group_abbr = (
        frappe.db.get_value("Item Group", doc.item_group, "item_group_abbr") or "XX"
    )
    if doc.manual_item_code:
        doc.forced_name = doc.item_code


def autoname(doc, method):
    if doc.get("forced_name"):
        doc.name = doc.forced_name
        doc.item_code = doc.forced_name
