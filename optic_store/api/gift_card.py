# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
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
