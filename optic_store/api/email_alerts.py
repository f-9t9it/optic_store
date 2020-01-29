# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import math
import frappe
from frappe import _
from frappe.utils import getdate, add_days, get_datetime, datetime
from functools import partial
from toolz import curry, unique, compose, merge, get

from optic_store.utils import sum_by, mapf, filterf


def process():
    alerts = frappe.get_single("Email Alerts")
    _document_expiry_reminder(alerts)
    _branch_sales_summary(alerts)


_get_recipients = compose(unique, partial(map, lambda x: x.user))


def _get_send_after(mins):
    if not mins:
        return None
    return get_datetime() + datetime.timedelta(minutes=mins)


def _document_expiry_reminder(dx):
    if not dx.document_expiry_enabled:
        return

    end_date = add_days(getdate(), dx.document_expiry_days_till_expiry or 0)

    get_branch_records = _get_branch_records(end_date)
    get_emp_records = _get_emp_records(end_date)
    filter_empty = partial(filterf, lambda x: x.get("data"))

    branch_docs = [
        {"label": "CR", "data": get_branch_records("os_cr_no", "os_cr_expiry")},
        {
            "label": "Shop NHRA License",
            "data": get_branch_records("os_nhra_license", "os_nhra_expiry"),
        },
    ]
    employee_docs = [
        {"label": "CPR", "data": get_emp_records("os_cpr_expiry")},
        {"label": "Passport", "data": get_emp_records("valid_upto")},
        {"label": "Employee NHRA License", "data": get_emp_records("os_nhra_expiry")},
        {"label": "Staff Contract", "data": get_emp_records("contract_end_date")},
        {"label": "Staff Resident Permit", "data": get_emp_records("os_rp_expiry")},
    ]

    if not len(filter_empty(branch_docs + employee_docs)):
        return

    context = _make_document_expiry_context(
        branch_docs=filter_empty(branch_docs),
        employee_docs=filter_empty(employee_docs),
        days_till_expiry=dx.document_expiry_days_till_expiry or 0,
    )
    msg = frappe.render_template("templates/includes/document_expiry.html.j2", context)

    for recipient in _get_recipients(dx.document_expiry_recipients):
        frappe.sendmail(
            recipients=recipient,
            subject=_("Document Expiry Reminder"),
            message=msg,
            reference_doctype="Email Alerts",
            reference_name="Email Alerts",
            unsubscribe_message=_("Unsubscribe from this Reminder"),
            send_after=_get_send_after(dx.send_after_mins),
        )


def _make_document_expiry_context(branch_docs, employee_docs, days_till_expiry):
    subtitle = "Within {} days or less".format(days_till_expiry)
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
    context.table = "width: 100%; border-collapse: collapse;"
    context.caption = "text-align: center; font-weight: bold; margin: 1em 0;"
    context.th = (
        "text-align: center; background-color: #c4bd97; border: 1px solid black;"
    )
    context.td = "border: 1px solid black;"
    context.tdfoot = "font-weight: bold; border: 1px solid black;"


@curry
def _get_branch_records(end_date, param_field, expiry_field):
    return frappe.db.sql(
        """
            SELECT
                branch_code,
                branch AS branch_name,
                {param_field} AS param,
                {expiry_field} AS expiry_date
            FROM `tabBranch`
            WHERE disabled = 0 AND {expiry_field} <= %(end_date)s
        """.format(
            param_field=param_field, expiry_field=expiry_field
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
            WHERE status = 'Active' AND {fieldname} <= %(end_date)s
        """.format(
            fieldname=fieldname
        ),
        values={"end_date": end_date},
        as_dict=1,
    )


def _branch_sales_summary(bs):
    yesterday = frappe.utils.add_days(frappe.utils.getdate(), -1)
    payments = _get_payments(yesterday)

    branch_collections = _get_branch_collections(payments, yesterday, bs)

    filter_zero = compose(list, partial(filter, lambda x: x.get("collected_today")))
    mop_collections = filter_zero(_get_mop_collections(payments, yesterday))

    if not len(branch_collections + mop_collections):
        return

    context = _make_branch_sales_context(
        bs,
        branch_collections=branch_collections,
        mop_collections=mop_collections,
        grouped_mop_collections=filter_zero(
            _get_grouped_mop_collections(payments, yesterday)
        ),
    )
    msg = frappe.render_template(
        "templates/includes/daily_branch_sales.html.j2", context
    )

    for recipient in _get_recipients(bs.branch_sales_recipients):
        frappe.sendmail(
            recipients=recipient,
            subject=_("Daily Sales Summary"),
            message=msg,
            reference_doctype="Email Alerts",
            reference_name="Email Alerts",
            unsubscribe_message=_("Unsubscribe from this Report"),
            send_after=_get_send_after(bs.send_after_mins),
        )


def _make_branch_sales_context(
    settings, branch_collections, mop_collections, grouped_mop_collections
):
    context = frappe._dict(
        branch_collections=branch_collections,
        mop_collections=mop_collections,
        grouped_mop_collections=grouped_mop_collections,
        company=frappe.defaults.get_global_default("company"),
        currency=frappe.defaults.get_global_default("currency"),
        show_quarter=settings.show_quarter,
        show_half_year=settings.show_half_year,
        show_year=settings.show_year,
    )
    frappe.new_doc("Email Digest").set_style(context)
    _set_other_styles(context)
    return context


def _get_payments(yesterday):
    start_date, end_date = _get_year_dates(yesterday)
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
        values={"start_date": start_date, "end_date": end_date},
        as_dict=1,
    )


def _get_year_dates(date):
    return date.replace(month=1, day=1), date.replace(month=12, day=31)


def _get_half_year_dates(date):
    if date.month > 6:
        return date.replace(month=7, day=1), date.replace(month=12, day=31)
    return date.replace(month=1, day=1), date.replace(month=6, day=30)


def _get_quarter_dates(date):
    if date.month > 9:
        return date.replace(month=10, day=1), date.replace(month=12, day=31)
    if date.month > 6:
        return date.replace(month=7, day=1), date.replace(month=9, day=30)
    if date.month > 3:
        return date.replace(month=4, day=1), date.replace(month=6, day=30)
    return date.replace(month=1, day=1), date.replace(month=3, day=31)


def _get_month_dates(date):
    return frappe.utils.get_first_day(date), frappe.utils.get_last_day(date)


def _get_half_month_dates(date):
    half_day = compose(int, math.ceil, lambda x: x / 2)
    return (
        frappe.utils.get_first_day(date),
        date.replace(day=half_day(frappe.utils.get_last_day(date).day)),
    )


def _get_branch_collections(payments, yesterday, settings):
    def make_aggregator(start, end):
        return compose(
            sum_by("amount"),
            lambda x: filter(
                lambda row: row.branch == x and (start <= row.posting_date <= end),
                payments,
            ),
            partial(get, "branch"),
        )

    sum_today = make_aggregator(yesterday, yesterday)
    sum_half_month = make_aggregator(*_get_half_month_dates(yesterday))
    sum_month = make_aggregator(*_get_month_dates(yesterday))
    sum_quarter = make_aggregator(*_get_quarter_dates(yesterday))
    sum_half_year = make_aggregator(*_get_half_year_dates(yesterday))
    sum_year = make_aggregator(*_get_year_dates(yesterday))

    def set_amounts(x):
        collected_mtd = sum_month(x)
        return merge(
            {
                "collected_today": sum_today(x),
                "half_monthly_sales": sum_half_month(x),
                "collected_mtd": collected_mtd,
                "monthly_target_remaining": get("monthly_target", x, 0) - collected_mtd,
            },
            {"quarterly_sales": sum_quarter(x)} if settings.show_quarter else {},
            {"half_yearly_sales": sum_half_year(x)} if settings.show_half_year else {},
            {"yearly_sales": sum_year(x)} if settings.show_year else {},
        )

    return mapf(
        lambda x: merge(x, set_amounts(x)),
        frappe.get_all(
            "Branch",
            fields=[
                "name AS branch",
                "os_half_monthly_target AS half_monthly_target",
                "os_target AS monthly_target",
                "os_quarterly_target AS quarterly_target",
                "os_half_yearly_target AS half_yearly_target",
                "os_yearly_target AS yearly_target",
            ],
            filters=[["name", "in", (settings.branches_to_show or "").split("\n")]],
        ),
    )


def _get_mop_collections(payments, yesterday):
    get_sum_today = compose(
        sum_by("amount"),
        lambda x: filter(
            lambda row: row.mode_of_payment == x and row.posting_date == yesterday,
            payments,
        ),
        partial(get, "mop"),
    )
    return mapf(
        lambda x: merge(x, {"collected_today": get_sum_today(x)}),
        frappe.get_all("Mode of Payment", fields=["name AS mop"]),
    )


def _get_grouped_mop_collections(payments, yesterday):
    get_sum_today = compose(
        sum_by("amount"),
        lambda x: filter(
            lambda row: row.mode_of_payment in x and row.posting_date == yesterday,
            payments,
        ),
        lambda x: x.split("\n"),
        partial(get, "mops", default=""),
    )
    return [
        merge(x, {"collected_today": get_sum_today(x)})
        for x in frappe.get_all(
            "Email Alerts Grouped MOP", fields=["group_name", "mops"]
        )
    ]


@frappe.whitelist()
def get_mops():
    return [x.get("name") for x in frappe.get_all("Mode of Payment")]


@frappe.whitelist()
def get_branches():
    return [x.get("name") for x in frappe.get_all("Branch")]
