# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
    get_loyalty_details,
    get_loyalty_program_details,
)
from toolz import merge, first

from optic_store.utils import pick


@frappe.whitelist()
def get_customer_loyalty_details(customer, loyalty_card_no, expiry_date, company):
    if loyalty_card_no != frappe.db.get_value(
        "Customer", customer, "os_loyalty_card_no"
    ):
        frappe.throw(_("Loyalty Card does not belong to this Customer"))
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


def get_loyalty_points(customer, company):
    loyalty_details = get_loyalty_details(
        customer,
        frappe.db.get_value('Customer', customer, 'loyalty_program'),
        company=company
    )
    return loyalty_details.get('loyalty_points') - loyalty_details.get('total_spent')
