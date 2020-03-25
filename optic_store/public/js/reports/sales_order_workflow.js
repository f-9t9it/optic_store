import { make_link, make_date_range, make_check } from './fields';

export default function() {
  return {
    filters: [
      make_date_range({
        fieldname: 'date_range',
        reqd: 1,
        default: [frappe.datetime.month_start(), frappe.datetime.month_end()],
      }),
      make_link({ fieldname: 'branch', options: 'Branch' }),
      make_check({ fieldname: 'show_collected' }),
    ],
  };
}
