# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from optic_store.api.customer import get_user_branch


def execute():
    for doc in frappe.get_all(
        "Customer",
        filters=[["branch", "is", "not set"], ["old_customer_id", "is", "not set"]],
        fields=["name", "owner"],
    ):
        branch = get_user_branch(doc.get("owner"))
        if branch:
            frappe.db.set_value("Customer", doc.get("name"), "branch", branch)
