# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from functools import partial
from toolz import compose


class CashbackProgram(Document):
    def validate(self):
        if not self.item_groups:
            frappe.throw(frappe._("At least one Item Group is required."))

        if self.to_date and (
            frappe.utils.getdate(self.from_date) >= frappe.utils.getdate(self.to_date)
        ):
            frappe.throw(frappe._("To Date must be after From Date."))

        existing = frappe.db.sql(
            """
                    SELECT name FROM `tabCashback Program`
                    WHERE
                        disabled = 0 AND
                        name != %(name)s AND
                        from_date <= %(to_date)s AND
                        IF(
                            IFNULL(to_date, '') = '',
                            9999-12-31,
                            to_date
                        ) >= %(from_date)s
                """,
            values={
                "name": self.name,
                "from_date": self.from_date,
                "to_date": self.to_date or frappe.utils.datetime.date.max,
            },
        )
        if existing:
            existing_doc = frappe.get_doc("Cashback Program", existing[0][0])
            _get_item_groups = compose(list, partial(map, lambda x: x.item_group))
            if any(
                [
                    x in _get_item_groups(existing_doc.item_groups)
                    for x in _get_item_groups(self.item_groups)
                ]
            ):
                frappe.throw(
                    frappe._(
                        "Another Program: {} exists with conflicting params".format(
                            frappe.get_desk_link("Cashback Program", existing[0][0])
                        )
                    )
                )
