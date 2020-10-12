# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute():
    for doctype in ["Sales Order", "Sales Invoice"]:
        if not frappe.db.exists(
            "Custom Field", "{}-{}".format(doctype, "os_sales_person")
        ):
            continue
        if not frappe.db.exists(
            "Custom Field", "{}-{}".format(doctype, "os_sales_person_name")
        ):
            frappe.get_doc(
                {
                    "doctype": "Custom Field",
                    "allow_on_submit": 1,
                    "dt": doctype,
                    "fetch_from": "os_sales_person.employee_name",
                    "fieldname": "os_sales_person_name",
                    "fieldtype": "Data",
                    "insert_after": "os_sales_person",
                    "label": "Sales Person Name",
                    "read_only": 1,
                }
            ).insert()
        for doc in frappe.get_all(
            doctype, fields=["name", "os_sales_person", "os_sales_person_name"]
        ):
            if doc.os_sales_person and not doc.os_sales_person_name:
                frappe.db.set_value(
                    doctype,
                    doc.name,
                    "os_sales_person_name",
                    frappe.db.get_value(
                        "Employee", doc.os_sales_person, "employee_name"
                    ),
                )
