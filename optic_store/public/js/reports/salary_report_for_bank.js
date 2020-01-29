import { make_date } from './fields';

export default function() {
  return {
    filters: [
      make_date({
        fieldname: 'start_date',
        options: 'Start Date',
        reqd: 1,
        default: frappe.datetime.month_start(),
      }),
      make_date({
        fieldname: 'end_date',
        options: 'End Date',
        reqd: 1,
        default: frappe.datetime.month_end(),
      }),
    ],
  };
}
