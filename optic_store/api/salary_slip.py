# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_salary_slips_from_payroll_entry(payroll_entry):
    return [
        x.get("name")
        for x in frappe.get_all(
            "Salary Slip", filters={"docstatus": 1, "payroll_entry": payroll_entry}
        )
    ]


def get_salary_slip_docs_from_payroll_entry(payroll_entry):
    return [
        frappe.get_doc("Salary Slip", x)
        for x in get_salary_slips_from_payroll_entry(payroll_entry)
    ]
