# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from toolz import merge


@frappe.whitelist()
def setup_defaults():
    frappe.only_for("System Manager")
    company = frappe.defaults.get_global_default("company")
    _update_settings()
    _setup_workflow()
    _setup_accounts(company)


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


def _setup_workflow():
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

    def make_workflow(name, **args):
        if args.get("transitions"):
            map(lambda x: make_action(x.get("action")), args.get("transitions"))
        if args.get("states"):
            map(
                lambda x: make_state(x.get("state"), x.get("style")), args.get("states")
            )
            map(lambda x: make_role(x.get("allow_edit")), args.get("states"))
        if not frappe.db.exists("Workflow", name):
            frappe.get_doc(
                merge({"doctype": "Workflow", "workflow_name": name}, args)
            ).insert(ignore_permissions=True)
        else:
            doc = frappe.get_doc("Workflow", name)
            doc.update(args)
            doc.save(ignore_permissions=True)

    map(
        lambda x: make_workflow(**x),
        [
            {
                "name": "Optic Store Sales Order",
                "document_type": "Sales Order",
                "is_active": 1,
                "send_email_alert": 0,
                "workflow_state_field": "workflow_state",
                "states": [
                    {
                        "state": "Draft",
                        "style": "Danger",
                        "doc_status": "0",
                        "allow_edit": "Sales User",
                    },
                    {
                        "state": "Processing at Branch",
                        "style": "Primary",
                        "doc_status": "1",
                        "allow_edit": "Sales User",
                    },
                    {
                        "state": "Sent to HQM",
                        "style": "Warning",
                        "doc_status": "1",
                        "allow_edit": "Store User",
                    },
                    {
                        "state": "With Special Order Incharge",
                        "style": "Warning",
                        "doc_status": "1",
                        "allow_edit": "Store User",
                    },
                    {
                        "state": "Processing at HQM",
                        "style": "Primary",
                        "doc_status": "1",
                        "allow_edit": "Lab Tech",
                    },
                    {
                        "state": "Processing for Delivery",
                        "style": "Info",
                        "doc_status": "1",
                        "allow_edit": "Store User",
                    },
                    {
                        "state": "In Transit (with Driver)",
                        "style": "Warning",
                        "doc_status": "1",
                        "allow_edit": "Sales User",
                    },
                    {
                        "state": "Ready to Deliver",
                        "style": "Success",
                        "doc_status": "1",
                        "allow_edit": "Sales User",
                    },
                ],
                "transitions": [
                    {
                        "state": "Draft",
                        "action": "Process at Branch",
                        "next_state": "Processing at Branch",
                        "allowed": "Sales User",
                        "allow_self_approval": 1,
                        "condition": "not doc.os_is_special_order and doc.os_is_branch_order",
                    },
                    {
                        "state": "Processing at Branch",
                        "action": "Complete",
                        "next_state": "Ready to Deliver",
                        "allowed": "Sales User",
                        "allow_self_approval": 1,
                    },
                    {
                        "state": "Draft",
                        "action": "Send to HQM",
                        "next_state": "Sent to HQM",
                        "allowed": "Sales User",
                        "allow_self_approval": 1,
                        "condition": "not doc.os_is_special_order and not doc.os_is_branch_order",
                    },
                    {
                        "state": "Sent to HQM",
                        "action": "Process at HQM",
                        "next_state": "Processing at HQM",
                        "allowed": "Store User",
                        "allow_self_approval": 1,
                    },
                    {
                        "state": "Draft",
                        "action": "Send as Special Order",
                        "next_state": "With Special Order Incharge",
                        "allowed": "Sales User",
                        "allow_self_approval": 1,
                        "condition": "doc.os_is_special_order",
                    },
                    {
                        "state": "With Special Order Incharge",
                        "action": "Process Special Order",
                        "next_state": "Processing at HQM",
                        "allowed": "Store User",
                        "allow_self_approval": 1,
                    },
                    {
                        "state": "Processing at HQM",
                        "action": "Proceed to Deliver",
                        "next_state": "Processing for Delivery",
                        "allowed": "Lab Tech",
                        "allow_self_approval": 1,
                    },
                    {
                        "state": "Processing for Delivery",
                        "action": "Send to Branch",
                        "next_state": "In Transit (with Driver)",
                        "allowed": "Store User",
                        "allow_self_approval": 1,
                    },
                    {
                        "state": "In Transit (with Driver)",
                        "action": "Complete",
                        "next_state": "Ready to Deliver",
                        "allowed": "Sales User",
                        "allow_self_approval": 1,
                    },
                ],
            }
        ],
    )


def _setup_accounts(company):
    def create_or_get_account_name():
        parent_account = frappe.db.exists(
            "Account", {"company": company, "account_name": "Current Liabilities"}
        )
        account_args = {"company": company, "account_name": "Gift Card"}
        account_name = frappe.db.exists("Account", account_args)
        if account_name:
            return account_name
        account = frappe.get_doc(
            merge(
                {"doctype": "Account"},
                account_args,
                {"parent_account": parent_account, "account_type": "Cash"},
            )
        ).insert(ignore_permissions=True)
        return account.name

    def create_or_get_mode_of_payment():
        mop_args = {"mode_of_payment": "Gift Card"}
        mop_name = frappe.db.exists("Mode of Payment", mop_args)
        if mop_name:
            return frappe.get_doc("Mode of Payment", mop_name)
        return frappe.get_doc(
            merge({"doctype": "Mode of Payment"}, mop_args, {"type": "General"})
        ).insert(ignore_permissions=True)

    settings = frappe.get_single("Optical Store Settings")
    settings.gift_card_deferred_revenue = create_or_get_account_name()
    settings.save(ignore_permissions=True)

    mop = create_or_get_mode_of_payment()
    if company not in map(lambda x: x.company, mop.accounts):
        mop.append(
            "accounts",
            {
                "company": company,
                "default_account": settings.gift_card_deferred_revenue,
            },
        )
        mop.save(ignore_permissions=True)

    jea_options = (
        frappe.get_meta("Journal Entry Account").get_field("reference_type").options
    )
    if "Gift Card" not in jea_options:
        existing_ps = frappe.db.exists(
            "Property Setter",
            {
                "doc_type": "Journal Entry Account",
                "field_name": "reference_type",
                "property": "options",
            },
        )
        if existing_ps:
            ps = frappe.get_doc("Property Setter", existing_ps)
            ps.value = ps.value + "\nGift Card"
            ps.save(ignore_permissions=True)
        else:
            frappe.get_doc(
                {
                    "doctype": "Property Setter",
                    "doc_type": "Journal Entry Account",
                    "doctype_or_field": "DocField",
                    "field_name": "reference_type",
                    "property": "options",
                    "value": jea_options + "\nGift Card",
                }
            ).insert(ignore_permissions=True)
