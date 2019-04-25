# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt


def validate(doc, method):
    if doc.mode_of_payment == "Gift Card":
        if not doc.os_gift_card:
            frappe.throw(_("Gift Card is mandatory for this Mode of Payment"))
        balance = frappe.db.get_value("Gift Card", doc.os_gift_card, "balance")
        if flt(doc.paid_amount) > balance:
            frappe.throw(_("Paid Amount cannot be greater that Gift Card balance"))


def on_submit(doc, method):
    if doc.mode_of_payment == "Gift Card":
        _set_gift_card_balance(doc.os_gift_card, doc.paid_amount)


def on_cancel(doc, method):
    if doc.mode_of_payment == "Gift Card":
        _set_gift_card_balance(doc.os_gift_card, doc.paid_amount, cancel=True)


def _set_gift_card_balance(gift_card, amount, cancel=False):
    balance = frappe.db.get_value("Gift Card", gift_card, "balance")
    frappe.db.set_value(
        "Gift Card",
        gift_card,
        "balance",
        balance - flt(amount) if not cancel else balance + flt(amount),
    )
