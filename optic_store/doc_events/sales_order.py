# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck

from optic_store.api.customer import get_user_branch
from optic_store.api.item import get_min_prices
from optic_store.utils.helpers import get_parts
from optic_store.utils import mapf
from optic_store.api.xz_report import get_unclosed


def before_naming(doc, method):
    naming_series = (
        frappe.db.get_value("Branch", doc.os_branch, "os_sales_order_naming_series")
        if doc.os_branch
        else None
    )
    if naming_series:
        doc.naming_series = naming_series


def validate(doc, method):
    validate_opened_xz_report(doc.company)
    _validate_max_item_rows(doc)

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
    validate_rate_against_min_prices(doc)


def validate_opened_xz_report(company, pos_profile=None):
    if not any(
        role in ["Sales Manager", "Accounts Manager"] for role in frappe.get_roles()
    ):
        if not get_unclosed(
            user=frappe.session.user, pos_profile=pos_profile, company=company
        ):
            frappe.throw(
                _(
                    "Open XZ Report not found. "
                    "Please create a draft XZ Report and try again."
                )
            )


def _validate_max_item_rows(doc):
    disable_row_limit = frappe.get_cached_value(
        "Optical Store Selling Settings", None, "disable_row_limit"
    )
    if not disable_row_limit and len(doc.items) > 5:
        frappe.throw(_("Number of items cannot be greater than 5"))


def before_insert(doc, method):
    if not doc.os_branch:
        doc.os_branch = get_user_branch()


def before_save(doc, method):
    settings = frappe.get_single("Optical Store Settings")
    frames = mapf(lambda x: x.item_group, settings.frames)
    lenses = mapf(lambda x: x.item_group, settings.lens)

    validate_item_group = _validate_item_group(frames, lenses)
    frame, lens_right, lens_left = get_parts(doc.items)
    for item in doc.items:
        if item.os_spec_part:
            validate_item_group(item)
        else:
            if not frame and item.item_group in frames:
                item.os_spec_part = "Frame"
                frame = item
            elif not lens_right and item.item_group in lenses:
                item.os_spec_part = "Lens Right"
                lens_right = item
            elif not lens_left and item.item_group in lenses:
                item.os_spec_part = "Lens Left"
                lens_left = item

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
    parts = mapf(lambda x: x.os_spec_part, items)

    def count(part):
        return compose(len, list, partial(filter, lambda x: x == part))

    for part in ["Frame", "Lens Right", "Lens Left"]:
        if count(part)(parts) > 1:
            frappe.throw(_("There can only be one row for {}".format(part)))


def validate_rate_against_min_prices(doc):
    price_lists = ["Minimum Selling", "Minimum Selling 2", "Standard Buying"]
    get_validation_items = compose(
        list,
        partial(pluck, "name"),
        lambda: frappe.get_all(
            "Item",
            filters={
                "os_ignore_min_price_validation": 0,
                "name": ("in", [x.item_code for x in doc.items]),
            },
        ),
    )

    for item in filter(lambda x: x.item_code in get_validation_items(), doc.items):
        min_price = frappe.db.sql(
            """
                SELECT MAX(price_list_rate) FROM `tabItem Price`
                WHERE
                    item_code = %(item_code)s AND
                    price_list IN %(price_lists)s
            """,
            values={"item_code": item.item_code, "price_lists": price_lists},
        )[0][0] or 0
        if item.net_rate < min_price:
            frappe.throw(
                frappe._(
                    "Item rate for row {idx} cannot be less than {min_price}".format(
                        idx=item.idx,
                        min_price=frappe.bold(
                            frappe.utils.fmt_money(min_price, currency=doc.currency)
                        ),
                    )
                )
            )


def before_submit(doc, method):
    for item in doc.items:
        prices = get_min_prices(item.item_code)
        item.os_minimum_selling_rate = prices.get("ms1")
        item.os_minimum_selling_2_rate = prices.get("ms2")


def on_update(doc, method):
    settings = frappe.get_single("Optical Store Settings")
    doc.db_set({"os_item_type": _get_item_type(doc.items, settings)})


def _get_item_type(items, settings):
    groups = mapf(lambda x: x.item_group, items)
    if settings.special_order_item_group in groups:
        return "Special"
    if settings.standard_item_group in groups:
        return "Standard"
    return "Other"


def before_cancel(doc, method):
    if frappe.model.meta.get_workflow_name("Sales Order") != "Optic Store Sales Order":
        return
    if doc.workflow_state != "Cancelled":
        doc.workflow_state = "Cancelled"
