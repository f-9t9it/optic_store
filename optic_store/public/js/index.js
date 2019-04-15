import {
  sales_invoice,
  sales_invoice_gift_cards,
  sales_order,
  customer,
  item,
  optical_prescription,
  optical_prescription_qe,
  optical_store_settings,
  group_discount,
  gift_card,
} from './scripts';

frappe.ui.form.on('Sales Invoice', sales_invoice);
frappe.ui.form.on('Sales Invoice Gift Card', sales_invoice_gift_cards);
frappe.ui.form.on('Sales Order', sales_order);
frappe.ui.form.on('Customer', customer);
frappe.ui.form.on('Item', item);

frappe.ui.form.OpticalPrescriptionQuickEntryForm = frappe.ui.form.QuickEntryForm.extend(
  optical_prescription_qe
);

const __version__ = '0.0.3';

frappe.provide('optic_store');
optic_store = {
  __version__,
  optical_prescription,
  optical_store_settings,
  group_discount,
  gift_card,
};
