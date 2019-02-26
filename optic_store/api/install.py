# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def setup_defaults():
    frappe.only_for("System Manager")
    _create_item_groups()
    _update_settings()


def _create_item_groups():
    def create_group(parent="All Item Groups", is_group=0):
        def fn(name, abbr=None):
            if not frappe.db.exists("Item Group", name):
                frappe.get_doc(
                    {
                        "doctype": "Item Group",
                        "item_group_name": name,
                        "item_group_abbr": abbr,
                        "parent_item_group": parent,
                        "is_group": is_group,
                    }
                ).insert(ignore_permissions=True)

        return fn

    def run_creator(name, value):
        create_group(is_group=1)(name)
        map(lambda x: create_group(parent=name)(*x), value.items())

    groups = {
        "Prescription": {
            "Frame": "FR",
            "Prescription Lens": None,
            "Special Order Prescription Lens": None,
            "Contact Lens": "CL",
            "Reader": None,
        },
        "Others": {"Sunglasses": "SG", "Accessories": "AC", "Solutions": "SL"},
    }

    map(lambda x: run_creator(*x), groups.items())


def _update_settings():
    def update(doctype, params):
        doc = frappe.get_single(doctype)
        map(lambda x: doc.set(*x), params.items())
        doc.save(ignore_permissions=True)

    settings = {
        "Selling Settings": {"cust_master_name": "Naming Series"},
        "Stock Settings": {"item_naming_by": "Naming Series", "show_barcode_field": 1},
    }

    map(lambda x: update(*x), settings.items())
