# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, cint
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from functools import partial
from toolz import compose, pluck, unique, first

from optic_store.doc_events.sales_order import (
    before_insert as so_before_insert,
    before_save as so_before_save,
)
from optic_store.api.sales_invoice import validate_loyalty


def before_naming(doc, method):
    naming_series = (
        frappe.db.get_value("Branch", doc.os_branch, "os_sales_invoice_naming_series")
        if doc.os_branch
        else None
    )
    if naming_series:
        doc.naming_series = naming_series


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
    if gift_cards:
        _validate_gift_card_balance(doc.payments, gift_cards)
    if cint(doc.redeem_loyalty_points):
        _validate_loyalty_card_no(doc.customer, doc.os_loyalty_card_no)
        validate_loyalty(doc)


def _validate_gift_card_expiry(posting_date, giftcard):
    if giftcard.expiry_date and getdate(giftcard.expiry_date) < getdate(posting_date):
        frappe.throw(_("Gift Card {} has expired.".format(giftcard.gift_card_no)))


def _validate_gift_card_balance(payments, gift_cards):
    get_gift_card_balances = compose(sum, partial(map, lambda x: x.balance))
    if _get_gift_card_amounts(payments) > get_gift_card_balances(gift_cards):
        frappe.throw(_("Gift Card(s) has insufficient balance."))


def _validate_loyalty_card_no(customer, loyalty_card_no):
    if loyalty_card_no != frappe.db.get_value(
        "Customer", customer, "os_loyalty_card_no"
    ):
        frappe.throw(
            _(
                "Loyalty Card No: {} does not belong to this Customer".format(
                    loyalty_card_no
                )
            )
        )


def before_insert(doc, method):
    so_before_insert(doc, method)


def before_save(doc, method):
    so_before_save(doc, method)


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
    if doc.is_return and not doc.os_manual_return_dn and not doc.update_stock:
        _make_return_dn(doc)


def _set_gift_card_validities(doc):
    for row in doc.items:
        is_gift_card = frappe.db.get_value("Item", row.item_code, "is_gift_card")
        if is_gift_card and row.serial_no:
            for serial_no in row.serial_no.split("\n"):
                gift_card_no = frappe.db.exists(
                    "Gift Card", {"gift_card_no": serial_no}
                )
                if gift_card_no:
                    gift_card_validity = frappe.db.get_value(
                        "Item", row.item_code, "gift_card_validity"
                    )
                    frappe.db.set_value(
                        "Gift Card",
                        gift_card_no,
                        "expiry_date",
                        frappe.utils.add_days(doc.posting_date, gift_card_validity),
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


def _make_return_dn(si_doc):
    get_dns = compose(list, unique, partial(pluck, "parent"), frappe.get_all)
    dns = get_dns(
        "Delivery Note Item",
        filters={"against_sales_invoice": si_doc.return_against, "docstatus": 1},
        fields=["parent"],
    )
    if not dns:
        return
    if len(dns) > 1:
        frappe.throw(
            _(
                "Multiple Delivery Notes found for this Sales Invoice. "
                "Please create Sales Return from the Delivery Note manually."
            )
        )
    doc = make_delivery_note(si_doc.name)
    for i, item in enumerate(doc.items):
        item.qty = si_doc.items[i].qty
        item.stock_qty = si_doc.items[i].stock_qty
    doc.is_return = 1
    doc.return_against = first(dns)
    doc.run_method("calculate_taxes_and_totals")
    doc.insert()
    doc.submit()


def on_cancel(doc, method):
    _set_gift_card_balances(doc, cancel=True)
