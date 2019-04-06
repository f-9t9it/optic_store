# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose


def on_cancel(doc, method):
    if doc.voucher_type == "Write Off Entry":
        reset_balances = compose(
            partial(
                map,
                lambda x: frappe.db.set_value(
                    "Gift Card",
                    x.reference_name,
                    "balance",
                    x.debit_in_account_currency,
                ),
            ),
            partial(filter, lambda x: x.reference_type == "Gift Card"),
        )
        reset_balances(doc.accounts)
