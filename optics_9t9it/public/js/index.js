import sales_order from './scripts/sales_order';
import customer from './scripts/customer';
import item from './scripts/item';

frappe.ui.form.on('Sales Order', sales_order);
frappe.ui.form.on('Customer', customer);
frappe.ui.form.on('Item', item);
