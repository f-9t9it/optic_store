# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial, reduce
from toolz import compose, pluck, merge, concatv, valmap

from optic_store.utils import pick


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    def make_column(key, label=None, type="Data", options=None, width=120):
        return {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    return [
        make_column(
            "invoice_name",
            "Sales Invoice",
            type="Link",
            options="Sales Invoice",
            width=150,
        ),
        make_column("invoice_date", type="Date", width=90),
        make_column("brand", type="Link", options="Brand"),
        make_column("item_code", type="Link", options="Item"),
        make_column("item_group", type="Link", options="Item Group"),
        make_column("description"),
        make_column("valuation_rate", "Cost Price", type="Currency", width=90),
        make_column("selling_rate", "Standard Selling Rate", type="Currency", width=90),
        make_column("rate", "Sale Unit Rate", type="Currency", width=90),
        make_column("qty", type="Float", width=90),
        make_column(
            "amount_before_discount",
            "Sale Amount Before Discount",
            type="Currency",
            width=90,
        ),
        make_column("discount_amount", type="Currency", width=90),
        make_column("discount_percentage", type="Percent", width=90),
        make_column(
            "amount_after_discount",
            "Sale Amount After Discount",
            type="Currency",
            width=90,
        ),
        make_column("tax_amount", type="Currency", width=90),
        make_column("ms1", "Minimum Selling Rate 1", type="Currency", width=90),
        make_column(
            "below_ms1",
            "Sold Below Mimimum Selling Rate 1",
            type="Select",
            options=["No", "Yes"],
            width=60,
        ),
        make_column("ms2", "Minimum Selling Rate 2", type="Currency", width=90),
        make_column(
            "below_ms2",
            "Sold Below Mimimum Selling Rate 2",
            type="Select",
            options=["No", "Yes"],
            width=60,
        ),
        make_column("sales_person", type="Link", options="Employee"),
        make_column("remarks", type="Small Text", width=150),
        make_column("customer", type="Link", options="Customer"),
        make_column("notes", type="Small Text", width=150),
        make_column("dispensor", type="Link", options="Employee"),
        make_column("branch", type="Link", options="Branch"),
        make_column("sales_status", type="Select", options=["Achieved", "Collected"]),
        make_column("collection_date", type="Date", width=90),
    ]


def _get_filters(filters):
    clauses = concatv(
        ["si.docstatus = 1"],
        [
            "(si.update_stock = 1 OR sii.delivered_qty = sii.qty)",
            """
                (
                    (
                        si.update_stock = 1 AND
                        si.posting_date BETWEEN %(from_date)s AND %(to_date)s
                    ) OR (
                        si.update_stock = 0 AND
                        dn.posting_date BETWEEN %(from_date)s AND %(to_date)s
                    )
                )
            """,
        ]
        if filters.report_type == "Collected"
        else [],
        [
            "(si.update_stock = 0 OR sii.delivered_qty < sii.qty)",
            "si.posting_date BETWEEN %(from_date)s AND %(to_date)s",
        ]
        if filters.report_type == "Achieved"
        else [],
    )
    values = merge(
        filters,
        {
            "selling_pl": "Standard Selling",
            "min_selling_pl1": "Minimum Selling",
            "min_selling_pl2": "Minimum Selling 2",
        },
    )
    return " AND ".join(clauses), values


def _get_data(clauses, values, keys):
    def make_price_query(alias, pl):
        return """
            `tabItem Price` AS {alias} ON
                {alias}.item_code = sii.item_code AND
                IFNULL({alias}.uom, '') IN (sii.stock_uom, '') AND
                IFNULL({alias}.customer, '') IN (si.customer, '') AND
                IFNULL({alias}.min_qty, 0) <= sii.qty AND
                {alias}.price_list = %({pl})s AND
                si.posting_date BETWEEN
                    IFNULL({alias}.valid_from, '2000-01-01') AND
                    IFNULL({alias}.valid_upto, '2500-12-31')
        """.format(
            alias=alias, pl=pl
        )

    items = frappe.db.sql(
        """
            SELECT
                si.name AS invoice_name,
                si.posting_date AS invoice_date,
                sii.brand AS brand,
                sii.item_code AS item_code,
                sii.item_group AS item_group,
                sii.description AS description,
                bp.valuation_rate AS valuation_rate,
                sp.price_list_rate AS selling_rate,
                sii.rate AS rate,
                sii.qty AS qty,
                sii.amount - sii.discount_amount AS amount_before_discount,
                sii.discount_amount AS discount_amount,
                sii.discount_percentage AS discount_percentage,
                sii.amount AS amount_after_discount,
                '' AS tax_amount,
                ms1.price_list_rate AS ms1,
                IF (sii.amount < ms1.price_list_rate, 'Yes', 'No') AS below_ms1,
                ms2.price_list_rate AS ms2,
                IF(sii.amount < ms2.price_list_rate, 'Yes', 'No') AS below_ms2,
                si.os_sales_person AS sales_person,
                '' AS remarks,
                si.customer AS customer,
                si.os_notes AS notes,
                si.orx_dispensor AS dispensor,
                si.os_branch AS branch,
                IF(
                    si.update_stock = 1 OR sii.qty = sii.delivered_qty,
                    'Collected', 'Achieved'
                ) AS sales_status,
                si.update_stock AS own_delivery,
                dn.posting_date AS delivery_date
            FROM `tabSales Invoice` AS si
            RIGHT JOIN `tabSales Invoice Item` AS sii ON
                sii.parent = si.name
            LEFT JOIN `tabDelivery Note Item` AS dni ON
                dni.against_sales_invoice = si.name AND
                dni.item_code = sii.item_code
            LEFT JOIN `tabDelivery Note` AS dn ON
                dn.name = dni.parent
            LEFT JOIN `tabBin` AS bp ON
                bp.item_code = sii.item_code AND
                bp.warehouse = sii.warehouse
            LEFT JOIN {selling_pl}
            LEFT JOIN {min_selling_pl1}
            LEFT JOIN {min_selling_pl2}
            WHERE {clauses}
            ORDER BY invoice_date
        """.format(
            clauses=clauses,
            selling_pl=make_price_query("sp", "selling_pl"),
            min_selling_pl1=make_price_query("ms1", "min_selling_pl1"),
            min_selling_pl2=make_price_query("ms2", "min_selling_pl2"),
        ),
        values=values,
        as_dict=1,
    )

    def add_collection_date(row):
        def get_collection_date():
            if row.sales_status == "Achieved":
                return None
            if row.own_delivery:
                return row.invoice_date
            return row.delivery_date

        return merge(row, {"collection_date": get_collection_date()})

    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})
    make_row = compose(
        partial(pick, keys),
        partial(valmap, lambda x: x or None),
        partial(merge, template),
        add_collection_date,
    )

    return map(make_row, items)
