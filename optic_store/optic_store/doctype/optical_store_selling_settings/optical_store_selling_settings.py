# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class OpticalStoreSellingSettings(Document):
    def on_update(self):
        if self.cashback_expense_account:
            company = frappe.defaults.get_global_default("company")
            cashback_mop = "Cashback"
            account_row = {
                "company": company,
                "default_account": self.cashback_expense_account,
            }
            if not frappe.db.exists("Mode of Payment", cashback_mop):
                frappe.get_doc(
                    {
                        "doctype": "Mode of Payment",
                        "mode_of_payment": cashback_mop,
                        "type": "General",
                        "accounts": [account_row],
                    }
                ).insert()
            if not frappe.db.exists(
                "Mode of Payment Account", {"parent": cashback_mop, "company": company},
            ):
                mop = frappe.get_doc("Mode of Payment", cashback_mop)
                mop.append("accounts", account_row)
                mop.save()
