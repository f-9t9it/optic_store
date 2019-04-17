# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from functools import partial, reduce
from toolz import compose, groupby, merge, keyfilter, valmap


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


def get_brand_discounts():
    discounts = frappe.db.sql(
        """
            SELECT
                gd.name AS group_discount,
                gdbc.brand_category AS brand_category,
                gdbc.discount_rate AS discount_rate
            FROM
                `tabGroup Discount` as gd
            RIGHT JOIN `tabGroup Discount Brand Category` AS gdbc
                ON gdbc.parent = gd.name
            WHERE gd.disabled = 0
        """,
        as_dict=1,
    )
    brands = frappe.db.sql(
        """
            SELECT name AS brand, brand_category
            FROM `tabBrand`
            WHERE IFNULL(brand_category, '') != ''
        """,
        as_dict=1,
    )

    brand_mapper = compose(
        lambda d: {x.get("brand"): x.get("discount_rate") for x in d},
        lambda d: reduce(lambda a, x: a + x, d, []),
        partial(map, _convert_to_brands(brands)),
    )

    discount_mapper = compose(
        partial(valmap, brand_mapper), partial(groupby, "group_discount")
    )
    return discount_mapper(discounts)


def _convert_to_brands(brands):
    brands_by_category = groupby("brand_category", brands)

    def fn(discount):
        brands = brands_by_category.get(discount.get("brand_category"), [])
        return map(
            lambda x: merge(_pick(["brand"], x), _pick(["discount_rate"], discount)),
            brands,
        )

    return fn


def _pick(whitelist, d):
    return keyfilter(lambda k: k in whitelist, d)
