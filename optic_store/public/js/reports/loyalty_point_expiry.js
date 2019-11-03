import { make_date } from './fields';

export default function() {
  return {
    filters: [
      make_date({
        fieldname: 'expiry_date',
        options: 'Expiry Date',
        reqd: 1,
        default: frappe.datetime.get_today(),
      }),
    ],
  };
}
