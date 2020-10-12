// Copyright (c) 2016, 9T9IT and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Monthly Sales Summary'] = {
  onload: async function(rep) {
    const { message: branch } = await frappe.call({
      method: 'optic_store.api.customer.get_user_branch',
    });
    rep.set_filter_value('branch', branch);
  },
  filters: [
    {
      fieldname: 'from_date',
      label: __('From Date'),
      fieldtype: 'Date',
      reqd: 1,
      default: frappe.datetime.add_days(
        frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        1
      ),
    },
    {
      fieldname: 'to_date',
      label: __('To Date'),
      fieldtype: 'Date',
      reqd: 1,
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: 'branch',
      label: __('Branch'),
      fieldtype: 'MultiSelect',
      read_only: !frappe.user_roles.includes('Sales Manager'),
      get_data: function() {
        const branches = frappe.query_report.get_filter_value('branch') || '';
        const values = branches.split(/\s*,\s*/).filter(d => d);
        const txt = branches.match(/[^,\s*]*$/)[0] || '';
        let data = [];
        frappe.call({
          type: 'GET',
          method: 'frappe.desk.search.search_link',
          async: false,
          no_spinner: true,
          args: {
            doctype: 'Branch',
            txt: txt,
            filters: { name: ['not in', values] },
          },
          callback: function({ results }) {
            data = results;
          },
        });
        return data;
      },
    },
  ],
};
