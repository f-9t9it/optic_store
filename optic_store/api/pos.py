# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import today
from erpnext.stock.get_item_details import get_pos_profile
from erpnext.accounts.doctype.sales_invoice.pos import get_customers_list
from erpnext.accounts.doctype.sales_invoice.pos import get_customer_id
from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_details
from functools import partial
from toolz import pluck, compose, valfilter, valmap, merge, get, groupby, flip

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
    start, page_length, price_list, item_group, search_value="", pos_profile=None
):
    from erpnext.selling.page.point_of_sale.point_of_sale import get_items

    result = get_items(
        start, page_length, price_list, item_group, search_value="", pos_profile=None
    )

    get_prices = compose(_get_item_prices, list, partial(pluck, "item_code"))

    items = get("items", result, [])
    prices = get_prices(items)

    def add_price(item):
        item_code = get("item_code", item)
        rates = get(item_code, prices)
        return merge(item, rates) if rates else item

    return merge(result, {"items": map(add_price, items)})
