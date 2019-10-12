# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9t9it and Contributors
# See license.txt

from __future__ import unicode_literals
from datetime import date
from functools import partial
from toolz import compose, first, excepts
from frappe.utils import get_first_day, get_last_day, getdate, add_months, add_days, flt


def generate_intervals(interval, start_date, end_date):
    if interval == "Daily":
        periods = []
        start = getdate(start_date)
        cur_start = start
        while cur_start <= getdate(end_date):
            periods.append(
                {
                    "key": cur_start.strftime("%Y-%m-%d"),
                    "label": cur_start.strftime("%Y-%m-%d"),
                    "start_date": cur_start,
                    "end_date": cur_start,
                }
            )
            cur_start = add_days(cur_start, 1)
        return periods
    if interval == "Weekly":
        periods = []
        start = getdate(start_date)
        cur_start = add_days(start, -start.weekday())
        while cur_start <= getdate(end_date):
            year, week, ___ = cur_start.isocalendar()
            periods.append(
                {
                    "key": "{:2d}W{:2d}".format(year % 100, week),
                    "label": cur_start.strftime("%Y-%m-%d"),
                    "start_date": cur_start,
                    "end_date": add_days(cur_start, 6),
                }
            )
            cur_start = add_days(cur_start, 7)
        return periods
    if interval == "Monthly":
        periods = []
        cur_start = get_first_day(start_date)
        while cur_start <= getdate(end_date):
            periods.append(
                {
                    "key": cur_start.strftime("%yM%m"),
                    "label": cur_start.strftime("%b %y"),
                    "start_date": cur_start,
                    "end_date": get_last_day(cur_start),
                }
            )
            cur_start = add_months(cur_start, 1)
        return periods
    if interval == "Yearly":
        periods = []
        cur_year = getdate(start_date).year
        while cur_year <= getdate(end_date).year:
            periods.append(
                {
                    "key": "{:2d}Y".format(cur_year % 100),
                    "label": "{:4d}".format(cur_year),
                    "start_date": date(cur_year, 1, 1),
                    "end_date": date(cur_year, 12, 31),
                }
            )
            cur_year += 1
        return periods
    return []


def get_parts(items):
    def get_by_part(part):
        return compose(
            excepts(StopIteration, first, lambda x: None),
            partial(filter, lambda x: x.os_spec_part == part),
        )(items)

    return map(get_by_part, ("Frame", "Lens Right", "Lens Left"))


def get_optical_items(items):
    frame, lens_right, lens_left = get_parts(items)
    return {
        "frame": frame,
        "lens_right": lens_right,
        "lens_left": lens_left,
        "others": filter(lambda x: x not in [frame, lens_right, lens_left], items),
    }


def get_amounts(doc):
    get_price_list_amount = compose(
        sum,
        partial(map, lambda x: max(flt(x.price_list_rate) * flt(x.qty), flt(x.amount))),
    )
    total = get_price_list_amount(doc.items)
    # `doc.discount_amount` is negative
    discount_amount = doc.discount_amount + (doc.total - total)
    return {"total": total, "discount_amount": discount_amount}
