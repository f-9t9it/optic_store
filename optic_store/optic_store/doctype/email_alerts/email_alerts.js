// Copyright (c) 2019, 9T9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on(
  'Email Alerts Grouped MOP',
  optic_store.scripts.email_alerts.email_alerts_grouped_mop
);

frappe.ui.form.on('Email Alerts', optic_store.scripts.email_alerts);
