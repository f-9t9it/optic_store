# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate


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

    gc_account = frappe.db.get_single_value(
        "Optical Store Settings", "gift_card_deferred_revenue"
    )
    company = frappe.db.get_value("Account", gc_account, "company")
    wo_account = frappe.db.get_value(
        "Company", company, "write_off_account"
    ) or frappe.db.exists("Account", {"company": company, "account_name": "Write Off"})
    cost_center = frappe.db.get_value("Company", company, "cost_center")
    je = frappe.get_doc(
        {
            "doctype": "Journal Entry",
            "voucher_type": "Write Off Entry",
            "posting_date": posting_date,
            "company": company,
            "accounts": [
                {
                    "account": gc_account,
                    "debit_in_account_currency": gc.balance,
                    "reference_type": "Gift Card",
                    "reference_name": gift_card_no,
                },
                {
                    "account": wo_account,
                    "cost_center": cost_center,
                    "credit_in_account_currency": gc.balance,
                },
            ],
        }
    )
    je.insert()
    je.submit()
    frappe.db.set_value("Gift Card", gift_card_no, "balance", 0)
