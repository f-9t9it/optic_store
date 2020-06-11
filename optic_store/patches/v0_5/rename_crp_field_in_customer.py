# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
    old_field = "os_crp_no"
    new_field = "os_cpr_no"
    if not frappe.db.exists("Custom Field", "Customer-{}".format(old_field)):
        return

    if not frappe.db.exists("Custom Field", "Customer-{}".format(new_field)):
        frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "Customer",
                "label": "CPR No",
                "fieldname": new_field,
                "fieldtype": "Data",
                "insert_after": "os_short_name",
            }
        ).insert()
    frappe.reload_doc("Selling", "doctype", "Customer")
    rename_field("Customer", old_field, new_field)
    frappe.delete_doc("Custom Field", "Customer-{}".format(old_field))
