// Copyright (c) 2016, 9T9IT and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Brand-wise Stock'] = {
  onload: async function(rep) {
    const { message: warehouse } = await frappe.call({
      method: 'optic_store.api.customer.get_user_warehouse',
    });
    rep.set_filter_value('warehouse', warehouse);
  },
  filters: [
    {
      fieldname: 'brand',
      label: __('Brand'),
      fieldtype: 'Link',
      options: 'Brand',
    },
    {
      fieldname: 'item_group',
      label: __('Item Group'),
      fieldtype: 'Link',
      options: 'Item Group',
    },
    {
      fieldname: 'warehouse',
      label: __('Warehouse'),
      fieldtype: 'Link',
      options: 'Warehouse',
      read_only: !frappe.user_roles.includes('Sales Manager'),
    },
  ],
};
