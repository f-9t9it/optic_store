# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, add_days
from functools import partial
from toolz import curry, unique, compose, merge, get, excepts

from optic_store.utils import sum_by, map_resolved


def process():
    alerts = frappe.get_single("Email Alerts")
    _document_expiry_reminder(alerts)
    _branch_sales_summary(alerts)


_get_recipients = compose(unique, partial(map, lambda x: x.user))


def _document_expiry_reminder(dx):
    if not dx.document_expiry_enabled:
        return

    end_date = add_days(getdate(), dx.document_expiry_days_till_expiry or 0)

    get_branch_records = _get_branch_records(end_date)
    get_emp_records = _get_emp_records(end_date)
    filter_empty = partial(filter, lambda x: x.get("data"))

    branch_docs = [
        {"label": "CR Expiry", "data": get_branch_records("os_cr_expiry")},
        {"label": "NHRA Expiry", "data": get_branch_records("os_nhra_expiry")},
    ]
    employee_docs = [
        {"label": "Passport Expiry", "data": get_emp_records("valid_upto")},
        {"label": "CPR Expiry", "data": get_emp_records("os_cpr_expiry")},
        {"label": "NHRA Expiry", "data": get_emp_records("os_nhra_expiry")},
    ]

    if not len(filter_empty(branch_docs + employee_docs)):
        return

    context = _make_document_expiry_context(
        branch_docs=filter_empty(branch_docs),
        employee_docs=filter_empty(employee_docs),
        days_till_expiry=dx.document_expiry_days_till_expiry or 0,
    )
    msg = frappe.render_template("templates/includes/document_expiry.html", context)

    for recipient in _get_recipients(dx.document_expiry_recipients):
        frappe.sendmail(
            recipients=recipient,
            subject=_("Document Expiry Reminder"),
            message=msg,
            reference_doctype="Email Alerts",
            unsubscribe_message=_("Unsubscribe from this Reminder"),
        )


def _make_document_expiry_context(branch_docs, employee_docs, days_till_expiry):
    subtitle = "Documents expiring in {} days or less".format(days_till_expiry)
    context = frappe._dict(
        branch_docs=branch_docs,
        employee_docs=employee_docs,
        company=frappe.defaults.get_global_default("company"),
        subtitle=subtitle,
    )
    frappe.new_doc("Email Digest").set_style(context)
    _set_other_styles(context)
    return context


def _set_other_styles(context):
    context.table = "width: 100%; margin-bottom: 1em;"
    context.caption = (
        "text-align: left; font-size: 1.2em; margin-bottom: 1em; line-height: 1;"
    )
    context.th = "color: #8D99A6; font-variant: all-small-caps;"
    context.td = "border-top: 1px solid #d1d8dd; padding: 5px 0;"


@curry
def _get_branch_records(end_date, fieldname):
    return frappe.db.sql(
        """
            SELECT branch_code, branch AS branch_name, {fieldname} AS expiry_date
            FROM `tabBranch`
            WHERE {fieldname} <= %(end_date)s
        """.format(
            fieldname=fieldname
        ),
        values={"end_date": end_date},
        as_dict=1,
    )


@curry
def _get_emp_records(end_date, fieldname):
    return frappe.db.sql(
        """
            SELECT name AS employee_id, employee_name, {fieldname} AS expiry_date
            FROM `tabEmployee`
            WHERE {fieldname} <= %(end_date)s
        """.format(
            fieldname=fieldname
        ),
        values={"end_date": end_date},
        as_dict=1,
    )


def _branch_sales_summary(bs):
    end_date = frappe.utils.getdate()
    payments = _get_payments(end_date)

    branch_collections = _get_branch_collections(payments, end_date)
    mop_collections = _get_mop_collections(payments, end_date)

    if not len(branch_collections + mop_collections):
        return

    context = _make_branch_sales_context(
        branch_collections=branch_collections, mop_collections=mop_collections
    )
    msg = frappe.render_template("templates/includes/daily_branch_sales.html", context)

    for recipient in _get_recipients(bs.branch_sales_recipients):
        frappe.sendmail(
            recipients=recipient,
            subject=_("Daily Sales Summary"),
            message=msg,
            reference_doctype="Email Alerts",
            unsubscribe_message=_("Unsubscribe from this Report"),
        )


def _make_branch_sales_context(branch_collections, mop_collections):
    subtitle = "Figures collected for today and the MTD"
    context = frappe._dict(
        branch_collections=branch_collections,
        mop_collections=mop_collections,
        company=frappe.defaults.get_global_default("company"),
        currency=frappe.defaults.get_global_default("currency"),
        subtitle=subtitle,
    )
    frappe.new_doc("Email Digest").set_style(context)
    _set_other_styles(context)
    return context


def _get_payments(end_date):
    return frappe.db.sql(
        """
            SELECT
                si.posting_date AS posting_date,
                si.os_branch AS branch,
                sip.mode_of_payment AS mode_of_payment,
                sip.base_amount AS amount
            FROM `tabSales Invoice` AS si
            RIGHT JOIN `tabSales Invoice Payment` AS sip ON
                sip.parent = si.name
            WHERE si.docstatus = 1 AND
                si.posting_date BETWEEN %(start_date)s AND %(end_date)s
            UNION ALL
            SELECT
                posting_date,
                os_branch AS branch,
                mode_of_payment,
                paid_amount AS amount
            FROM `tabPayment Entry`
            WHERE docstatus = 1 AND
                posting_date BETWEEN %(start_date)s AND %(end_date)s
        """,
        values={
            "start_date": frappe.utils.get_first_day(end_date),
            "end_date": end_date,
        },
        as_dict=1,
    )


def _get_branch_collections(payments, end_date):
    get_sum_today = compose(
        sum_by("amount"),
        lambda x: filter(
            lambda row: row.branch == x and row.posting_date == end_date, payments
        ),
        partial(get, "branch"),
    )
    get_sum_mtd = compose(
        sum_by("amount"),
        lambda x: filter(lambda row: row.branch == x, payments),
        partial(get, "branch"),
    )

    get_percent = excepts(ZeroDivisionError, lambda x, y: x / y * 100, lambda __: 0)

    def set_amounts(x):
        monthly_target = get("monthly_target", x, 0)
        collected_mtd = get_sum_mtd(x)
        return {
            "collected_today": get_sum_today(x),
            "half_monthly_target": monthly_target / 2,
            "half_monthly_target_percent": get_percent(
                collected_mtd, monthly_target / 2
            ),
            "collected_mtd": collected_mtd,
            "monthly_target_remaining": monthly_target - collected_mtd,
            "monthly_target_percent": get_percent(collected_mtd, monthly_target),
        }

    return map_resolved(
        lambda x: merge(x, set_amounts(x)),
        frappe.get_all(
            "Branch",
            fields=["name AS branch", "os_target AS monthly_target"],
            filters={"disabled": 0},
        ),
    )


def _get_mop_collections(payments, end_date):
    get_sum_today = compose(
        sum_by("amount"),
        lambda x: filter(
            lambda row: row.mode_of_payment == x and row.posting_date == end_date,
            payments,
        ),
        partial(get, "mop"),
    )
    get_sum_mtd = compose(
        sum_by("amount"),
        lambda x: filter(lambda row: row.mode_of_payment == x, payments),
        partial(get, "mop"),
    )
    return map_resolved(
        lambda x: merge(
            x, {"collected_today": get_sum_today(x), "collected_mtd": get_sum_mtd(x)}
        ),
        frappe.get_all("Mode of Payment", fields=["name AS mop"]),
    )
