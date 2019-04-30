# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


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
