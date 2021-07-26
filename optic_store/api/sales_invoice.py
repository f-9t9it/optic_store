# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import nowdate, nowtime, cint
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from erpnext.selling.page.point_of_sale.point_of_sale import (
    search_serial_or_batch_or_barcode_number as search_item,
)
from six import string_types
from functools import partial, reduce
from toolz import compose, unique, pluck, concat, merge, excepts, groupby, valmap, first

from optic_store.utils import sum_by, pick, mapf, filterf
from optic_store.api.loyalty_program import get_customer_loyalty_details

_filter_batch_items = partial(
    filter, lambda x: frappe.db.get_value("Item", x.item_code, "has_batch_no")
)


@frappe.whitelist()
def get_state_to_complete(doctype):
    workflow_name = frappe.model.meta.get_workflow_name(doctype)
    return frappe.db.get_value(
        "Workflow Transition",
        filters={"parent": workflow_name, "action": "Complete"},
        fieldname="state",
        order_by="idx desc",
    )


@frappe.whitelist()
def deliver_qol(name, payments=[], batches=None, deliver=0):

    is_delivery = cint(deliver)

    si = frappe.get_doc("Sales Invoice", name)
    _validate_workflow()
    if is_delivery:
        _validate_qol(batches, si)

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

    make_payments = compose(partial(mapf, make_payment), json.loads)
    pe_names = make_payments(payments) if payments else []

    result = {"payment_entries": pe_names}
    if is_delivery:
        dn = make_delivery_note(name)
        dn.os_branch = si.os_branch
        warehouse = (
            frappe.db.get_value("Branch", si.os_branch, "warehouse")
            if si.os_branch
            else None
        )
        if batches:
            get_batches = compose(unique, partial(pluck, "item_code"), json.loads)
            batch_items = filterf(
                lambda x: x.item_code in get_batches(batches), dn.items
            )

            def get_item(field, value):
                return compose(
                    lambda x: x.as_dict() if x else {},
                    excepts(StopIteration, first, lambda x: None),
                    partial(filter, lambda x: x.get(field) == value),
                )(batch_items)

            dn.items = filterf(lambda x: x not in batch_items, dn.items)
            for batch in json.loads(batches):
                si_detail = batch.get("si_detail")
                item = merge(
                    (
                        get_item("si_detail", si_detail)
                        or get_item("batch_no", batch.get("batch_no"))
                        or get_item("item_code", batch.get("item_code"))
                    ),
                    pick(
                        ["item_code", "batch_no", "qty"],
                        batch,
                    ),
                    {"si_detail": si_detail} if si_detail else {},
                )
                dn.append("items", item)
        if warehouse:
            for item in dn.items:
                item.warehouse = warehouse
        dn.insert(ignore_permissions=True)
        dn.submit()
        result = merge(result, {"delivery_note": dn.name})

    return result


def _validate_workflow():
    if not get_state_to_complete("Sales Order"):
        frappe.throw(
            frappe._(
                "Operation not permitted because either Sales Order workflow is not "
                "configured or incompatible"
            )
        )


def _validate_qol(batches, si):
    state_to_complete = get_state_to_complete("Sales Order")

    def si_deliverable(items):
        return sum_by("qty")(items) > sum_by("delivered_qty")(items)

    def invalid_batch_qtys(items):
        get_qtys = compose(
            partial(valmap, sum_by("qty")), partial(groupby, "item_code")
        )
        get_si_items = compose(
            get_qtys, partial(map, lambda x: x.as_dict()), _filter_batch_items
        )
        get_batch_items = compose(get_qtys, json.loads)
        return get_si_items(items) != get_batch_items(batches)

    sos_deliverable = compose(
        lambda states: reduce(lambda a, x: a and x == state_to_complete, states, True),
        partial(map, lambda x: frappe.db.get_value("Sales Order", x, "workflow_state")),
        unique,
        partial(filter, lambda x: x),
        partial(map, lambda x: x.sales_order),
    )

    if si.update_stock or not si_deliverable(si.items):
        frappe.throw(_("Delivery has already been processed"))
    if not sos_deliverable(si.items):
        frappe.throw(
            _(
                "Cannot make delivery until Sales Order status is '{}'".format(
                    state_to_complete
                )
            )
        )
    if batches and invalid_batch_qtys(si.items):
        frappe.throw(_("Mismatched Items and Batches"))


def _make_payment_entry(name, mode_of_payment, paid_amount, gift_card_no):
    if not mode_of_payment:
        frappe.throw(_("Mode of Payment is required"))
    si = frappe.get_doc("Sales Invoice", name)
    payment_account = _get_account(mode_of_payment, si.company)
    pe = frappe.new_doc("Payment Entry")
    is_same_currency = si.party_account_currency == payment_account.account_currency
    pe.update(
        {
            "payment_type": "Receive",
            "company": si.company,
            "os_branch": si.os_branch,
            "posting_date": nowdate(),
            "os_posting_time": nowtime(),
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
    if doc.doctype == "Sales Invoice":
        sales_orders = _get_sales_orders(doc.name)
        so_payments = get_payments_against("Sales Order", sales_orders)
        si_payments = get_payments_against("Sales Invoice", [doc.name])
        self_payments = _get_si_self_payments(doc)
        return so_payments + si_payments + self_payments
    if doc.doctype == "Sales Order":
        so_payments = get_payments_against("Sales Order", [doc.name])
        sales_invoices = _get_sales_invoices(doc.name)
        si_payments = get_payments_against("Sales Invoice", sales_invoices)

        get_si_self_payment = compose(
            _get_si_self_payments, partial(frappe.get_doc, "Sales Invoice")
        )
        si_self_payments = compose(list, concat, partial(map, get_si_self_payment))(
            sales_invoices
        )
        return so_payments + si_payments + si_self_payments
    return []


def _get_sales_orders(sales_invoice):
    doc = frappe.get_doc("Sales Invoice", sales_invoice)
    get_so_names = compose(
        list,
        unique,
        partial(filter, lambda x: x),
        partial(map, lambda x: x.sales_order),
    )
    return get_so_names(doc.items)


def _get_sales_invoices(sales_order):
    q = frappe.db.sql(
        """
            SELECT sii.parent AS name
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN `tabSales Invoice` AS si ON sii.parent = si.name
            WHERE
                si.docstatus = 1 AND
                si.is_return = 0 AND
                sii.sales_order = %(sales_order)s
        """,
        values={"sales_order": sales_order},
        as_dict=1,
    )
    get_si_names = compose(list, unique, partial(pluck, "name"))
    return get_si_names(q)


def get_payments_against(doctype, names):
    if not names:
        return []
    return frappe.db.sql(
        """
            SELECT
                pe.name AS payment_name,
                'Payment Entry' AS payment_doctype,
                pe.posting_date AS posting_date,
                pe.mode_of_payment AS mode_of_payment,
                per.reference_doctype AS reference_doctype,
                per.reference_name AS reference_name,
                SUM(per.allocated_amount) AS paid_amount
            FROM `tabPayment Entry Reference` AS per
            LEFT JOIN `tabPayment Entry` AS pe ON
                per.parent = pe.name
            WHERE
                pe.docstatus = 1 AND
                per.reference_doctype = %(doctype)s AND
                per.reference_name IN %(names)s
            GROUP BY pe.name
        """,
        values={"doctype": doctype, "names": list(names)},
        as_dict=1,
    )


def _get_si_self_payments(doc):
    return filterf(
        lambda x: x.get("paid_amount"),
        concat(
            [
                [
                    {
                        "payment_name": doc.name,
                        "payment_doctype": doc.doctype,
                        "posting_date": doc.posting_date,
                        "mode_of_payment": "Loyalty Program",
                        "paid_amount": doc.loyalty_amount,
                    }
                ],
                map(
                    lambda x: {
                        "payment_name": doc.name,
                        "payment_doctype": doc.doctype,
                        "posting_date": doc.posting_date,
                        "mode_of_payment": x.mode_of_payment,
                        "paid_amount": x.amount,
                    },
                    doc.payments,
                ),
            ]
        ),
    )


def get_ref_so_date(sales_invoice):
    get_transaction_dates = compose(
        excepts(ValueError, min, lambda x: None),
        partial(
            map, lambda x: frappe.db.get_value("Sales Order", x, "transaction_date")
        ),
        _get_sales_orders,
    )
    return get_transaction_dates(sales_invoice)


@frappe.whitelist()
def get_ref_so_statuses(sales_invoice):
    _validate_workflow()
    get_statuses = compose(
        partial(
            mapf, lambda x: frappe.db.get_value("Sales Order", x, "workflow_state")
        ),
        _get_sales_orders,
    )
    print(get_statuses(sales_invoice))
    return get_statuses(sales_invoice)


@frappe.whitelist()
def validate_loyalty(doc):
    def get_dict(obj):
        if isinstance(obj, frappe.model.document.Document):
            return obj.as_dict()
        if isinstance(obj, string_types):
            return json.loads(obj)
        if isinstance(obj, dict):
            return obj
        return {}

    code = frappe.db.get_single_value("Optical Store Settings", "loyalty_validation")
    locals = frappe._dict(pick(["loyalty_points"], get_dict(doc)))
    if code and not frappe.safe_eval(code, eval_locals=locals):
        frappe.throw(
            _(
                "Loyalty validation failed."
                "Please correct loyalty fields or contact System Manager."
            )
        )


def write_off_expired_credit_notes():
    credit_note_expiry = frappe.db.get_single_value(
        "Optic Store Selling Settings", "credit_note_expiry"
    )
    if not credit_note_expiry:
        return

    posting_date = frappe.utils.today()

    expired_credit_notes = frappe.db.sql(
        """
            SELECT name, company, cost_center, debit_to, outstanding_amount
            FROM `tabSales Invoice`
            WHERE
                status = 'Credit Note Issued' AND
                outstanding_amount < 0 AND
                posting_date < %(posting_date)s
            ORDER BY posting_date
        """,
        values={
            "posting_date": frappe.utils.add_days(posting_date, -credit_note_expiry)
        },
        as_dict=1,
    )

    for credit_note in expired_credit_notes:
        _make_je(credit_note, posting_date)


def _make_je(credit_note, posting_date):
    company = credit_note.get("company")
    wo_account = frappe.db.get_value(
        "Company", company, "write_off_account"
    ) or frappe.db.exists("Account", {"company": company, "account_name": "Write Off"})
    cost_center = credit_note.get("cost_center") or frappe.db.get_value(
        "Company", company, "cost_center"
    )

    outstanding_amount = credit_note.get("outstanding_amount")
    je = frappe.get_doc(
        {
            "doctype": "Journal Entry",
            "voucher_type": "Write Off Entry",
            "posting_date": posting_date,
            "company": company,
            "accounts": [
                {
                    "account": wo_account,
                    "cost_center": cost_center,
                    "credit": outstanding_amount,
                },
                {
                    "account": credit_note.get("debit_to"),
                    "debit": outstanding_amount,
                    "reference_type": "Sales Invoice",
                    "reference_name": credit_note.get("name"),
                },
            ],
        }
    )
    je.insert()
    je.submit()


def get_credit_notes(customer):
    expiry_days = frappe.utils.cint(
        frappe.db.get_single_value(
            "Optical Store Selling Settings", "credit_note_expiry"
        )
    )

    def make_line(invoice):
        return merge(
            pick(["name"], invoice),
            {
                "amount": -invoice.get("outstanding_amount"),
                "expiry_date": frappe.utils.add_days(
                    invoice.get("posting_date"), expiry_days
                )
                if expiry_days
                else None,
            },
        )

    return [
        make_line(x)
        for x in frappe.get_all(
            "Sales Invoice",
            filters={"status": "Credit Note Issued", "customer": customer},
            fields=["name", "outstanding_amount", "posting_date"],
        )
    ]


def get_loyalty_points_earned(sales_invoice):
    loyalty_point_entry = frappe.get_all(
        "Loyalty Point Entry",
        filters={"sales_invoice": sales_invoice, "redeem_against": ""},
        fields=["loyalty_points"],
    )
    return (
        first(loyalty_point_entry).get("loyalty_points")
        if loyalty_point_entry
        else 0.00
    )
