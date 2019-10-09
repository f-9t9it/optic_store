# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import pluck, compose

from optic_store.api.item import get_min_prices


def execute():
    cache = {}

    def get_price(item_code):
        if cache.get(item_code):
            return cache.get(item_code)
        prices = get_min_prices(item_code)
        cache.update({item_code: prices})
        return prices

    get_names = compose(partial(pluck, "name"), frappe.get_all)

    for doctype in ["Sales Order Item", "Sales Invoice Item"]:
        for cdn in get_names(doctype):
            item = frappe.get_doc(doctype, cdn)
            prices = get_price(item.item_code)
            if not item.os_minimum_selling_rate and prices.get("ms1"):
                frappe.db.set_value(
                    doctype, cdn, "os_minimum_selling_rate", prices.get("ms1")
                )
            if not item.os_minimum_selling_2_rate and prices.get("ms2"):
                frappe.db.set_value(
                    doctype, cdn, "os_minimum_selling_2_rate", prices.get("ms2")
                )
