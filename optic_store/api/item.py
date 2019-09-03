# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from toolz import dissoc, merge


@frappe.whitelist()
def get_prices(item_code):
    prices = frappe.db.sql(
        """
            SELECT
                pl.price_list AS price_list,
                ip.price_list_rate AS price_list_rate
            FROM `tabOptical Store Settings Price List` AS pl
            LEFT JOIN (
                SELECT price_list, price_list_rate
                FROM `tabItem Price`
                WHERE item_code = %(item_code)s
            ) AS ip ON ip.price_list = pl.price_list
            ORDER by pl.idx
        """,
        values={"item_code": item_code},
        as_dict=1,
    )
    return prices


@frappe.whitelist()
def get_min_prices(item_code):
    def get_price(price_list):
        return frappe.db.get_value(
            "Item Price",
            {"item_code": item_code, "price_list": price_list},
            "price_list_rate",
        )

    return {"ms1": get_price("Minimum Selling"), "ms2": get_price("Minimum Selling 2")}


@frappe.whitelist()
def update_prices(item_code, prices):
    price_list_rates = json.loads(prices)
    map(lambda x: _update_price(item_code, **x), price_list_rates)


def _update_price(item_code, price_list, price_list_rate=0):
    item_price = frappe.db.exists(
        "Item Price", {"item_code": item_code, "price_list": price_list}
    )
    if not item_price:
        if price_list_rate:
            frappe.get_doc(
                {
                    "doctype": "Item Price",
                    "item_code": item_code,
                    "price_list": price_list,
                    "price_list_rate": price_list_rate,
                }
            ).insert()
    else:
        doc = frappe.get_doc("Item Price", item_price)
        if price_list_rate:
            if doc.price_list_rate != price_list_rate:
                doc.price_list_rate = price_list_rate
                doc.save()
        else:
            doc.delete()


@frappe.whitelist()
def get_item_details(args):
    from erpnext.stock.get_item_details import get_item_details

    result = get_item_details(args)
    return dissoc(result, "batch_no")
