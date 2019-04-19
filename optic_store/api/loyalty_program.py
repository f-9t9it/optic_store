# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
    get_loyalty_details,
    get_loyalty_program_details,
)
from toolz import merge

from optic_store.utils import pick


@frappe.whitelist()
def get_customer_loyalty_details(customer, expiry_date, company):
    program = get_loyalty_program_details(
        customer, expiry_date=expiry_date, company=company
    )
    points = get_loyalty_details(
        customer, program.loyalty_program, expiry_date=expiry_date, company=company
    )
    return merge(
        pick(["loyalty_program", "conversion_factor"], program),
        pick(["loyalty_points"], points),
    )
