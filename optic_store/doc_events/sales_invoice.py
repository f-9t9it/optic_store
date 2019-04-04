# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def on_submit(doc, method):
    for item in doc.items:
        if item.serial_no:
            gift_card_validity = frappe.db.get_value(
                "Item", item.item_code, "gift_card_validity"
            )
            for serial_no in item.serial_no.split("\n"):
                gift_card_no = frappe.db.exists(
                    "Gift Card", {"gift_card_no": serial_no}
                )
                if gift_card_no:
                    frappe.db.set_value(
                        "Gift Card",
                        gift_card_no,
                        "expiry_date",
                        frappe.utils.add_days(doc.posting_date, gift_card_validity),
                    )
