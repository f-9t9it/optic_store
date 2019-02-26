import { sales_order, customer, item } from './scripts';

frappe.ui.form.on('Sales Order', sales_order);
frappe.ui.form.on('Customer', customer);
frappe.ui.form.on('Item', item);
