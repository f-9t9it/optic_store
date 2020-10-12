# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from toolz import excepts, first, compose

from optic_store.utils import map_resolved


def set_or_create_batch(doc, method):
    def set_existing_batch(item):
        if item.os_expiry_date and not item.batch_no:
            has_batch_no, has_expiry_date = frappe.db.get_value(
                "Item", item.item_code, ["has_batch_no", "has_expiry_date"]
            )
            if has_batch_no and has_expiry_date:
                batch_no = frappe.db.exists(
                    "Batch",
                    {"item": item.item_code, "expiry_date": item.os_expiry_date},
                )
                item.batch_no = batch_no

    get_batch_in_previous_items = compose(
        lambda x: x.get("batch_no"),
        excepts(StopIteration, first, lambda _: {}),
        lambda x: filter(
            lambda item: item.idx < x.idx
            and item.item_code == x.item_code
            and item.pb_expiry_date == x.pb_expiry_date,
            doc.items,
        ),
    )

    def create_new_batch(item):
        warehouse = "t_warehouse" if doc.doctype == "Stock Entry" else "warehouse"
        if item.get(warehouse) and item.os_expiry_date and not item.batch_no:
            has_batch_no, create_new_batch, has_expiry_date = frappe.db.get_value(
                "Item",
                item.item_code,
                ["has_batch_no", "create_new_batch", "has_expiry_date"],
            )
            if has_batch_no and create_new_batch and has_expiry_date:
                batch_in_items = get_batch_in_previous_items(item)
                if batch_in_items:
                    item.batch_no = batch_in_items
                    return
                batch = frappe.get_doc(
                    {
                        "doctype": "Batch",
                        "item": item.item_code,
                        "expiry_date": item.os_expiry_date,
                        "supplier": doc.supplier,
                        # "reference_doctype": doc.doctype,
                        # "reference_name": doc.name,
                    }
                ).insert()
                item.batch_no = batch.name

    if doc._action == "save":
        map_resolved(set_existing_batch, doc.items)

        # TODO: when `before_validate` gets merged into master create_new_batch should
        # run when doc._action == 'submit'.
        # also update `hooks.py` to use `before_validate` instead of the current
        # `before_save` method
        map_resolved(create_new_batch, doc.items)


def before_validate(doc, method):
    set_or_create_batch(doc, method)


def validate(doc, method):
    if doc.supplier_delivery_note:
        existing = frappe.db.exists(
            "Purchase Receipt",
            {
                "supplier_delivery_note": doc.supplier_delivery_note,
                "name": ("!=", doc.name),
            },
        )
        if existing:
            frappe.throw(
                frappe._(
                    "Supplier Delivery Note {} exists in Purchase Receipt {}".format(
                        doc.supplier_delivery_note, existing
                    )
                )
            )


def set_batch_references(doc, method):
    # this method will not be necessaery when upstream 'before_validate' comes into play
    def set_fields(item):
        if item.batch_no:
            batch = frappe.get_doc("Batch", item.batch_no)
            if not batch.reference_doctype and not batch.reference_name:
                frappe.db.set_value(
                    "Batch", item.batch_no, "reference_doctype", doc.doctype
                )
                frappe.db.set_value("Batch", item.batch_no, "reference_name", doc.name)

    map_resolved(set_fields, doc.items)
