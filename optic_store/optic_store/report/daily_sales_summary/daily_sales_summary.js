// Copyright (c) 2016, 9T9IT and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Daily Sales Summary'] = {
  filters: [
    {
      fieldname: 'from_date',
      label: __('From Date'),
      fieldtype: 'Date',
      default: frappe.datetime.add_days(
        frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        1
      ),
    },
    {
      fieldname: 'to_date',
      label: __('To Date'),
      fieldtype: 'Date',
      default: frappe.datetime.get_today(),
    },
  ],
};
