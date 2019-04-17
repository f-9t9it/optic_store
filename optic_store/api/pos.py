# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from optic_store.api.group_discount import get_brand_discounts


@frappe.whitelist()
def get_extended_pos_data():
    return {
        "sales_persons": _get_sales_persons(),
        "group_discounts": get_brand_discounts(),
    }


def _get_sales_persons():
    sales_person_department = frappe.db.get_single_value(
        "Optical Store Settings", "sales_person_department"
    )
    return frappe.get_all(
        "Employee",
        fields=["name", "employee_name"],
        filters=[["department", "=", sales_person_department]],
    )
