import { make_link, make_data } from './fields';

export default {
  onload: async function(rep) {
    const scrap_warehouse = await frappe.db.get_single_value(
      'Optical Store Settings',
      'scrap_warehouse'
    );
    const filters = [
      ['is_group', '=', '0'],
      scrap_warehouse && ['name', '!=', scrap_warehouse],
    ];
    rep.get_filter('warehouse').get_query = { filters: filters.filter(x => !!x) };
  },
  filters: [
    make_link({ fieldname: 'warehouse', options: 'Warehouse' }),
    make_link({ fieldname: 'item_group', options: 'Item Group' }),
    make_link({ fieldname: 'brand', options: 'Brand' }),
    make_link({ fieldname: 'item_code', options: 'Item' }),
    make_data({ fieldname: 'item_name' }),
  ],
};
