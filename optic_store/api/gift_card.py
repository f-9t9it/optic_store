# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, today
from functools import partial
from toolz import compose


@frappe.whitelist()
def get_details(gift_card_no, posting_date):
    if not frappe.db.exists("Gift Card", gift_card_no):
        return None
    gc = frappe.get_doc("Gift Card", gift_card_no)
    return {
        "gift_card": gc.gift_card_no,
        "amount": gc.amount,
        "balance": gc.balance,
        "expiry_date": gc.expiry_date,
        "has_expired": getdate(posting_date) > gc.expiry_date
        if gc.expiry_date
        else False,
    }


@frappe.whitelist()
def write_off(gift_card_no, posting_date):
    if "Sales Manager" not in frappe.get_roles():
        raise frappe.PermissionError

    gc = frappe.get_doc("Gift Card", gift_card_no)
    if not gc.balance:
        frappe.throw(
            _(
                "Cannot proceed. Balance for Gift Card: {} is already depleted".format(
                    gift_card_no
                )
            )
        )
    _make_je([gc], posting_date)
    frappe.db.set_value("Gift Card", gift_card_no, "balance", 0)


def _make_je(gift_cards, posting_date):
    gc_account = frappe.db.get_single_value(
        "Optical Store Settings", "gift_card_deferred_revenue"
    )
    company = frappe.db.get_value("Account", gc_account, "company")
    wo_account = frappe.db.get_value(
        "Company", company, "write_off_account"
    ) or frappe.db.exists("Account", {"company": company, "account_name": "Write Off"})
    cost_center = frappe.db.get_value("Company", company, "cost_center")

    def make_journal_entry_account(gc):
        return {
            "account": gc_account,
            "debit_in_account_currency": gc.balance,
            "reference_type": "Gift Card",
            "reference_name": gc.gift_card_no,
        }

    sum_of_balances = compose(sum, partial(map, lambda x: x.balance))

    je = frappe.get_doc(
        {
            "doctype": "Journal Entry",
            "voucher_type": "Write Off Entry",
            "posting_date": posting_date,
            "company": company,
            "accounts": map(make_journal_entry_account, gift_cards)
            + [
                {
                    "account": wo_account,
                    "cost_center": cost_center,
                    "credit_in_account_currency": sum_of_balances(gift_cards),
                }
            ],
        }
    )
    je.insert()
    je.submit()


def write_off_expired_gift_cards():
    posting_date = today()
    gift_cards = map(
        frappe._dict,
        frappe.db.sql(
            """
            SELECT gift_card_no, balance FROM `tabGift Card`
            WHERE IFNULL(balance, 0) > 0 AND expiry_date < %(posting_date)s
        """,
            values={"posting_date": posting_date},
            as_dict=1,
        ),
    )

    sum_of_balances = compose(sum, partial(map, lambda x: x.balance))
    if gift_cards and sum_of_balances(gift_cards):
        _make_je(gift_cards, posting_date)
        map(
            lambda x: frappe.db.set_value("Gift Card", x.gift_card_no, "balance", 0),
            gift_cards,
        )
