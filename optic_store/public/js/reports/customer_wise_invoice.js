import { make_date_range, make_link, make_check } from './fields';

export default {
  onload: async function(rep) {
    rep.set_filter_value({
      date_range: [
        frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        frappe.datetime.get_today(),
      ],
    });
  },
  filters: [
    make_date_range({ fieldname: 'date_range', reqd: 1 }),
    make_link({ fieldname: 'customer', options: 'Customer', reqd: 1 }),
    make_link({ fieldname: 'branch', options: 'Branch' }),
    make_check({ fieldname: 'item_wise', label: __('Show Item-wise') }),
  ],
};
