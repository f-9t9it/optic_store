// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Simple Purchase Register'] = {
  filters: [
    {
      fieldname: 'from_date',
      label: __('From Date'),
      fieldtype: 'Date',
      required: 1,
      default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
    },
    {
      fieldname: 'to_date',
      label: __('To Date'),
      fieldtype: 'Date',
      required: 1,
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: 'supplier',
      label: __('Supplier'),
      fieldtype: 'Link',
      options: 'Supplier',
    },
    {
      fieldname: 'company',
      label: __('Company'),
      fieldtype: 'Link',
      options: 'Company',
      required: 1,
      default: frappe.defaults.get_user_default('Company'),
    },
    {
      fieldname: 'invoice_type',
      label: __('Invoice Type'),
      fieldtype: 'Select',
      options: ['Both', 'Purchases', 'Returns'],
      default: 'Both',
    },
  ],
};
