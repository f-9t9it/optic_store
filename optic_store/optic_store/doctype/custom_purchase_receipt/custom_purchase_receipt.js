// Copyright (c) 2019, 9T9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on(
  'Custom Purchase Receipt',
  optic_store.scripts.custom_purchase_receipt
);
frappe.ui.form.on(
  'Custom Purchase Receipt Item',
  optic_store.scripts.custom_purchase_receipt.custom_purchase_receipt_item
);
