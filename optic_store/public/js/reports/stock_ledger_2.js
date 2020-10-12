import { make_link, make_date, make_data } from './fields';

export default function stock_ledger_2() {
  return {
    filters: [
      make_link({
        fieldname: 'company',
        options: 'Company',
        default: frappe.defaults.get_user_default('Company'),
        reqd: 1,
      }),
      make_date({
        fieldname: 'from_date',
        default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        reqd: 1,
      }),
      make_date({
        fieldname: 'to_date',
        default: frappe.datetime.get_today(),
        reqd: 1,
      }),
      make_link({ fieldname: 'warehouse', options: 'Warehouse' }),
      make_link({
        fieldname: 'item_code',
        options: 'Item',
        get_query: function() {
          return {
            query: 'erpnext.controllers.queries.item_query',
          };
        },
      }),
      make_link({ fieldname: 'item_group', options: 'Item Group' }),
      make_link({ fieldname: 'batch_no', options: 'Batch' }),
      make_link({ fieldname: 'brand', options: 'Brand' }),
      make_data({ fieldname: 'voucher_no', label: __('Voucher #') }),
      make_link({ fieldname: 'project', options: 'Project' }),
    ],
  };
}
