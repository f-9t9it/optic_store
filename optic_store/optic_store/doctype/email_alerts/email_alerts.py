# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class EmailAlerts(Document):
    def validate(self):
        for grouped_mop in self.branch_sales_grouped_mops:
            if not grouped_mop.mops:
                frappe.throw(
                    frappe._(
                        "Please select Modes of Payment for the Group in row {}".format(
                            grouped_mop.idx
                        )
                    )
                )
