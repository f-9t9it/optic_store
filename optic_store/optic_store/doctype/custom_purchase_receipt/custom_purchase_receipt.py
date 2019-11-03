# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class CustomPurchaseReceipt(Document):
    def before_save(self):
        self._set_existing()

    def before_submit(self):
        self._validate_existing_items()
        self._validate_new_items()

    def on_submit(self):
        self._create_items()
        self._create_purchase_receipt()

    def _set_existing(self):
        for item in self.items:
            item.amount = flt(item.qty) * flt(item.rate)
            item.item_code = frappe.db.exists("Item", {"item_name": item.item_name})
            if item.item_code:
                item.item_group = frappe.db.get_value(
                    "Item", item.item_code, "item_group"
                )
            if item.item_code and not item.uom:
                item.uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
            if item.item_code and item.has_batch and item.expiry_date:
                item.batch = frappe.db.exists(
                    "Batch", {"item": item.item_code, "expiry_date": item.expiry_date}
                )

    def _validate_existing_items(self):
        for item in filter(lambda x: x.item_code, self.items):
            if item.has_batch != frappe.db.get_value(
                "Item", item.item_code, "has_batch_no"
            ):
                frappe.throw(
                    _(
                        "<em>Has Batch</em> mismatched for "
                        "item <strong>{}: {}</strong> on row #{}.".format(
                            item.item_code, item.item_name, item.idx
                        )
                    )
                )
            if item.uom not in [
                x.uom
                for x in frappe.get_all(
                    "UOM Conversion Detail",
                    filters={"parent": item.item_code},
                    fields=["uom"],
                )
            ]:
                frappe.throw(
                    _(
                        "<em>UOM</em> <strong>{}</strong> not allowed for "
                        "item <strong>{}: {}</strong> on row #{}.".format(
                            item.uom, item.item_code, item.item_name, item.idx
                        )
                    )
                )

    def _validate_new_items(self):
        for item in filter(lambda x: not x.item_code, self.items):
            if not item.item_group:
                frappe.throw(
                    _(
                        "<em>Item Group</em> required for Item <strong>{}</strong> on "
                        "row #{}.".format(item.item_name, item.idx)
                    )
                )
            if not item.uom:
                frappe.throw(
                    _(
                        "<em>UOM</em> required for Item <strong>{}</strong> on "
                        "row #{}.".format(item.item_name, item.idx)
                    )
                )

    def _create_items(self):
        for item in filter(lambda x: not x.item_code, self.items):
            doc = frappe.get_doc(
                {
                    "doctype": "Item",
                    "item_name": item.item_name,
                    "item_group": item.item_group,
                    "is_stock_item": 1,
                    "has_batch_no": item.has_batch,
                    "create_new_batch": item.has_batch,
                    "has_expiry_date": 1 if item.has_batch and item.expiry_date else 0,
                }
            )
            doc.flags.ignore_permissions = True
            doc.insert()
            doc.append("barcodes", {"barcode": doc.name})
            doc.save()
            frappe.db.set_value(item.doctype, item.name, "item_code", doc.name)

    def _create_purchase_receipt(self):
        def post_doc(source, target):
            if target.set_posting_time:
                target.posting_date = source.posting_datetime.date()
                target.posting_time = source.posting_datetime.time()

        doc = get_mapped_doc(
            "Custom Purchase Receipt",
            self.name,
            {
                "Custom Purchase Receipt": {"doctype": "Purchase Receipt"},
                "Custom Purchase Receipt Item": {
                    "doctype": "Purchase Receipt Item",
                    "field_map": {"expiry_date": "os_expiry_date", "batch": "batch_no"},
                },
            },
            postprocess=post_doc,
            ignore_permissions=True,
        )
        doc.insert()
        doc.submit()

        frappe.db.set_value(self.doctype, self.name, "purchase_receipt", doc.name)
        for i, item in enumerate(self.items):
            if item.has_batch and not item.batch:
                frappe.db.set_value(
                    item.doctype, item.name, "batch", doc.items[i].batch_no
                )
