import { make_date, make_select } from './fields';

export default function() {
  return {
    filters: [
      make_date({
        fieldname: 'start_date',
        options: 'Start Date',
        reqd: 1,
        default: frappe.datetime.month_start(),
      }),
      make_select({
        fieldname: 'report_type',
        reqd: 1,
        options: ['Type 1', 'Type 2'],
        default: 'Type 1',
      }),
      make_select({
        fieldname: 'status',
        reqd: 1,
        options: ['Draft', 'Submitted'],
        default: 'Submitted',
      }),
    ],
  };
}
