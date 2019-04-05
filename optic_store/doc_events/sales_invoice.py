# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
from functools import partial
from toolz import compose

_get_gift_card_amounts = compose(
    sum,
    partial(map, lambda x: x.amount),
    partial(filter, lambda x: x.mode_of_payment == "Gift Card"),
)


def validate(doc, method):
    gift_cards = map(
        lambda x: frappe.get_doc("Gift Card", x.gift_card), doc.os_gift_cards
    )
    map(partial(_validate_gift_card_expiry, doc.posting_date), gift_cards)
    _validate_gift_card_balance(doc.payments, gift_cards)


def _validate_gift_card_expiry(posting_date, giftcard):
    if giftcard.expiry_date and getdate(giftcard.expiry_date) < getdate(posting_date):
        frappe.throw(_("Gift Card {} has expired.".format(giftcard.gift_card_no)))


def _validate_gift_card_balance(payments, gift_cards):
    get_gift_card_balances = compose(sum, partial(map, lambda x: x.balance))
    if _get_gift_card_amounts(payments) > get_gift_card_balances(gift_cards):
        frappe.throw(_("Gift Card(s) has insufficient balance."))


def before_submit(doc, method):
    """
        Service dates are set to None to disable monthly scheduled task
        `erpnext.accounts.deferred_revenue.convert_deferred_revenue_to_income`
    """
    for item in doc.items:
        is_gift_card = frappe.db.get_value("Item", item.item_code, "is_gift_card")
        if is_gift_card:
            item.service_start_date = None
            item.service_end_date = None
            item.service_stop_date = None


def on_submit(doc, method):
    _set_gift_card_validities(doc)
    _set_gift_card_balances(doc)


def _set_gift_card_validities(doc):
    for row in doc.items:
        item = frappe.get_doc("Item", row.item_code)
        if item.is_gift_card and row.serial_no:
            for serial_no in row.serial_no.split("\n"):
                gift_card_no = frappe.db.exists(
                    "Gift Card", {"gift_card_no": serial_no}
                )
                if gift_card_no:
                    frappe.db.set_value(
                        "Gift Card",
                        gift_card_no,
                        "expiry_date",
                        frappe.utils.add_days(
                            doc.posting_date, item.gift_card_validity
                        ),
                    )


def _set_gift_card_balances(doc, cancel=False):
    amount_remaining = _get_gift_card_amounts(doc.payments)
    gift_cards = map(
        lambda x: frappe.get_doc("Gift Card", x.gift_card), doc.os_gift_cards
    )
    for gift_card in gift_cards:
        if amount_remaining < 0:
            break
        amount = min(
            amount_remaining,
            gift_card.balance if not cancel else gift_card.amount - gift_card.balance,
        )
        frappe.db.set_value(
            "Gift Card",
            gift_card.gift_card_no,
            "balance",
            gift_card.balance - amount if not cancel else gift_card.balance + amount,
        )
        amount_remaining -= amount


def on_cancel(doc, method):
    _set_gift_card_balances(doc, cancel=True)
