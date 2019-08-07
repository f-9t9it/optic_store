# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial, reduce
from toolz import (
    compose,
    pluck,
    merge,
    concatv,
    itemmap,
    unique,
    groupby,
    get,
    reduceby,
)

from optic_store.utils import pick, split_to_list, with_report_error_check
from optic_store.api.sales_invoice import get_payments_against


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

    columns = concatv(
        [
            make_column(
                "invoice_name",
                "Sales Invoice",
                type="Link",
                options="Sales Invoice",
                width=150,
            ),
            make_column("invoice_date", type="Date", width=90),
            make_column("invoice_time", type="Time", width=90),
            make_column("brand", type="Link", options="Brand"),
            make_column("item_code", type="Link", options="Item"),
            make_column("item_group", type="Link", options="Item Group"),
            make_column("description"),
        ],
        [make_column("valuation_rate", "Cost Price", type="Currency", width=90)]
        if "Accounts Manager" in frappe.get_roles()
        else [],
        [
            make_column(
                "selling_rate", "Standard Selling Rate", type="Currency", width=90
            ),
            make_column("rate", "Sale Unit Rate", type="Currency", width=90),
            make_column("qty", type="Float", width=90),
        ],
        [make_column("valuation_amount", "Cost Amount", type="Currency", width=90)]
        if "Accounts Manager" in frappe.get_roles()
        else [],
        [
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
            make_column("sales_person_name", width="150"),
            make_column("commission_amount", type="Currency", width=90),
            make_column("remarks", type="Small Text", width=150),
            make_column("customer", type="Link", options="Customer"),
            make_column("customer_name", width="150"),
            make_column("notes", type="Small Text", width=150),
            make_column("dispensor", type="Link", options="Employee"),
            make_column("branch", type="Link", options="Branch"),
            make_column(
                "sales_status", type="Select", options=["Achieved", "Collected"]
            ),
            make_column("collection_date", type="Date", width=90),
        ],
    )

    return list(columns)


def _get_filters(filters):
    branches = split_to_list(filters.branches)

    clauses = concatv(
        ["si.docstatus = 1"],
        ["si.os_branch IN %(branches)s"] if branches else [],
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
        {"branches": branches} if branches else {},
        {
            "selling_pl": "Standard Selling",
            "min_selling_pl1": "Minimum Selling",
            "min_selling_pl2": "Minimum Selling 2",
        },
    )
    return " AND ".join(clauses), values


@with_report_error_check
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
                sii.sales_order AS order_name,
                si.posting_date AS invoice_date,
                si.posting_time AS invoice_time,
                sii.brand AS brand,
                sii.item_code AS item_code,
                sii.item_group AS item_group,
                sii.description AS description,
                bp.valuation_rate AS valuation_rate,
                sp.price_list_rate AS selling_rate,
                sii.rate AS rate,
                sii.qty AS qty,
                sii.qty * IFNULL(bp.valuation_rate, 0) AS valuation_amount,
                sii.amount - sii.discount_amount AS amount_before_discount,
                sii.discount_amount AS discount_amount,
                sii.discount_percentage AS discount_percentage,
                sii.amount AS amount_after_discount,
                ms1.price_list_rate AS ms1,
                IF (sii.amount < ms1.price_list_rate, 'Yes', 'No') AS below_ms1,
                ms2.price_list_rate AS ms2,
                IF(sii.amount < ms2.price_list_rate, 'Yes', 'No') AS below_ms2,
                si.os_sales_person AS sales_person,
                si.os_sales_person_name AS sales_person_name,
                IF(
                    si.total = 0,
                    0,
                    si.total_commission * sii.amount / si.total
                ) AS commission_amount,
                si.customer AS customer,
                si.customer_name AS customer_name,
                si.os_notes AS notes,
                si.orx_dispensor AS dispensor,
                si.os_branch AS branch,
                IF(
                    si.update_stock = 1 OR sii.qty = sii.delivered_qty,
                    'Collected',
                    'Achieved'
                ) AS sales_status,
                si.update_stock AS own_delivery,
                dn.posting_date AS delivery_date
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN `tabSales Invoice` AS si ON
                si.name = sii.parent
            LEFT JOIN (
                SELECT
                    idni.si_detail AS si_detail,
                    idn.is_return AS is_return,
                    idn.posting_date AS posting_date
                FROM `tabDelivery Note Item` AS idni
                LEFT JOIN `tabDelivery Note` AS idn ON
                    idn.name = idni.parent
            ) AS dn ON
                dn.si_detail = sii.name AND
                dn.is_return = si.is_return
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
        def get_collection_date(x):
            if x.sales_status == "Achieved":
                return None
            if x.own_delivery:
                return x.invoice_date
            return x.delivery_date

        return merge(row, {"collection_date": get_collection_date(row)})

    def add_payment_remarks(items):
        payments = _get_payments(items)

        def fn(row):
            make_remark = compose(
                lambda x: ", ".join(x),
                partial(map, lambda x: "{mop}: {amount}".format(mop=x[0], amount=x[1])),
                lambda x: x.items(),
                lambda lines: reduceby(
                    "mode_of_payment",
                    lambda a, x: a + get("paid_amount", x, 0),
                    lines,
                    0,
                ),
                lambda x: concatv(
                    get(x.invoice_name, payments, []), get(x.order_name, payments, [])
                ),
                frappe._dict,
            )

            return merge(row, {"remarks": make_remark(row)})

        return fn

    def set_null(k, v):
        if v:
            return k, v
        if k not in [
            "valuation_rate",
            "selling_rate",
            "rate",
            "qty",
            "valuation_amount",
            "amount_before_discount",
            "discount_amount",
            "discount_percentage",
            "amount_after_discount",
            "ms1",
            "ms2",
            "commission_amount",
        ]:
            return k, None
        return k, 0

    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})
    make_row = compose(
        partial(pick, keys),
        partial(itemmap, lambda x: set_null(*x)),
        partial(merge, template),
        add_payment_remarks(items),
        add_collection_date,
    )

    return map(make_row, items)


def _get_payments(items):
    def get_names(key):
        return compose(list, unique, partial(pluck, key))(items)

    invoices = get_names("invoice_name")

    si_payments = frappe.db.sql(
        """
            SELECT parent AS reference_name, mode_of_payment, amount AS paid_amount
            FROM `tabSales Invoice Payment` WHERE parent IN %(invoices)s
        """,
        values={"invoices": invoices},
        as_dict=1,
    )
    payments_against_si = get_payments_against("Sales Invoice", invoices)
    payments_against_so = get_payments_against("Sales Order", get_names("order_name"))

    return groupby(
        "reference_name", concatv(si_payments, payments_against_si, payments_against_so)
    )
