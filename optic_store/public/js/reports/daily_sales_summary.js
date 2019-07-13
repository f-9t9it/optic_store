import { make_date, make_multiselect } from './fields';

export default {
  onload: async function(rep) {
    rep.set_filter_value('posting_date', frappe.datetime.get_today());
    const { message: branch } = await frappe.call({
      method: 'optic_store.api.customer.get_user_branch',
    });
    rep.set_filter_value('branch', branch);
    const branch_filter = rep.filters.find(({ fieldname }) => fieldname === 'hqm_view');
    if (branch_filter) {
      const has_role = ['Sales Manager'].some(role => frappe.user_roles.includes(role));
      branch_filter.df.read_only = !has_role;
      branch_filter.refresh();
    }
  },
  filters: [
    make_date({ fieldname: 'posting_date', label: 'Date', reqd: 1 }),
    make_multiselect({ fieldname: 'branch', options: 'Branch' }),
  ],
};
