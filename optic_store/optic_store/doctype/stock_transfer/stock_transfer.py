# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import now, get_datetime, flt
from frappe.model.document import Document
from functools import partial
from toolz import merge, compose

from optic_store.api.customer import get_user_branch
from optic_store.utils import pick, sum_by


class StockTransfer(Document):
    def validate(self):
        user_branch = get_user_branch()
        if not _is_sys_mgr() and self.source_branch != user_branch:
            frappe.throw(
                _(
                    "Source branch only allowed to be set to User branch: {}".format(
                        user_branch
                    )
                )
            )
        if self.source_branch == self.target_branch:
            frappe.throw(_("Source and Target Branches cannot be the same"))
        if not self.source_warehouse:
            self.source_warehouse = frappe.db.get_value(
                "Branch", self.source_branch, "warehouse"
            )
        if not self.target_warehouse:
            self.target_warehouse = frappe.db.get_value(
                "Branch", self.target_branch, "warehouse"
            )
        if not self.source_warehouse or not self.target_warehouse:
            frappe.throw(_("Warehouse not found for one or both Branches"))

    def before_save(self):
        if not self.outgoing_datetime:
            self.outgoing_datetime = now()
        self.set_missing_fields()

    def before_submit(self):
        self.validate_owner()

    def on_submit(self):
        if self.workflow_state == "In Transit":
            warehouses = self.get_warehouses(incoming=False)
            accounts = self.get_accounts()
            ref_doc = _make_stock_entry(
                merge(
                    pick(["company"], self.as_dict()),
                    warehouses,
                    {"items": _map_items(warehouses, accounts)(self.items)},
                    _destruct_datetime(self.outgoing_datetime),
                )
            )
            self.set_ref_doc("outgoing_stock_entry", ref_doc)

    def before_update_after_submit(self):
        if not _is_sys_mgr() and self.target_branch != get_user_branch():
            frappe.throw(
                _(
                    "Only users from Branch: {} can perform this".format(
                        self.target_branch
                    )
                )
            )

        if not self.incoming_datetime:
            self.incoming_datetime = now()
        self.validate_dates()

    def on_update_after_submit(self):
        if self.workflow_state == "Received":
            warehouses = self.get_warehouses(incoming=True)
            accounts = self.get_accounts()
            ref_doc = _make_stock_entry(
                merge(
                    pick(["company"], self.as_dict()),
                    warehouses,
                    {"items": _map_items(warehouses, accounts)(self.items)},
                    _destruct_datetime(self.incoming_datetime),
                )
            )
            self.set_ref_doc("incoming_stock_entry", ref_doc)

    def before_cancel(self):
        self.validate_owner()

    def on_cancel(self):
        if self.incoming_stock_entry:
            se = frappe.get_doc("Stock Entry", self.incoming_stock_entry)
            se.cancel()
        if self.outgoing_stock_entry:
            se = frappe.get_doc("Stock Entry", self.outgoing_stock_entry)
            se.cancel()

    def set_missing_fields(self):
        for item in self.items:
            item.amount = flt(item.qty) * flt(item.basic_rate)
            item.valuation_rate = item.amount / flt(item.qty)
        self.total_value = sum_by("amount")(self.items)
        self.total_qty = sum_by("qty")(self.items)

    def validate_dates(self):
        if get_datetime(self.outgoing_datetime) > get_datetime(self.incoming_datetime):
            frappe.throw(_("Outgoing Datetime cannot be after Incoming Datetime"))

    def validate_owner(self):
        if not _is_sys_mgr() and self.owner != frappe.session.user:
            frappe.throw(_("Only document owner can perform this"))

    def set_ref_doc(self, field, ref_doc):
        self.db_set(field, ref_doc)

    def get_warehouses(self, incoming=False):
        transit_warehouse = frappe.db.get_single_value(
            "Optical Store Settings", "transit_warehouse"
        )
        return (
            {"from_warehouse": self.source_warehouse, "to_warehouse": transit_warehouse}
            if not incoming
            else {
                "from_warehouse": transit_warehouse,
                "to_warehouse": self.target_warehouse,
            }
        )

    def get_accounts(self):
        company = frappe.get_doc("Company", self.company)
        return {
            "expense_account": company.stock_adjustment_account,
            "cost_center": company.cost_center,
        }


def _destruct_datetime(dt):
    _dt = get_datetime(dt)
    return {"posting_date": _dt.date(), "posting_time": _dt.time()}


def _map_items(warehouses, accounts):
    make_item = compose(
        partial(
            merge,
            {
                "s_warehouse": warehouses.get("from_warehouse"),
                "t_warehouse": warehouses.get("to_warehouse"),
                "expense_account": accounts.get("expense_account"),
                "cost_center": accounts.get("cost_center"),
            },
        ),
        partial(
            pick,
            [
                "item_code",
                "qty",
                "uom",
                "basic_rate",
                "amount",
                "valuation_rate",
                "serial_no",
                "batch_no",
            ],
        ),
        lambda x: x.as_dict(),
    )
    return partial(map, make_item)


def _make_stock_entry(args):
    doc = frappe.get_doc(
        merge(
            {
                "doctype": "Stock Entry",
                "purpose": "Material Transfer",
                "set_posting_time": 1,
            },
            args,
        )
    )
    doc.insert()
    doc.submit()
    return doc.name


def _is_sys_mgr():
    return "System Manager" in frappe.get_roles(frappe.session.user)
