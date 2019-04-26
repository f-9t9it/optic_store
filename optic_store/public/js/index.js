import {
  sales_invoice,
  sales_invoice_item,
  sales_invoice_gift_card,
  delivery_note,
  delivery_note_item,
  sales_order,
  customer,
  customer_qe,
  employee,
  item,
  optical_prescription,
  optical_prescription_qe,
  optical_store_settings,
  group_discount,
  gift_card,
  stock_transfer,
  stock_transfer_item,
} from './scripts';
import extend_pos from './pages/pos';

frappe.ui.form.on('Sales Invoice', sales_invoice);
frappe.ui.form.on('Sales Invoice Item', sales_invoice_item);
frappe.ui.form.on('Sales Invoice Gift Card', sales_invoice_gift_card);
frappe.ui.form.on('Delivery Note', delivery_note);
frappe.ui.form.on('Delivery Note Item', delivery_note_item);
frappe.ui.form.on('Sales Order', sales_order);
frappe.ui.form.on('Customer', customer);
frappe.ui.form.on('Employee', employee);
frappe.ui.form.on('Item', item);

if (frappe.ui.form.CustomerQuickEntryForm) {
  frappe.ui.form.CustomerQuickEntryForm = frappe.ui.form.CustomerQuickEntryForm.extend(
    customer_qe
  );
}

frappe.ui.form.OpticalPrescriptionQuickEntryForm = frappe.ui.form.QuickEntryForm.extend(
  optical_prescription_qe
);

const __version__ = '0.3.4';

frappe.provide('optic_store');
optic_store = {
  __version__,
  optical_prescription,
  optical_store_settings,
  group_discount,
  gift_card,
  stock_transfer,
  stock_transfer_item,
  extend_pos,
};
