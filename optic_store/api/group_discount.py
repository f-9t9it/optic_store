# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json


@frappe.whitelist()
def get_item_discounts(discount_name, item_codes):
    discounts = frappe.db.sql(
        """
            SELECT
                i.item_code AS item_code,
                IFNULL(gd.discount_rate, 0) AS discount_rate
            FROM `tabItem` AS i
            LEFT JOIN (
                SELECT
                    b.name AS brand,
                    gdbc.discount_rate AS discount_rate
                FROM `tabBrand` AS b
                LEFT JOIN `tabGroup Discount Brand Category` AS gdbc
                    ON gdbc.brand_category = b.brand_category
                WHERE gdbc.parent = %(discount_name)s
            ) AS gd
                ON gd.brand = i.brand
            WHERE i.item_code IN %(item_codes)s
        """,
        values={"discount_name": discount_name, "item_codes": json.loads(item_codes)},
        as_dict=1,
    )
    return discounts
