// Copyright (c) 2016, 9T9IT and contributors
// For license information, please see license.txt
/* eslint-disable */

// this pattern is used instead of the packaged report settings because `onload` and
// `route_options` doesn't seem to work together. apparently it's possible to set only
// one `filter` value from `route_options` at a time.
frappe.query_reports['Customer-wise Invoice'] = {
  filters: [
    optic_store.reports.utils.make_date_range({
      fieldname: 'date_range',
      reqd: 1,
      default: [
        frappe.datetime.add_months('2017-12-12', -1),
        frappe.datetime.get_today(),
      ],
    }),
    optic_store.reports.utils.make_link({
      fieldname: 'customer',
      options: 'Customer',
      reqd: 1,
    }),
    optic_store.reports.utils.make_link({ fieldname: 'branch', options: 'Branch' }),
    optic_store.reports.utils.make_check({
      fieldname: 'item_wise',
      label: __('Show Item-wise'),
    }),
  ],
};
