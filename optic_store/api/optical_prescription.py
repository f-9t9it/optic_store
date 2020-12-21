# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.desk.reportview import get_filters_cond
from toolz import compose


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def query_latest(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """
            SELECT name, type, customer_name, test_date
            FROM `tabOptical Prescription`
            WHERE
                docstatus = 1 AND
                {key} like %(txt)s
                {fcond}
            ORDER BY
                IF(LOCATE(%(_txt)s, name), LOCATE(%(_txt)s, name), 99999),
                test_date DESC
            LIMIT %(start)s, %(page_len)s
        """.format(
            key=searchfield, fcond=get_filters_cond(doctype, filters, [])
        ),
        values={
            "txt": "%%%s%%" % txt,
            "_txt": txt.replace("%", ""),
            "start": start,
            "page_len": page_len,
        },
    )


@frappe.whitelist()
def save_and_submit(doc):
    submit = compose(frappe.client.submit, frappe.client.insert)
    return submit(doc)
