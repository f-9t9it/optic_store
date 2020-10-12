import { make_date, make_link, make_data, make_multiselect } from './fields';

export default {
  onload: async function(rep) {
    rep.set_filter_value({
      from_date: frappe.datetime.month_start(),
      to_date: frappe.datetime.month_end(),
    });
  },
  filters: [
    make_date({ fieldname: 'from_date', reqd: 1 }),
    make_date({ fieldname: 'to_date', reqd: 1 }),
    make_multiselect({ fieldname: 'branches', options: 'Branch' }),
    make_link({ fieldname: 'brand', options: 'Brand' }),
    make_link({ fieldname: 'item_code', options: 'Item' }),
    make_data({ fieldname: 'item_name' }),
    make_link({ fieldname: 'item_group', options: 'Item Group' }),
  ],
};
