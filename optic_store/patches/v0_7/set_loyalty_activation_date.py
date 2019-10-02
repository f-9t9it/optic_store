# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from functools import partial
from toolz import get, compose


def execute():
    if not frappe.db.exists(
        "Custom Field", {"dt": "Customer", "fieldname": "os_loyalty_activation_date"}
    ):
        frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "Customer",
                "fieldname": "os_loyalty_activation_date",
                "fieldtype": "Date",
                "insert_after": "os_loyalty_col",
                "label": "Loyalty Activation Date",
                "read_only": 1,
            }
        ).insert(ignore_permissions=True)

    got_activated = compose(
        partial(filter, lambda x: x[0] == "loyalty_program" and not x[1] and x[2]),
        partial(get, "changed"),
        json.loads,
    )

    for version in frappe.get_all(
        "Version",
        fields=["docname", "creation", "data"],
        filters={"ref_doctype": "Customer"},
        order_by="creation",
    ):
        if got_activated(version.get("data")) and not frappe.db.get_value(
            "Customer", version.get("docname"), "os_loyalty_activation_date"
        ):
            frappe.db.set_value(
                "Customer",
                version.get("docname"),
                "os_loyalty_activation_date",
                version.get("creation"),
            )
