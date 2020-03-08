# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from toolz import compose, excepts, first


def get_cashback_program(branch, posting_date):
    program_names = [
        x.get("name")
        for x in frappe.db.sql(
            """
                SELECT cp.name AS name FROM `tabCashback Program` AS cp
                LEFT JOIN `tabCashback Program Branch` AS cpb ON
                    cpb.parent = cp.name
                WHERE
                    cp.disabled = 0 AND
                    cpb.branch = %(branch)s AND
                    %(posting_date)s BETWEEN
                        cp.from_date AND IFNULL(cp.to_date, '9999-12-31')
            """,
            values={"branch": branch, "posting_date": posting_date},
            as_dict=1,
        )
    ]
    if len(program_names) > 1:
        frappe.throw(
            frappe._("Something is wrong. More than one Cashback Program found.")
        )

    get_program = compose(
        lambda x: frappe.get_doc("Cashback Program", x) if x else None,
        excepts(StopIteration, first, lambda x: None),
    )

    return get_program(program_names)
