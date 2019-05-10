# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.utils import nowdate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from erpnext.selling.page.point_of_sale.point_of_sale import (
    search_serial_or_batch_or_barcode_number as search_item,
)
from functools import partial
from toolz import compose, excepts, first, unique


@frappe.whitelist()
def payment_qol(name, payments):
    def make_payment(payment):
        pe = _make_payment_entry(
            name,
            payment.get("mode_of_payment"),
            payment.get("amount"),
            payment.get("gift_card_no"),
        )
        pe.insert(ignore_permissions=True)
        pe.submit()
        pe.name

    make_payments = compose(partial(map, make_payment), json.loads)
    return make_payments(payments)


@frappe.whitelist()
def deliver_qol(name):
    si = frappe.get_doc("Sales Invoice", name)
    dn = make_delivery_note(name)
    dn.os_branch = si.os_branch
    warehouse = (
        frappe.db.get_value("Branch", si.os_branch, "warehouse")
        if si.os_branch
        else None
    )
    if warehouse:
        for item in dn.items:
            item.warehouse = warehouse
    dn.insert(ignore_permissions=True)
    dn.submit()

    return dn.name


def _make_payment_entry(name, mode_of_payment, paid_amount, gift_card_no):
    si = frappe.get_doc("Sales Invoice", name)
    payment_account = _get_account(mode_of_payment, si.company)
    pe = frappe.new_doc("Payment Entry")
    is_same_currency = si.party_account_currency == payment_account.account_currency
    pe.update(
        {
            "payment_type": "Receive",
            "company": si.company,
            "posting_date": nowdate(),
            "mode_of_payment": mode_of_payment,
            "os_gift_card": gift_card_no,
            "party_type": "Customer",
            "party": si.customer,
            "paid_from": si.debit_to,
            "paid_to": payment_account.name,
            "paid_from_account_currency": si.party_account_currency,
            "paid_to_account_currency": payment_account.account_currency,
            "paid_amount": paid_amount,
            "received_amount": paid_amount if is_same_currency else 0,
            "allocate_payment_amount": 1,
            "letter_head": si.get("letter_head"),
        }
    )
    pe.append(
        "references",
        {
            "reference_doctype": "Sales Invoice",
            "reference_name": name,
            "bill_no": si.get("bill_no"),
            "due_date": si.get("due_date"),
            "total_amount": (si.base_rounded_total or si.base_grand_total)
            if is_same_currency
            else (si.rounded_total or si.grand_total),
            "outstanding_amount": si.outstanding_amount,
            "allocated_amount": paid_amount,
        },
    )
    pe.setup_party_account_field()
    pe.set_missing_values()
    return pe


def _get_account(mode_of_payment, company):
    mopa = frappe.db.exists(
        "Mode of Payment Account", {"parent": mode_of_payment, "company": company}
    )
    if not mopa:
        return None
    account = frappe.db.get_value("Mode of Payment Account", mopa, "default_account")
    return frappe.get_doc("Account", account) if account else None


@frappe.whitelist()
def search_serial_or_batch_or_barcode_number(search_value):
    return (
        frappe.db.get_value("Item", search_value, ["name as item_code"], as_dict=True)
        or search_item(search_value)
        or None
    )


def get_payments(doc):
    sales_order = _get_sales_order(doc.name)
    so_payments = (
        _get_payments_against("Sales Order", sales_order.name) if sales_order else []
    )
    si_payments = _get_payments_against("Sales Invoice", doc.name)
    self_payments = map(
        lambda x: {
            "payment_entry": None,
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "paid_amount": x.amount,
        },
        doc.payments,
    )
    return so_payments + si_payments + self_payments


# this does not handle cases where one Sales Invoice could reference more than one
# Sales Order
def _get_sales_order(sales_invoice):
    doc = frappe.get_doc("Sales Invoice", sales_invoice)
    if not doc:
        return None
    so = compose(
        excepts(StopIteration, first, lambda x: None),
        unique,
        partial(map, lambda x: x.sales_order),
    )(doc.items)
    return frappe.get_doc("Sales Order", so) if so else None


def _get_payments_against(doctype, name):
    return frappe.db.sql(
        """
            SELECT
                pe.name AS payment_entry,
                per.reference_doctype AS reference_doctype,
                per.reference_name AS reference_name2,
                SUM(per.allocated_amount) AS paid_amount
            FROM `tabPayment Entry Reference` AS per
            LEFT JOIN `tabPayment Entry` AS pe ON
                per.parent = pe.name
            WHERE
                per.reference_doctype = %(doctype)s AND
                per.reference_name = %(name)s
            GROUP BY pe.name
        """,
        values={"doctype": doctype, "name": name},
        as_dict=1,
    )


def get_ref_so_date(sales_invoice):
    so = _get_sales_order(sales_invoice)
    return so.transaction_date if so else None
