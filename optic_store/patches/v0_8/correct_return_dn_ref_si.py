# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute():
    dnis = frappe.db.sql(
        """
            SELECT
                dni.name AS name,
                fdni.against_sales_invoice AS against_sales_invoice,
                fdni.si_detail AS si_detail
            FROM `tabDelivery Note Item` AS dni
            LEFT JOIN `tabDelivery Note` AS dn ON dn.name = dni.parent
            LEFT JOIN `tabSales Invoice` AS si ON si.name = dni.against_sales_invoice
            LEFT JOIN `tabDelivery Note Item` AS fdni
                ON fdni.parent = dn.return_against AND fdni.idx = dni.idx
            WHERE
                dn.docstatus < 2 AND
                dn.is_return = 1 AND
                si.is_return = 1
        """,
        as_dict=1,
    )
    for dni in dnis:
        frappe.db.set_value(
            "Delivery Note Item",
            dni.get("name"),
            "against_sales_invoice",
            dni.get("against_sales_invoice"),
        )
        frappe.db.set_value(
            "Delivery Note Item", dni.get("name"), "si_detail", dni.get("si_detail")
        )
