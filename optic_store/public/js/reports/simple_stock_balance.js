import { make_link } from './fields';

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
  filters: [make_link({ fieldname: 'warehouse', options: 'Warehouse' })],
};
