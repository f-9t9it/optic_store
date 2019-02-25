# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
from toolz import merge


def make_employees():
    make_companies()
    make_users()
    make_branches()
    records = [
        (
            {"user_id": "simpson@optix.com"},
            {
                "first_name": "Homer",
                "last_name": "Simpson",
                "company": "Optix",
                "gender": "Male",
                "date_of_birth": "1956-05-12",
                "date_of_joining": "2010-10-10",
                "branch": "Moe's Tavern",
            },
        )
    ]
    return map(lambda x: make_test_doc("Employee", *x), records)


def make_users():
    records = [
        (
            {"email": "simpson@optix.com"},
            {
                "first_name": "Homer",
                "last_name": "Simpson",
                "roles": [
                    {"doctype": "Has Role", "role": "Employee"},
                    {"doctype": "Has Role", "role": "Sales User"},
                ],
            },
        )
    ]
    return map(lambda x: make_test_doc("User", *x), records)


def make_branches():
    records = [({"branch": "Moe's Tavern"}, {})]
    return map(lambda x: make_test_doc("Branch", *x), records)


def make_companies():
    records = [
        (
            {"company_name": "Optix"},
            {
                "abbr": "O",
                "parent_compnay": None,
                "default_currency": "BHD",
                "country": "Bahrain",
            },
        )
    ]
    return map(lambda x: make_test_doc("Company", *x), records)


def make_test_doc(doctype, exists_dict, args):
    name = frappe.db.exists(doctype, exists_dict)
    if name:
        return name
    doc = frappe.get_doc(merge({"doctype": doctype}, exists_dict, args)).insert(
        ignore_permissions=True
    )
    return doc.name
