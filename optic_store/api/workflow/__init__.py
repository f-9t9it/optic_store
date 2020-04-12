# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import os.path
from toolz import merge, unique


@frappe.whitelist()
def get_sales_order_workflows():
    return [
        x.get("name")
        for x in frappe.get_all("Workflow", {"document_type": "Sales Order"})
    ]


@frappe.whitelist()
def get_current_workflow_name(doctype):
    return frappe.model.meta.get_workflow_name(doctype)


def activate_workflow(name):
    if not frappe.db.exists("Workflow", name):
        setup_workflow(name)

    document_type = frappe.db.get_value("Workflow", name, "document_type")
    for (other,) in frappe.get_all(
        "Workflow",
        filters={"document_type": document_type, "name": ("!=", name), "is_active": 1},
        as_list=1,
    ):
        frappe.db.set_value("Workflow", other, "is_active", 0)
    frappe.db.set_value("Workflow", name, "is_active", 1)


def setup_workflow(name):
    def make_action(name):
        if not frappe.db.exists("Workflow Action Master", name):
            frappe.get_doc(
                {"doctype": "Workflow Action Master", "workflow_action_name": name}
            ).insert(ignore_permissions=True)

    def make_state(name, style=None):
        if not frappe.db.exists("Workflow State", name):
            frappe.get_doc(
                {
                    "doctype": "Workflow State",
                    "workflow_state_name": name,
                    "style": style,
                }
            ).insert(ignore_permissions=True)
        else:
            doc = frappe.get_doc("Workflow State", name)
            doc.update({"style": style})
            doc.save(ignore_permissions=True)

    def make_role(name, desk_access=1):
        if not frappe.db.exists("Role", name):
            frappe.get_doc(
                {"doctype": "Role", "role_name": name, "desk_access": desk_access}
            ).insert(ignore_permissions=True)

    args = _get_workflow_config(name)
    if not args:
        frappe.throw(frappe._("Unable to setup workflow {}".format(frappe.bold(name))))

    for action in unique([x.get("action") for x in args.get("transitions")]):
        make_action(action)
    for state in args.get("states"):
        make_state(state.get("state"), state.get("style"))
        make_role(state.get("allow_edit"))

    frappe.get_doc(
        merge({"doctype": "Workflow", "workflow_name": args.get("name")}, args)
    ).insert(ignore_permissions=True)


def _get_workflow_config(name):
    filepath = "{}/fixtures/{}.json".format(
        os.path.abspath(os.path.dirname(__file__)), frappe.scrub(name)
    )
    try:
        with open(filepath) as f:
            return f.read()
    except FileNotFoundError:
        return None
