import { make_link, make_date, make_check } from './fields';

export default function() {
  return {
    onload: async function(rep) {
      const warehouse_filter = rep.filters.find(
        ({ fieldname }) => fieldname === 'warehouse'
      );
      const is_manager = ['Item Manager', 'Stock Manager'].some(role =>
        frappe.user_roles.includes(role)
      );
      if (warehouse_filter && !is_manager) {
        warehouse_filter.df.read_only = !is_manager;
        warehouse_filter.refresh();
        const { message: warehouse } = await frappe.call({
          method: 'optic_store.api.customer.get_user_warehouse',
        });

        rep.set_filter_value('warehouse', warehouse);
      }
    },
    filters: [
      make_link({
        fieldname: 'company',
        options: 'Company',
        reqd: 1,
        default: frappe.defaults.get_user_default('company'),
      }),
      make_date({
        fieldname: 'query_date',
        options: 'Query Date',
        reqd: 1,
        default: frappe.datetime.get_today(),
      }),
      make_link({ fieldname: 'warehouse', options: 'Warehouse' }),
      make_link({ fieldname: 'item_group', options: 'Item Group' }),
      make_check({ fieldname: 'hide_zero_stock' }),
    ],
  };
}
