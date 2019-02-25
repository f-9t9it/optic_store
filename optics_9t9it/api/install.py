# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def setup_defaults():
    _create_item_groups()
    _update_settings()


def _create_item_groups():
    def create_group(parent="All Item Groups", is_group=0):
        def fn(name):
            if not frappe.db.exists("Item Group", name):
                frappe.get_doc(
                    {
                        "doctype": "Item Group",
                        "item_group_name": name,
                        "parent_item_group": parent,
                        "is_group": is_group,
                    }
                ).insert(ignore_permissions=True)

        return fn

    parent = "Optical"
    create_group(is_group=1)(parent)

    create_optical_child = create_group(parent=parent)
    map(
        create_optical_child,
        [
            "Frame",
            "Prescription Lens",
            "Special Order Prescription Lens",
            "Contact Lens",
            "Reader",
        ],
    )
    frappe.db.commit()


def _update_settings():
    frappe.db.set_value("Selling Settings", None, "cust_master_name", "Naming Series")
