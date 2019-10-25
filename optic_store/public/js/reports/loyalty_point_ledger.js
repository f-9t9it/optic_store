import { make_date_range, make_link } from './fields';

export default function loyalty_point_ledger() {
  return {
    filters: [
      make_date_range({
        fieldname: 'date_range',
        reqd: 1,
        default: [frappe.datetime.month_start(), frappe.datetime.month_end()],
      }),
      make_link({ fieldname: 'customer', options: 'Customer' }),
      make_link({ fieldname: 'loyalty_program', options: 'Loyalty Program' }),
    ],
  };
}
