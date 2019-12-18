import { make_date_range } from './fields';

export default function branch_wise_achieved_sales() {
  return {
    filters: [
      make_date_range({
        fieldname: 'date_range',
        reqd: 1,
        default: [frappe.datetime.month_start(), frappe.datetime.month_end()],
      }),
    ],
  };
}
