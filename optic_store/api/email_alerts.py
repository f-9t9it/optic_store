# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, add_days
from functools import partial
from toolz import curry


def process():
    alerts = frappe.get_single("Email Alerts")
    _document_expiry_reminder(alerts)


def _document_expiry_reminder(dx):
    if dx.document_expiry_disabled:
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

    for recipient in map(lambda x: x.user, dx.document_expiry_recipients):
        frappe.sendmail(
            recipients=recipient,
            subject=_("Document Expiry Reminder"),
            message=msg,
            reference_doctype="Document Expiry Reminder",
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
    context.table = "width: 100%; margin-bottom: 1em;"
    context.caption = (
        "text-align: left; font-size: 1.2em; margin-bottom: 1em; line-height: 1;"
    )
    context.th = "color: #8D99A6; font-variant: all-small-caps;"
    context.td = "border-top: 1px solid #d1d8dd; padding: 5px 0;"
    return context


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
