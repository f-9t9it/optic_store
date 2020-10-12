import { make_link, make_data } from './fields';

export default {
  onload: async function(rep) {
    const warehouse = rep.filters.find(({ fieldname }) => fieldname === 'warehouse');
    if (warehouse) {
      warehouse.df.read_only = !frappe.user_roles.includes('Sales Manager');
      warehouse.refresh();
    }
    const { message: user_warehouse } = await frappe.call({
      method: 'optic_store.api.customer.get_user_warehouse',
    });
    await rep.set_filter_value('warehouse', user_warehouse);
  },
  filters: [
    make_link({
      fieldname: 'brand',
      options: 'Brand',
    }),
    make_link({
      fieldname: 'item_group',
      options: 'Item Group',
    }),
    make_link({
      fieldname: 'warehouse',
      options: 'Warehouse',
    }),
    make_data({ fieldname: 'item_name' }),
  ],
};
