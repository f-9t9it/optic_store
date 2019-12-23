# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from optic_store.api.item import get_min_prices


def execute():
    def get_docs(doctype):
        return frappe.db.sql(
            """
                SELECT
                    name,
                    '{doctype}' AS doctype,
                    item_code,
                    os_minimum_selling_rate,
                    os_minimum_selling_2_rate
                FROM `tab{doctype}` WHERE
                    IFNULL(os_minimum_selling_rate, 0) = 0 OR
                    IFNULL(os_minimum_selling_2_rate, 0) = 0
            """.format(
                doctype=doctype
            ),
            as_dict=1,
        )

    def set_prices(row):
        prices = get_min_prices(row.get("item_code"))
        if not row.get("os_minimum_selling_rate") and prices.get("ms1"):
            frappe.db.set_value(
                row.get("doctype"),
                row.get("name"),
                "os_minimum_selling_rate",
                prices.get("ms1"),
            )
        if not row.get("os_minimum_selling_2_rate") and prices.get("ms2"):
            frappe.db.set_value(
                row.get("doctype"),
                row.get("name"),
                "os_minimum_selling_2_rate",
                prices.get("ms2"),
            )

    for doc in get_docs("Sales Order Item"):
        set_prices(doc)
    for doc in get_docs("Sales Invoice Item"):
        set_prices(doc)
