# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

from optic_store.api.workflow import activate_workflow


class OpticalStoreSettings(Document):
    def validate(self):
        if (
            self.special_order_item_group
            and self.standard_item_group
            and self.special_order_item_group == self.standard_item_group
        ):
            frappe.throw(
                _("Special Order Item Group and Standard Item Group cannot be the same")
            )

    def on_update(self):
        if self.sales_order_workflow:
            activate_workflow(self.sales_order_workflow)
        else:
            for (name,) in frappe.get_all(
                "Workflow",
                filters={"document_type": "Sales Order", "is_active": 1},
                as_list=1,
            ):
                frappe.db.set_value("Workflow", name, "is_active", 0)
