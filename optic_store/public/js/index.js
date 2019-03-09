import {
  sales_order,
  customer,
  item,
  optical_prescription,
  optical_prescription_qe,
} from './scripts';

frappe.ui.form.on('Sales Order', sales_order);
frappe.ui.form.on('Customer', customer);
frappe.ui.form.on('Item', item);

frappe.ui.form.OpticalPrescriptionQuickEntryForm = frappe.ui.form.QuickEntryForm.extend(
  optical_prescription_qe
);

frappe.provide('optic_store');
optic_store = { optical_prescription };
