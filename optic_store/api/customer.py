# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_user_branch():
    employee = frappe.db.exists("Employee", {"user_id": frappe.session.user})
    return frappe.db.get_value("Employee", employee, "branch") if employee else None
