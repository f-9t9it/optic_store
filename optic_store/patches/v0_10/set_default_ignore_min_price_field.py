# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute():
    for (name,) in frappe.get_all("Item", as_list=1):
        frappe.db.set_value("Item", name, "os_ignore_min_price_validation", 1)
