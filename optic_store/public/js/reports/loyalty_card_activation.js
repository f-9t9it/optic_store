import { make_date_range, make_select, make_multiselect } from './fields';

export default function loyalty_card_activation() {
  return {
    filters: [
      make_date_range({
        fieldname: 'date_range',
        reqd: 1,
        default: [frappe.datetime.month_start(), frappe.datetime.month_end()],
      }),
      make_select({
        fieldname: 'interval',
        options: ['Daily', 'Weekly', 'Monthly', 'Yearly'],
        default: 'Daily',
      }),
      make_multiselect({ fieldname: 'branches', options: 'Branch' }),
    ],
  };
}
