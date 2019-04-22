# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt


def before_naming(doc, method):
    """
        item_group_abbr: used in Item naming_series
        forced_name: temporary field to handle manual_item_code
    """
    doc.item_group_abbr = (
        frappe.db.get_value("Item Group", doc.item_group, "item_group_abbr") or "XX"
    )
    if doc.manual_item_code:
        doc.forced_name = doc.item_code


def autoname(doc, method):
    if doc.get("forced_name"):
        doc.name = doc.forced_name
        doc.item_code = doc.forced_name


def validate(doc, method):
    if doc.is_gift_card and not doc.gift_card_value:
        frappe.throw(_("Gift Card value is required."))
    if doc.is_gift_card and doc.no_of_months:
        frappe.throw(_("No of Months for Deferred Revenue needs to be zero."))


def after_insert(doc, method):
    def add_price(price_list, price):
        if flt(price) and frappe.db.exists(
            "Price List", {"price_list_name": price_list}
        ):
            frappe.get_doc(
                {
                    "doctype": "Item Price",
                    "price_list": price_list,
                    "item_code": doc.item_code,
                    "currency": frappe.defaults.get_global_default("currency"),
                    "price_list_rate": price,
                }
            ).insert()

    field_pl_map = {
        "Minimum Selling": doc.os_minimum_selling_rate,
        "Minimum Selling 2": doc.os_minimum_selling_2_rate,
        "Wholesale": doc.os_wholesale_rate,
        "Standard Buying": doc.os_cost_price,
    }
    map(lambda x: add_price(*x), field_pl_map.items())


def before_save(doc, method):
    if doc.is_gift_card:
        doc.has_serial_no = 1
        doc.enable_deferred_revenue = 1
        doc.no_of_months = 0
        if not doc.deferred_revenue_account:
            doc.deferred_revenue_account = frappe.db.get_single_value(
                "Optical Store Settings", "gift_card_deferred_revenue"
            )
    if not doc.os_has_commission:
        doc.os_commissions = []
