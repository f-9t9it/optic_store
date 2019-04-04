# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def after_insert(doc, method):
    item = frappe.get_doc("Item", doc.item_code)
    if item.is_gift_card:
        frappe.get_doc(
            {
                "doctype": "Gift Card",
                "gift_card_no": doc.serial_no,
                "amount": item.gift_card_value,
            }
        ).insert()


def on_trash(doc, method):
    gift_card_no = frappe.db.exists("Gift Card", {"gift_card_no": doc.serial_no})
    if gift_card_no:
        frappe.delete_doc("Gift Card", gift_card_no)
