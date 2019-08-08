# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import today, cint
from frappe.utils.nestedset import get_root_of
from erpnext.stock.get_item_details import get_pos_profile
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from erpnext.selling.page.point_of_sale.point_of_sale import (
    search_serial_or_batch_or_barcode_number,
)
from erpnext.accounts.doctype.sales_invoice.pos import get_customers_list
from erpnext.accounts.doctype.sales_invoice.pos import get_customer_id
from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_details
from functools import partial
from toolz import (
    pluck,
    compose,
    valfilter,
    valmap,
    merge,
    get,
    groupby,
    flip,
    concatv,
    unique,
    excepts,
    first,
)

from optic_store.api.group_discount import get_brand_discounts
from optic_store.api.customer import CUSTOMER_DETAILS_FIELDS, get_user_branch
from optic_store.utils import pick, key_by


@frappe.whitelist()
def get_extended_pos_data(company):
    pos_profile = get_pos_profile(company)
    if not pos_profile.warehouse:
        frappe.throw(_("Warehouse missing in POS Profile"))
    query_date = today()
    return {
        "sales_persons": _get_sales_persons(),
        "group_discounts": get_brand_discounts(),
        "customers_details": _get_customers_details(pos_profile, query_date),
        "loyalty_programs": _get_loyalty_programs(company),
        "gift_cards": _get_gift_cards(query_date),
        "territories": _get_territories(),
        "customer_groups": _get_customer_groups(),
        "batch_details": _get_batch_details(pos_profile.warehouse),
        "branch_details": _get_branch_details(),
    }


def _get_sales_persons():
    sales_person_department = frappe.db.get_single_value(
        "Optical Store Settings", "sales_person_department"
    )
    return frappe.get_all(
        "Employee",
        fields=["name", "employee_name"],
        filters=[["department", "=", sales_person_department]],
    )


def _get_customers_details(pos_profile, query_date):
    customers = compose(list, partial(pluck, "name"), get_customers_list)(pos_profile)
    details = frappe.db.sql(
        """
            SELECT
                name,
                old_customer_id,
                customer_name,
                os_loyalty_card_no,
                loyalty_program,
                {customer_details_fields}
            FROM `tabCustomer` WHERE name IN %(customers)s
        """.format(
            customer_details_fields=", ".join(CUSTOMER_DETAILS_FIELDS)
        ),
        values={"customers": customers},
        as_dict=1,
    )

    def add_loyalty_points(customer):
        loyalty_points = get_loyalty_details(
            customer.get("name"),
            customer.get("loyalty_program"),
            expiry_date=query_date,
        )
        return merge(customer, pick(["loyalty_points"], loyalty_points))

    return map(compose(add_loyalty_points, partial(valfilter, lambda x: x)), details)


def _get_loyalty_programs(company):
    return frappe.get_all(
        "Loyalty Program",
        fields=["name", "conversion_factor"],
        filters={"company": company},
    )


def _get_gift_cards(query_date):
    return frappe.db.sql(
        """
            SELECT name, balance, expiry_date FROM `tabGift Card`
            WHERE
                balance > 0 AND (
                    IFNULL(expiry_date, '') = '' OR
                    expiry_date >= %(expiry_date)s
                )
        """,
        values={"expiry_date": query_date},
        as_dict=1,
    )


def _get_territories():
    return compose(list, partial(pluck, "name"))(frappe.get_all("Territory"))


def _get_customer_groups():
    return compose(list, partial(pluck, "name"))(frappe.get_all("Customer Group"))


def _get_branch_details():
    branch = get_user_branch()
    if not branch:
        return None
    doc = frappe.get_doc("Branch", branch)
    return pick(["name", "branch_phone", "os_cr_no"], doc.as_dict()) if doc else None


@frappe.whitelist()
def get_pos_data():
    from erpnext.accounts.doctype.sales_invoice.pos import get_pos_data

    data = get_pos_data()
    allowed_items = get("bin_data", data, {}).keys()
    prices = _get_item_prices(allowed_items)

    def set_prices(item):
        get_price = compose(
            partial(get, seq=prices, default={}), partial(get, "item_code")
        )
        return merge(item, get_price(item))

    trans_items = compose(
        partial(map, set_prices),
        partial(filter, lambda x: x.get("name") in allowed_items),
        partial(get, "items", default=[]),
    )
    add_branch = compose(
        flip(merge, {"os_branch": get_user_branch()}),
        lambda x: x.as_dict(),
        partial(get, "doc", default={}),
    )

    return merge(data, {"items": trans_items(data), "doc": add_branch(data)})


def _get_item_prices(item_codes):
    if not item_codes:
        return {}
    result = frappe.db.sql(
        """
            SELECT
                name AS item_code,
                os_minimum_selling_rate,
                os_minimum_selling_2_rate
            FROM `tabItem`
            WHERE name in %(item_codes)s
        """,
        values={"item_codes": item_codes},
        as_dict=1,
    )
    return key_by("item_code", result)


def _get_batch_details(warehouse):
    batches = frappe.db.sql(
        """
                SELECT
                    name,
                    item,
                    expiry_date,
                    (
                        SELECT SUM(actual_qty)
                        FROM `tabStock Ledger Entry`
                        WHERE batch_no=b.name AND
                            item_code=b.item AND
                            warehouse=%(warehouse)s
                    ) as qty
                FROM `tabBatch` AS b
                WHERE IFNULL(expiry_date, '4000-10-10') >= CURDATE()
                ORDER BY expiry_date
            """,
        values={"warehouse": warehouse},
        as_dict=1,
    )
    return compose(partial(groupby, "item"), partial(filter, lambda x: x.get("qty")))(
        batches
    )


@frappe.whitelist()
def make_invoice(doc_list={}, email_queue_list={}, customers_list={}):
    from erpnext.accounts.doctype.sales_invoice.pos import make_invoice

    result = make_invoice(doc_list, email_queue_list, customers_list)
    _update_customer_details(customers_list)
    return result


def _update_customer_details(customers_list):
    def update_details(customer, data):
        cust_id = get_customer_id(data, customer)
        doc = frappe.get_doc("Customer", cust_id)
        doc.update(pick(CUSTOMER_DETAILS_FIELDS, data))
        doc.flags.ignore_mandatory = True
        doc.save(ignore_permissions=True)

    updater = compose(
        partial(map, lambda x: update_details(*x)),
        lambda x: x.items(),
        partial(valmap, json.loads),
        json.loads,
    )
    updater(customers_list)
    frappe.db.commit()


@frappe.whitelist()
def get_items(
    start,
    page_length,
    price_list,
    item_group,
    search_value="",
    pos_profile=None,
    customer=None,
):
    search_data = (
        search_serial_or_batch_or_barcode_number(search_value) if search_value else {}
    )
    clauses, values = _get_conditions(
        merge(
            {
                "start": cint(start),
                "page_length": cint(page_length),
                "price_list": price_list,
                "item_group": item_group or get_root_of("Item Group"),
                "search_value": search_value,
                "pos_profile": pos_profile,
                "customer": customer,
            },
            search_data,
        )
    )

    items = frappe.db.sql(
        """
            SELECT
                i.name AS item_code,
                i.item_name AS item_name,
                i.image AS item_image,
                i.idx AS idx,
                i.is_stock_item AS is_stock_item,
                i.variant_of AS variant_of
            FROM `tabItem` AS i
            LEFT JOIN `tabItem Group` AS ig ON ig.name = i.item_group
            {stock_clause}
            WHERE {clauses}
            ORDER BY i.idx
            LIMIT %(start)s, %(page_length)s
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
        debug=1,
    )

    def list_items(items):
        make_list = compose(partial(filter, lambda x: x), unique, concatv)
        return make_list(pluck("item_code", items), pluck("variant_of", items))

    make_prices = compose(
        partial(valmap, partial(groupby, "item_code")), partial(groupby, "price_list")
    )

    # better to use a second query to fetch prices because combining with items query
    # takes considerably longer
    prices = (
        make_prices(
            frappe.db.sql(
                """
                SELECT
                    i.name AS item_code,
                    ip.price_list AS price_list,
                    ip.price_list_rate AS price_list_rate,
                    ip.currency AS currency
                FROM `tabItem Price` AS ip
                LEFT JOIN `tabItem` AS i ON i.name = ip.item_code
                WHERE
                    ip.selling = 1 AND
                    ip.item_code IN %(items)s AND
                    IFNULL(ip.uom, '') IN (i.stock_uom, '') AND
                    IFNULL(ip.min_qty, 0) <= 1 AND
                    IFNULL(ip.customer, '') IN (%(customer)s, '') AND
                    CURDATE() BETWEEN
                        IFNULL(ip.valid_from, '2000-01-01') AND
                        IFNULL(ip.valid_upto, '2500-12-31')
            """,
                values={"items": list_items(items), "customer": customer},
                as_dict=1,
                debug=1,
            )
        )
        if items
        else []
    )

    def add_price(prices):
        def make_price(item_code):
            return compose(
                excepts(StopIteration, first, lambda x: {}),
                partial(get, item_code, default=[]),
                lambda x: get(x, prices, {}),
            )

        def fn(item):
            item_price = make_price(item.item_code)
            template_price = make_price(item.variant_of)
            sp = item_price(price_list) or template_price(price_list)
            ms1 = item_price("Minimum Selling") or template_price("Minimum Selling")
            ms2 = item_price("Minimum Selling 2") or template_price("Minimum Selling 2")
            return merge(
                item,
                {
                    "price_list_rate": get("price_list_rate", sp, 0),
                    "currency": get("currency", sp, 0),
                    "os_minimum_selling_rate": get("price_list_rate", ms1, 0),
                    "os_minimum_selling_2_rate": get("price_list_rate", ms2, 0),
                },
            )

        return fn

    make_item = compose(
        partial(
            pick,
            [
                "item_code",
                "item_name",
                "idx",
                "is_stock_item",
                "price_list_rate",
                "currency",
            ],
        ),
        add_price(prices),
    )

    return merge(
        {"items": map(make_item, items)},
        pick(["barcode", "serial_no", "batch_no"], search_data),
    )


def _get_conditions(args_dict):
    args = frappe._dict(args_dict)
    join_clauses = compose(lambda x: " AND ".join(x), concatv)

    lft, rgt = frappe.db.get_value("Item Group", args.item_group, ["lft", "rgt"])
    warehouse, display_items_in_stock = (
        frappe.db.get_value(
            "POS Profile", args.pos_profile, ["warehouse", "display_items_in_stock"]
        )
        if args.pos_profile
        else ("", 0)
    )
    profile_item_groups = get_item_groups(args.pos_profile)

    def make_stock_clause():
        if display_items_in_stock:
            sub_query = (
                """
                    SELECT
                        item_code,
                        actual_qty
                    FROM `tabBin`
                    WHERE
                        warehouse = %(warehouse)s AND
                        actual_qty > 0
                """
                if warehouse
                else """
                    SELECT
                        item_code,
                        SUM(actual_qty) AS actual_qty
                    FROM `tabBin`
                    GROUP BY item_code
                """
            )
            return """
                INNER JOIN ({sub_query}) AS b ON
                    b.item_code = i.name AND
                    b.actual_qty > 0
            """.format(
                sub_query=sub_query
            )
        return ""

    clauses = join_clauses(
        [
            "i.disabled = 0",
            "i.has_variants = 0",
            "i.is_sales_item = 1",
            "ig.lft >= {lft} AND ig.rgt <= {rgt}".format(lft=lft, rgt=rgt),
        ],
        ["i.name = %(item_code)s"] if args.item_code else [],
        ["(i.name LIKE %(free_text)s OR i.item_name LIKE %(free_text)s)"]
        if not args.item_code and args.search_value
        else [],
        ["i.item_group IN %(profile_item_groups)s"] if profile_item_groups else [],
    )
    values = merge(
        args,
        {
            "warehouse": warehouse,
            "profile_item_groups": profile_item_groups,
            "free_text": "%{}%".format(args.search_value),
        },
    )
    return {"clauses": clauses, "stock_clause": make_stock_clause()}, values


# TODO: when PR #18111 is merged
@frappe.whitelist()
def get_loyalty_program_details(
    customer,
    loyalty_program=None,
    expiry_date=None,
    company=None,
    silent=False,
    include_expired_entry=False,
):
    from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
        get_loyalty_program_details,
        get_loyalty_details,
    )

    program = get_loyalty_program_details(
        customer, loyalty_program, expiry_date, company, silent, include_expired_entry
    )
    points = get_loyalty_details(
        customer, program.loyalty_program, expiry_date, company, include_expired_entry
    )

    return merge(program, points)
