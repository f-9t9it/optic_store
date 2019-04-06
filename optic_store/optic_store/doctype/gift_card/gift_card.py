# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document


class GiftCard(Document):
    def before_insert(self):
        self.balance = self.amount
