import { make_date, make_multiselect } from './fields';

export default {
  onload: async function(rep) {
    rep.set_filter_value('posting_date', frappe.datetime.get_today());
    const { message: branch } = await frappe.call({
      method: 'optic_store.api.customer.get_user_branch',
    });
    rep.set_filter_value('branch', branch);
  },
  filters: [
    make_date({ fieldname: 'posting_date', label: 'Date', reqd: 1 }),
    make_multiselect({ fieldname: 'branch', options: 'Branch' }),
  ],
};
