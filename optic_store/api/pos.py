# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.utils import today
from erpnext.stock.get_item_details import get_pos_profile
from erpnext.accounts.doctype.sales_invoice.pos import get_customers_list
from erpnext.accounts.doctype.sales_invoice.pos import (
    make_invoice as erpnext_make_invoice,
    get_customer_id,
)
from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_details
from functools import partial
from toolz import pluck, compose, valfilter, valmap, merge

from optic_store.api.group_discount import get_brand_discounts
from optic_store.api.customer import CUSTOMER_DETAILS_FIELDS
from optic_store.utils import pick


@frappe.whitelist()
def get_extended_pos_data(company):
    pos_profile = get_pos_profile(company)
    query_date = today()
    return {
        "sales_persons": _get_sales_persons(),
        "group_discounts": get_brand_discounts(),
        "customers_details": _get_customers_details(pos_profile, query_date),
        "loyalty_programs": _get_loyalty_programs(company),
        "gift_cards": _get_gift_cards(query_date),
        "territories": _get_territories(),
        "customer_groups": _get_customer_groups(),
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
            SELECT name, os_loyalty_card_no, loyalty_program, {customer_details_fields}
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

@frappe.whitelist()
def make_invoice(doc_list={}, email_queue_list={}, customers_list={}):
    result = erpnext_make_invoice(doc_list, email_queue_list, customers_list)
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
