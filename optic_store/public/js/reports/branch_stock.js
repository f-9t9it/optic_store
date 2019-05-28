import { make_data, make_multiselect, make_check } from './fields';

export default {
  onload: async function(rep) {
    const hqm_view = rep.filters.find(({ fieldname }) => fieldname === 'hqm_view');
    if (hqm_view) {
      const has_role = frappe.user_roles.includes('Sales Manager');
      hqm_view.df.hidden = !has_role;
      hqm_view.refresh();
      rep.set_filter_value('hqm_view', has_role);
    }
  },
  filters: [
    make_multiselect({ fieldname: 'item_groups', options: 'Item Group' }),
    make_multiselect({ fieldname: 'brands', options: 'Brand' }),
    make_multiselect({ fieldname: 'item_codes', options: 'Item' }),
    make_data({ fieldname: 'item_name' }),
    make_check({ fieldname: 'hqm_view' }),
  ],
};
