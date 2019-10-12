# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, unique


def execute():
    if not frappe.db.exists(
        "Custom Field",
        {"dt": "Purchase Invoice", "fieldname": "supplier_delivery_note"},
    ):
        frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "Purchase Invoice",
                "fieldname": "supplier_delivery_note",
                "fieldtype": "Data",
                "insert_after": "release_date",
                "label": "Supplier Delivery Note",
                "allow_on_submit": 1,
                "in_standard_filter": 1,
            }
        ).insert(ignore_permissions=True)

    get_purchase_receipt = compose(
        lambda x: x[0] if len(x) == 1 else None,
        list,
        partial(filter, lambda x: x),
        unique,
        partial(map, lambda x: x.purchase_receipt),
        lambda x: x.items,
        partial(frappe.get_doc, "Purchase Invoice"),
    )

    for name, sdn in frappe.get_all(
        "Purchase Invoice",
        fields=["name", "supplier_delivery_note"],
        filters=[["docstatus", "<", "2"]],
        order_by="creation",
        as_list=1,
    ):
        if not sdn:
            purchase_receipt = get_purchase_receipt(name)
            if purchase_receipt:
                supplier_delivery_note = frappe.db.get_value(
                    "Purchase Receipt", purchase_receipt, "supplier_delivery_note"
                )
                if supplier_delivery_note:
                    frappe.db.set_value(
                        "Purchase Invoice",
                        name,
                        "supplier_delivery_note",
                        supplier_delivery_note,
                    )
