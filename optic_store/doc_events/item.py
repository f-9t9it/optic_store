# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


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
