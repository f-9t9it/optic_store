// Copyright (c) 2016, 9T9IT and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Daily Sales Summary'] = {
  onload: async function(rep) {
    const { message: branch } = await frappe.call({
      method: 'optic_store.api.customer.get_user_branch',
    });
    rep.set_filter_value('branch', branch);
  },
  filters: [
    {
      fieldname: 'posting_date',
      label: __('Date'),
      fieldtype: 'Date',
      reqd: 1,
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: 'branch',
      label: __('Branch'),
      fieldtype: 'Link',
      options: 'Branch',
      read_only: !frappe.user_roles.includes('Sales Manager'),
    },
  ],
};
