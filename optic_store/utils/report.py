import frappe
from frappe import _
from frappe.utils import now, format_datetime
from functools import reduce
from toolz import merge, compose, first


def make_column(key, label=None, type="Data", options=None, width=120, hidden=0):
    return {
        "label": _(label or key.replace("_", " ").title()),
        "fieldname": key,
        "fieldtype": type,
        "options": options,
        "width": width,
        "hidden": hidden,
    }


def with_report_generation_time(rows, keys, field=None):
    if not rows or not frappe.db.get_single_value(
        "Optical Store Settings", "include_report_generation_time"
    ):
        return rows
    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})
    get_stamp = compose(format_datetime, now)
    return [merge(template, {field or first(keys): get_stamp()})] + rows
