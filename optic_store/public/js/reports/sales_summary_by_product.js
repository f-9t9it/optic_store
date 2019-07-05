import { make_date, make_multiselect, make_select } from './fields';

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
    make_select({
      fieldname: 'report_type',
      reqd: 1,
      options: ['Achieved', 'Collected'],
    }),
  ],
};
