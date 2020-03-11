# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, excepts, first, unique, valmap, concatv

from optic_store.utils import key_by


def get_cashback_program(branch, posting_date):
    program_names = [
        x.get("name")
        for x in frappe.db.sql(
            """
                SELECT cp.name AS name FROM `tabCashback Program` AS cp
                LEFT JOIN `tabCashback Program Branch` AS cpb ON
                    cpb.parent = cp.name
                WHERE
                    cp.disabled = 0 AND
                    cpb.branch = %(branch)s AND
                    %(posting_date)s BETWEEN
                        cp.from_date AND IFNULL(cp.to_date, '9999-12-31')
            """,
            values={"branch": branch, "posting_date": posting_date},
            as_dict=1,
        )
    ]
    if len(program_names) > 1:
        frappe.throw(
            frappe._("Something is wrong. More than one Cashback Program found.")
        )

    get_program = compose(
        lambda x: frappe.get_doc("Cashback Program", x) if x else None,
        excepts(StopIteration, first, lambda x: None),
    )

    return get_program(program_names)


def get_invoice_casback_amount(items, cashback_program):
    item_prices = _get_item_prices(items, cashback_program.price_list)

    # validates price check against all items
    if not all([x.net_rate == item_prices.get(x.item_code) for x in items]):
        return 0

    applicable_item_codes = _get_applicable_item_codes(items, cashback_program)
    applicable_doc_items = [x for x in items if x.item_code in applicable_item_codes]

    # calculates amount against just the applicable items
    return sum(
        [x.amount * cashback_program.cashback_rate / 100 for x in applicable_doc_items]
    )


_get_item_codes = compose(list, unique, partial(map, lambda x: x.item_code))


def _get_item_prices(items, price_list):
    get_price_map = compose(
        partial(valmap, lambda x: x.get("price_list_rate")),
        partial(key_by, "item_code"),
        frappe.db.sql,
    )
    return get_price_map(
        """
            SELECT item_code, price_list_rate FROM `tabItem Price`
            WHERE price_list = %(price_list)s AND item_code IN %(item_codes)s
        """,
        values={"price_list": price_list, "item_codes": _get_item_codes(items)},
        as_dict=1,
    )


def _get_applicable_item_codes(items, cashback_program):
    values = {
        "item_codes": _get_item_codes(items),
        "item_groups": [x.item_group for x in cashback_program.item_groups],
        "brands": [x.brand for x in cashback_program.brands],
    }

    def join(sep):
        return compose(lambda x: sep.join(x), concatv)

    ander = join(" AND ")
    orer = join(" OR ")

    item_attrib = orer(
        ["item_group IN %(item_groups)s"] if values.get("item_groups") else [],
        ["brand IN %(brands)s"] if values.get("brands") else [],
    )
    clauses = ander(
        ["name IN %(item_codes)s"] if values.get("item_codes") else [],
        ["os_ignore_cashback = 0"],
        ["({})".format(item_attrib)] if item_attrib else [],
    )
    return [
        x.get("name")
        for x in frappe.db.sql(
            "SELECT name FROM `tabItem` {where}".format(
                where="WHERE {}".format(clauses) if clauses else ""
            ),
            values=values,
            as_dict=1,
        )
    ]
