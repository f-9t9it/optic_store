import { make_date, make_data, make_multiselect, make_check } from './fields';

export default {
  onload: async function(rep) {
    const branches = rep.filters.find(({ fieldname }) => fieldname === 'branches');
    const has_role = ['Accounts Manager'].some(role =>
      frappe.user_roles.includes(role)
    );
    branches.df.hidden = !has_role;
    branches.refresh();
    rep.set_filter_value({
      from_date: frappe.datetime.month_start(),
      to_date: frappe.datetime.month_end(),
    });
  },
  filters: [
    make_date({ fieldname: 'from_date', reqd: 1 }),
    make_date({ fieldname: 'to_date', reqd: 1 }),
    make_multiselect({ fieldname: 'branches', hidden: 1, options: 'Branch' }),
    make_check({ fieldname: 'show_all' }),
  ],
};
