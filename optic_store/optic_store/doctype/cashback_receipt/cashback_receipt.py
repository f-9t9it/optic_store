# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class CashbackReceipt(Document):
    def validate(self):
        if sum([x.amount for x in self.redemptions]) > self.cashback_amount:
            frappe.throw(frappe._("Cannot redeem more than the Cashback Amount."))

    def before_save(self):
        self.balance_amount = self.cashback_amount - sum(
            [x.amount for x in self.redemptions]
        )
