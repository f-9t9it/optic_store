# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def after_insert(doc, method):
    is_gift_card = frappe.db.get_value("Item", doc.item_code, "is_gift_card")
    if is_gift_card:
        gift_card_value = frappe.db.get_value("Item", doc.item_code, "gift_card_value")
        frappe.get_doc(
            {
                "doctype": "Gift Card",
                "gift_card_no": doc.serial_no,
                "amount": gift_card_value,
            }
        ).insert()


def on_trash(doc, method):
    gift_card_no = frappe.db.exists("Gift Card", {"gift_card_no": doc.serial_no})
    if gift_card_no:
        frappe.delete_doc("Gift Card", gift_card_no)
