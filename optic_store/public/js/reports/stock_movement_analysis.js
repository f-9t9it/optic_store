import { make_link, make_data, make_date, make_select } from './fields';

export default function() {
  return {
    filters: [
      make_link({
        fieldname: 'item_group',
        options: 'Item Group',
      }),
      make_link({
        fieldname: 'brand',
        options: 'Brand',
      }),
      make_link({
        fieldname: 'item_code',
        options: 'Item',
      }),
      make_data({ fieldname: 'item_name' }),
      make_date({
        fieldname: 'query_date',
        options: 'Expiry Date',
        reqd: 1,
        default: frappe.datetime.get_today(),
      }),
      make_select({
        fieldname: 'period',
        options: ['Monthly', 'Yearly'],
        reqd: 1,
        default: 'Monthly',
      }),
    ],
  };
}
