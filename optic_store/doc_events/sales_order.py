# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from optic_store.api.customer import get_user_branch


def validate(doc, method):
    if len(doc.items) > 5:
        frappe.throw(_("Number of items cannot be greater than 5"))
    for i in range(0, 3):
        try:
            if doc.items[i].qty > 1:
                frappe.throw(
                    _("Qty for row {} cannot exceed 1".format(doc.items[i].idx))
                )
        except IndexError:
            break
    if not doc.orx_name and doc.os_order_type in ["Sales", "Eye Test"]:
        frappe.throw(
            _(
                "Prescription is required is for Order Type: {}".format(
                    doc.os_order_type
                )
            )
        )
    if doc.orx_name and doc.os_order_type in ["Repair"]:
        frappe.throw(
            _(
                "Prescription is not allowed for Order Type: {}".format(
                    doc.os_order_type
                )
            )
        )
    if doc.os_order_type == "Eye Test":
        for item in doc.items:
            if item.item_group != "Services":
                frappe.throw(
                    _(
                        "Item: {} is required to be a Service Item".format(
                            item.item_name
                        )
                    )
                )


def on_update(doc, method):
    settings = frappe.get_single("Optical Store Settings")
    process_at_branch = (
        frappe.db.get_value("Branch", doc.os_branch, "process_at_branch")
        if doc.os_branch
        else 0
    )
    doc.db_set(
        {
            "os_is_special_order": 1
            if settings.special_order_item_group
            in map(lambda x: x.item_group, doc.items)
            else 0,
            "os_is_branch_order": process_at_branch,
        }
    )
