# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from operator import neg
import frappe
from frappe.model.document import Document
from frappe.utils import now, flt
from functools import partial
from toolz import compose, excepts, first, get, unique, pluck

from optic_store.api.customer import get_user_branch
from optic_store.utils import pick, sum_by


class XZReport(Document):
    def validate(self):
        existing = frappe.db.sql(
            """
                    SELECT 1 FROM `tabXZ Report`
                    WHERE
                        docstatus = 1 AND
                        name != %(name)s AND
                        company = %(company)s AND
                        pos_profile = %(pos_profile)s AND
                        user = %(user)s AND
                        start_time <= %(end_time)s AND
                        end_time >= %(start_time)s
                """,
            values={
                "name": self.name,
                "company": self.company,
                "pos_profile": self.pos_profile,
                "user": self.user,
                "start_time": self.start_time or now(),
                "end_time": self.end_time or now(),
            },
        )
        if existing:
            frappe.throw("Another XZ Report already exists during this time frame.")

    def before_insert(self):
        if not self.branch:
            self.branch = get_user_branch()

    def before_save(self):
        self.expected_cash = (
            flt(self.opening_cash)
            + flt(self.cash_sales)
            + flt(self.cash_returns)
            + flt(self.cash_pe_received)
        )
        self.difference_cash = self.expected_cash - flt(self.closing_cash)

    def set_report_details(self):
        args = pick(
            ["user", "pos_profile", "company", "start_time", "end_time"], self.as_dict()
        )

        sales, returns = _get_invoices(args)
        sales_payments, returns_payments, collection_payments = _get_payments(args)
        taxes = _get_taxes(args)

        make_invoice = partial(
            pick, ["invoice", "total_qty", "grand_total", "paid_amount"]
        )
        make_payment = partial(pick, ["mode_of_payment", "amount"])
        make_tax = partial(pick, ["rate", "tax_amount"])
        mops = compose(unique, partial(pluck, "mode_of_payment"))

        def get_mop_amount(mode_of_payment, payments=[]):
            return compose(
                partial(get, "amount"),
                excepts(StopIteration, first, lambda x: {"amount": 0}),
                partial(filter, lambda x: x.get("mode_of_payment") == mode_of_payment),
            )(payments)

        get_cash = partial(get_mop_amount, "Cash")
        get_sales_amount = partial(get_mop_amount, payments=sales_payments)
        get_returns_amount = partial(get_mop_amount, payments=returns_payments)
        get_collection_amount = partial(get_mop_amount, payments=collection_payments)

        def make_payment(mode_of_payment):
            sales_amount = get_sales_amount(mode_of_payment)
            returns_amount = get_returns_amount(mode_of_payment)
            collection_amount = get_collection_amount(mode_of_payment)
            return {
                "mode_of_payment": mode_of_payment,
                "sales_amount": sales_amount,
                "returns_amount": returns_amount,
                "collection_amount": collection_amount,
                "total_amount": sales_amount + returns_amount + collection_amount,
            }

        sum_by_total = sum_by("total")
        sum_by_net = sum_by("net_total")
        sum_by_discount = compose(neg, sum_by("discount_amount"))
        sum_by_taxes = sum_by("tax_amount")
        sum_by_grand = sum_by("grand_total")

        self.cash_sales = get_cash(sales_payments)
        self.cash_returns = get_cash(returns_payments)
        self.cash_pe_received = get_cash(collection_payments)
        self.sales__total = sum_by_total(sales) - sum_by_total(returns)
        self.total__discount_amount = sum_by_discount(sales) + sum_by_discount(returns)
        self.returns__net_total = sum_by_net(returns)
        self.total__net_total = sum_by_net(sales + returns)
        self.total__total_taxes_and_charges = sum_by_taxes(taxes)
        self.total__grand_total = sum_by_grand(sales) + sum_by_grand(returns)

        self.sales = []
        for invoice in sales:
            self.append("sales", make_invoice(invoice))
        self.returns = []
        for invoice in returns:
            self.append("returns", make_invoice(invoice))
        self.payments = []
        for payment in mops(sales_payments + returns_payments + collection_payments):
            self.append("payments", make_payment(payment))
        self.taxes = []
        for tax in taxes:
            self.append("taxes", make_tax(tax))


def _get_invoices(args):
    sales = frappe.db.sql(
        """
            SELECT
                name AS invoice,
                pos_total_qty AS total_qty,
                base_total AS total,
                base_grand_total AS grand_total,
                base_net_total AS net_total,
                base_discount_amount AS discount_amount,
                outstanding_amount,
                paid_amount
            FROM `tabSales Invoice`
            WHERE docstatus = 1 AND
                is_pos = 1 AND
                is_return != 1 AND
                pos_profile = %(pos_profile)s AND
                company = %(company)s AND
                owner = %(user)s AND
                TIMESTAMP(posting_date, posting_time)
                    BETWEEN %(start_time)s AND %(end_time)s
        """,
        values=args,
        as_dict=1,
    )
    returns = frappe.db.sql(
        """
            SELECT
                name AS invoice,
                pos_total_qty AS total_qty,
                base_total AS total,
                base_grand_total AS grand_total,
                base_net_total AS net_total,
                base_discount_amount AS discount_amount,
                paid_amount
            FROM `tabSales Invoice`
            WHERE docstatus = 1 AND
                is_return = 1 AND
                company = %(company)s AND
                owner = %(user)s AND
                TIMESTAMP(posting_date, posting_time)
                    BETWEEN %(start_time)s AND %(end_time)s
        """,
        values=args,
        as_dict=1,
    )
    return sales, returns


def _get_payments(args):
    sales_payments = frappe.db.sql(
        """
            SELECT
                sip.mode_of_payment AS mode_of_payment,
                SUM(sip.base_amount) AS amount
            FROM `tabSales Invoice Payment` AS sip
            LEFT JOIN `tabSales Invoice` AS si ON
                sip.parent = si.name
            WHERE si.docstatus = 1 AND
                si.is_pos = 1 AND
                si.is_return != 1 AND
                si.company = %(company)s AND
                si.owner = %(user)s AND
                TIMESTAMP(si.posting_date, si.posting_time)
                    BETWEEN %(start_time)s AND %(end_time)s
            GROUP BY sip.mode_of_payment
        """,
        values=args,
        as_dict=1,
    )
    returns_payments = frappe.db.sql(
        """
            SELECT
                sip.mode_of_payment AS mode_of_payment,
                SUM(sip.base_amount) AS amount
            FROM `tabSales Invoice Payment` AS sip
            LEFT JOIN `tabSales Invoice` AS si ON
                sip.parent = si.name
            WHERE si.docstatus = 1 AND
                si.is_return = 1 AND
                si.company = %(company)s AND
                si.owner = %(user)s AND
                TIMESTAMP(si.posting_date, si.posting_time)
                    BETWEEN %(start_time)s AND %(end_time)s
            GROUP BY sip.mode_of_payment
        """,
        values=args,
        as_dict=1,
    )
    collection_payments = frappe.db.sql(
        """
            SELECT
                mode_of_payment AS mode_of_payment,
                SUM(paid_amount) AS amount
            FROM `tabPayment Entry`
            WHERE docstatus = 1 AND
                company = %(company)s AND
                owner = %(user)s AND
                creation BETWEEN %(start_time)s AND %(end_time)s
            GROUP BY mode_of_payment
        """,
        values=args,
        as_dict=1,
    )
    return sales_payments, returns_payments, collection_payments


def _get_taxes(args):
    taxes = frappe.db.sql(
        """
            SELECT
                stc.rate AS mode_of_payment,
                SUM(stc.base_tax_amount_after_discount_amount) AS tax_amount
            FROM `tabSales Taxes and Charges` AS stc
            LEFT JOIN `tabSales Invoice` AS si ON
                stc.parent = si.name
            WHERE si.docstatus = 1 AND
                si.is_pos = 1 AND
                si.company = %(company)s AND
                si.owner = %(user)s AND
                TIMESTAMP(si.posting_date, si.posting_time)
                    BETWEEN %(start_time)s AND %(end_time)s
            GROUP BY stc.rate
        """,
        values=args,
        as_dict=1,
    )
    return taxes
