import scripts, {
  payment_entry,
  sales_invoice,
  sales_invoice_item,
  sales_invoice_list,
  sales_invoice_gift_card,
  delivery_note,
  delivery_note_item,
  sales_order,
  customer,
  employee,
  branch,
  item,
  customer_qe,
  optical_prescription_qe,
  batch_qe,
  stock_entry,
  salary_slip,
  payroll_entry,
} from './scripts';
import extend_query_report, { extend_multiselect } from './pages/query_report';
import extend_pos from './pages/pos';
import * as reports from './reports';
import * as addons from './addons';

frappe.ui.form.on('Payment Entry', payment_entry);
frappe.ui.form.on('Sales Invoice', sales_invoice);
frappe.ui.form.on('Sales Invoice Item', sales_invoice_item);
frappe.ui.form.on('Sales Invoice Gift Card', sales_invoice_gift_card);
frappe.ui.form.on('Delivery Note', delivery_note);
frappe.ui.form.on('Delivery Note Item', delivery_note_item);
frappe.ui.form.on('Stock Entry', stock_entry);
frappe.ui.form.on('Sales Order', sales_order);
frappe.ui.form.on('Sales Order Item', sales_order.sales_order_item);
frappe.ui.form.on('Customer', customer);
frappe.ui.form.on('Employee', employee);
frappe.ui.form.on('Branch', branch);
frappe.ui.form.on('Item', item);
frappe.ui.form.on('Salary Slip', salary_slip);
frappe.ui.form.on('Payroll Entry', payroll_entry);

if (frappe.ui.form.CustomerQuickEntryForm) {
  frappe.ui.form.CustomerQuickEntryForm = frappe.ui.form.CustomerQuickEntryForm.extend(
    customer_qe
  );
}

frappe.ui.form.OpticalPrescriptionQuickEntryForm = frappe.ui.form.QuickEntryForm.extend(
  optical_prescription_qe
);
frappe.ui.form.BatchQuickEntryForm = frappe.ui.form.QuickEntryForm.extend(batch_qe);

const __version__ = '0.9.1';

frappe.provide('optic_store');
optic_store = {
  __version__,
  scripts,
  reports,
  addons,
  extend_pos,
  listview: {
    sales_invoice: sales_invoice_list,
    stock_entry: stock_entry.listview_settings,
  },
};

frappe.views.QueryReport = extend_query_report(frappe.views.QueryReport);

frappe.ui.form.ControlMultiSelect = extend_multiselect(
  frappe.ui.form.ControlMultiSelect
);
