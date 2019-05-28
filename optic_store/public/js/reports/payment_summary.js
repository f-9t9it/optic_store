import { make_date, make_multiselect, make_check } from './fields';

export default {
  onload: async function(rep) {
    const branches = rep.filters.find(({ fieldname }) => fieldname === 'branches');
    if (branches) {
      branches.df.read_only = !frappe.user_roles.includes('Sales Manager');
      branches.refresh();
    }
    const { message: branch } = await frappe.call({
      method: 'optic_store.api.customer.get_user_branch',
    });
    rep.set_filter_value('branches', branch);
  },
  filters: [
    make_date({
      fieldname: 'start_date',
      reqd: 1,
      default: frappe.datetime.get_today(),
    }),
    make_date({
      fieldname: 'end_date',
      reqd: 1,
      default: frappe.datetime.get_today(),
    }),
    make_multiselect({
      fieldname: 'modes_of_payment',
      options: 'Mode of Payment',
    }),
    make_multiselect({
      fieldname: 'branches',
      options: 'Branch',
    }),
    make_check({
      fieldname: 'hide_returns',
    }),
  ],
};
