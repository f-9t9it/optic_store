# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose


def validate(doc, method):
    if doc.orx_type == "Spectacles":
        sum_of = _qty_sum(doc.items)
        if sum_of("Frame") < 1:
            frappe.throw(
                "Cannot create Sales Order for Spectacle Prescription without a Frame"
            )
        if sum_of("Prescription Lens") + sum_of("Special Order Prescription Lens") < 2:
            frappe.throw(
                "Cannot create Sales Order for Spectacle Prescription without Lenses"
            )


def _qty_sum(items):
    def fn(group):
        return compose(
            sum,
            partial(map, lambda x: x.qty),
            partial(filter, lambda x: x.item_group == group),
        )(items)

    return fn
