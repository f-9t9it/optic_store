# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from erpnext.selling.page.point_of_sale.point_of_sale import (
    search_serial_or_batch_or_barcode_number as search_item,
)


@frappe.whitelist()
def deliver_qol(name):
    doc = make_delivery_note(name)
    doc.insert(ignore_permissions=True)
    doc.submit()
    return doc.name


# This method is hooked in override_whitelisted_methods because the return value by
# upstream method cannot evaluate to false client side. It should be removed once the
# upstream code has been patched
@frappe.whitelist()
def search_serial_or_batch_or_barcode_number(search_value):
    return (
        frappe.db.get_value("Item", search_value, ["name as item_code"], as_dict=True)
        or search_item(search_value)
        or None
    )
