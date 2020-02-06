# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck, concatv, merge

from optic_store.utils import pick
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    return [
        make_column("bank_name", "BANK CODE", width=90),
        make_column("bank_ac_no", "CREDIT ACCOUNT NO", width=150),
        make_column("employee_name", "EMP NAME", width=150),
        make_column("amount", "AMOUNT", type="Currency"),
        make_column("remarks", "REMARKS", width=150),
        make_column("placeholder1", "PAYMENT_PRODUCT"),
        make_column("placeholder2", "TXN_CCY"),
        make_column("placeholder3", "SWIFT_CHARGING_OPT"),
        make_column("placeholder3", "PAYMENT_VALUE_DATE"),
        make_column("account_number", "DEBIT_ACCOUNT NUMBER", width=150),
    ]


def _get_filters(filters):
    join_clauses = compose(lambda x: " AND ".join(x), concatv)
    get_components = compose(
        list,
        partial(pluck, "salary_component"),
        lambda x: frappe.get_all(
            "Optical Store HR Settings Salary Component",
            fields=["salary_component"],
            filters={"parentfield": "{}_components".format(x)},
        ),
        lambda x: x.replace(" ", "_").lower(),
    )

    values = merge(filters, {"components": get_components(filters.get("report_type"))})
    return (
        join_clauses(["sl.status = %(status)s", "sl.start_date = %(start_date)s"]),
        values,
    )


def _get_data(clauses, values, keys):
    result = frappe.db.sql(
        """
            SELECT
                e.bank_name AS bank_name,
                e.bank_ac_no AS bank_ac_no,
                e.employee_name AS employee_name,
                IFNULL(SUM(sde.amount), 0) - IFNULL(SUM(sdd.amount), 0) AS amount,
                sl.start_date AS start_date,
                a.account_number AS account_number
            FROM `tabSalary Slip` AS sl
            LEFT JOIN `tabSalary Detail` AS sde ON
                sde.parent = sl.name AND
                sde.parentfield = 'earnings' AND
                sde.salary_component IN %(components)s
            LEFT JOIN `tabSalary Detail` AS sdd ON
                sdd.parent = sl.name AND
                sdd.parentfield = 'deductions' AND
                sdd.salary_component IN %(components)s
            LEFT JOIN `tabEmployee` AS e ON e.name = sl.employee
            LEFT JOIN `tabPayroll Entry` AS pe ON pe.name = sl.payroll_entry
            LEFT JOIN `tabAccount` AS a ON a.name = pe.payment_account
            WHERE {clauses}
            GROUP BY sl.employee, sl.start_date
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    def add_remarks(row):
        start_date = row.get("start_date")
        return merge(
            row, {"remarks": "{} SAL".format(start_date.strftime("%b").upper())}
        )

    make_row = compose(partial(pick, keys), add_remarks)
    return with_report_generation_time([make_row(x) for x in result], keys)
