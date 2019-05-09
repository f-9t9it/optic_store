// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Item Consumption'] = {
  filters: [
    {
      fieldname: 'company',
      label: __('Company'),
      fieldtype: 'Link',
      options: 'Company',
      reqd: 1,
      default: frappe.defaults.get_user_default('company'),
    },
    {
      fieldname: 'start_date',
      label: __('Start Date'),
      fieldtype: 'Date',
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: 'end_date',
      label: __('End Date'),
      fieldtype: 'Date',
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: 'interval',
      label: __('Interval'),
      fieldtype: 'Select',
      options: '\nWeekly\nMonthly\nYearly',
    },
    {
      fieldname: 'warehouse',
      label: __('Warehouse'),
      fieldtype: 'Link',
      options: 'Warehouse',
      get_query: { filters: { is_group: 0 } },
    },
  ],
};
