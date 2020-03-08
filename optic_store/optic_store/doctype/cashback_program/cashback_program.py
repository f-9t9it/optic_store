# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


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
                SELECT cp.name FROM `tabCashback Program Branch` AS cpb
                LEFT JOIN `tabCashback Program` AS cp ON
                    cp.name = cpb.parent
                WHERE
                    cp.disabled = 0 AND
                    cp.name != %(name)s AND
                    cp.from_date <= %(to_date)s AND
                    IFNULL(cp.to_date, '9999-12-31') >= %(from_date)s AND
                    cpb.branch IN %(branches)s
            """,
            values={
                "name": self.name,
                "from_date": self.from_date,
                "to_date": self.to_date or frappe.utils.datetime.date.max,
                "branches": [x.branch for x in self.branches],
            },
        )
        if existing:
            frappe.throw(
                frappe._(
                    "Another {} exists with conflicting params".format(
                        frappe.get_desk_link("Cashback Program", existing[0][0])
                    )
                )
            )
