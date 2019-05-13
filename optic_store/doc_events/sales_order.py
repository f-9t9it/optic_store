# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from optic_store.api.customer import get_user_branch


def before_naming(doc, method):
    naming_series = (
        frappe.db.get_value("Branch", doc.os_branch, "os_sales_order_naming_series")
        if doc.os_branch
        else None
    )
    if naming_series:
        doc.naming_series = naming_series


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


def before_insert(doc, method):
    if not doc.os_branch:
        doc.os_branch = get_user_branch()


def on_update(doc, method):
    settings = frappe.get_single("Optical Store Settings")
    doc.db_set({"os_item_type": _get_item_type(doc.items, settings)})


def _get_item_type(items, settings):
    groups = map(lambda x: x.item_group, items)
    if settings.special_order_item_group in groups:
        return "Special"
    if settings.standard_item_group in groups:
        return "Standard"
    return "Other"
