# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose

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


def before_save(doc, method):
    if doc.orx_type == "Spectacles":
        settings = frappe.get_single("Optical Store Settings")
        frames = map(lambda x: x.item_group, settings.frames)
        lenses = map(lambda x: x.item_group, settings.lens)

        validate_item_group = _validate_item_group(frames, lenses)
        no_of_lenses = 0

        for item in doc.items:
            if item.os_spec_part:
                validate_item_group(item)
                if item.item_group in lenses:
                    no_of_lenses += 1
            else:
                if item.item_group in frames:
                    item.os_spec_part = "Frame"
                elif item.item_group in lenses:
                    if no_of_lenses == 0:
                        item.os_spec_part = "Lens Right"
                    elif no_of_lenses == 1:
                        item.os_spec_part = "Lens Left"
                    no_of_lenses += 1

        _validate_spec_parts(doc.items)


def _validate_item_group(frames, lenses):
    def throw_err(item):
        frappe.throw(
            _("Item in row {} cannot be {}".format(item.idx, item.os_spec_part))
        )

    def fn(item):
        if item.os_spec_part in ["Frame"] and item.item_group not in frames:
            throw_err(item)
        elif (
            item.os_spec_part in ["Lens Right", "Lens Left"]
            and item.item_group not in lenses
        ):
            if item.item_group not in lenses:
                throw_err(item)

    return fn


def _validate_spec_parts(items):
    parts = map(lambda x: x.os_spec_part, items)

    def count(part):
        return compose(len, partial(filter, lambda x: x == part))

    for part in ["Frame", "Lens Right", "Lens Left"]:
        if count(part)(parts) > 1:
            frappe.throw(_("There can only be one row for {}".format(part)))


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


def before_cancel(doc, method):
    if doc.workflow_state != "Cancelled":
        doc.workflow_state = "Cancelled"
