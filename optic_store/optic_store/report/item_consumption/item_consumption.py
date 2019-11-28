# Copyright (c) 2013,     9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today
from functools import partial, reduce
import operator
from toolz import merge, pluck, get, compose, first, flip, groupby, excepts, keyfilter

from optic_store.utils.helpers import generate_intervals


def execute(filters=None):
    args = _get_args(filters)
    columns = _get_columns(args)
    data = _get_data(args, columns)
    make_column = partial(
        keyfilter,
        lambda k: k in ["label", "fieldname", "fieldtype", "options", "width"],
    )
    return [make_column(x) for x in columns], data


def _get_args(filters={}):
    if not filters.get("company"):
        frappe.throw(_("Company is required to generate report"))
    return merge(
        filters,
        {
            "price_list": frappe.db.get_value(
                "Buying Settings", None, "buying_price_list"
            ),
            "start_date": filters.get("start_date") or today(),
            "end_date": filters.get("end_date") or today(),
        },
    )


def _get_columns(args):
    def make_column(key, label, type="Float", options=None, width=90):
        return {
            "label": _(label),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    columns = [
        make_column("item_code", "Item Code", type="Link", options="Item", width=120),
        make_column("brand", "Brand", type="Link", options="Brand", width=120),
        make_column("item_name", "Item Name", type="Data", width=200),
        make_column("supplier", "Supplier", type="Link", options="Supplier", width=120),
        make_column(
            "price",
            args.get("price_list", "Standard Buying Price"),
            type="Currency",
            width=120,
        ),
        make_column("stock", "Available Stock"),
    ]
    intervals = compose(
        list,
        partial(map, lambda x: merge(x, make_column(x.get("key"), x.get("label")))),
        generate_intervals,
    )
    return (
        columns
        + intervals(args.get("interval"), args.get("start_date"), args.get("end_date"))
        + [make_column("total_consumption", "Total Consumption")]
    )


def _get_data(args, columns):
    warehouse_conditions = (
        "warehouse = %(warehouse)s"
        if args.get("warehouse")
        else (
            "warehouse IN (SELECT name FROM `tabWarehouse` WHERE company = %(company)s)"
        )
    )
    items = frappe.db.sql(
        """
            SELECT
                i.item_code AS item_code,
                i.brand AS brand,
                i.item_name AS item_name,
                id.default_supplier AS supplier,
                p.price_list_rate AS price,
                b.actual_qty AS stock
            FROM `tabItem` AS i
            LEFT JOIN `tabItem Price` AS p
                ON p.item_code = i.item_code AND p.price_list = %(price_list)s
            LEFT JOIN (
                SELECT
                    item_code, SUM(actual_qty) AS actual_qty
                FROM `tabBin`
                WHERE {warehouse_conditions}
                GROUP BY item_code
            ) AS b
                ON b.item_code = i.item_code
            LEFT JOIN `tabItem Default` AS id
                ON id.parent = i.name AND id.company = %(company)s
        """.format(
            warehouse_conditions=warehouse_conditions
        ),
        values={
            "price_list": args.get("price_list"),
            "company": args.get("company"),
            "warehouse": args.get("warehouse"),
        },
        as_dict=1,
    )
    sles = frappe.db.sql(
        """
            SELECT item_code, posting_date, actual_qty
            FROM `tabStock Ledger Entry`
            WHERE docstatus < 2 AND
                voucher_type = 'Sales Invoice' AND
                company = %(company)s AND
                {warehouse_conditions} AND
                posting_date BETWEEN %(start_date)s AND %(end_date)s
        """.format(
            warehouse_conditions=warehouse_conditions
        ),
        values={
            "company": args.get("company"),
            "warehouse": args.get("warehouse"),
            "start_date": args.get("start_date"),
            "end_date": args.get("end_date"),
        },
        as_dict=1,
    )
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    periods = list(filter(lambda x: x.get("start_date") and x.get("end_date"), columns))

    set_consumption = _set_consumption(sles, periods)

    make_row = compose(partial(keyfilter, lambda k: k in keys), set_consumption)

    return [make_row(x) for x in items]


def _set_consumption(sles, periods):
    def groupby_filter(sl):
        def fn(p):
            return p.get("start_date") <= sl.get("posting_date") <= p.get("end_date")

        return fn

    groupby_fn = compose(
        partial(get, "key", default=None),
        excepts(StopIteration, first, lambda __: {}),
        partial(flip, filter, periods),
        groupby_filter,
    )

    sles_grouped = groupby(groupby_fn, sles)

    summer = compose(operator.neg, sum, partial(pluck, "actual_qty"))

    def seg_filter(x):
        return lambda sl: sl.get("item_code") == x

    segregator_fns = [
        merge(
            x,
            {
                "seger": compose(
                    summer,
                    partial(flip, filter, get(x.get("key"), sles_grouped, [])),
                    seg_filter,
                )
            },
        )
        for x in periods
    ]

    def seg_reducer(item_code):
        def fn(a, p):
            key = get("key", p, None)
            seger = get("seger", p, lambda __: None)
            return merge(a, {key: seger(item_code)})

        return fn

    total_fn = compose(summer, partial(flip, filter, sles), seg_filter)

    def fn(item):
        item_code = item.get("item_code")
        return merge(
            item,
            reduce(seg_reducer(item_code), segregator_fns, {}),
            {"total_consumption": total_fn(item_code)},
        )

    return fn
