import { sales_order, customer, item, optical_prescription } from './scripts';

frappe.ui.form.on('Sales Order', sales_order);
frappe.ui.form.on('Customer', customer);
frappe.ui.form.on('Item', item);

frappe.provide('optic_store');
optic_store = { optical_prescription };
