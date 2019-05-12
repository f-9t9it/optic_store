# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import now


@frappe.whitelist()
def create_opening(opening_cash, company, pos_profile, user=None, start_time=None):
    xzreport = frappe.get_doc(
        {
            "doctype": "XZ Report",
            "start_time": start_time or now(),
            "user": user or frappe.session.user,
            "pos_profile": pos_profile,
            "company": company,
            "opening_cash": opening_cash,
        }
    ).insert(ignore_permissions=True)
    return xzreport.name


@frappe.whitelist()
def get_unclosed(user, pos_profile, company):
    return frappe.db.exists(
        "XZ Report",
        {"user": user, "pos_profile": pos_profile, "company": company, "docstatus": 0},
    )
