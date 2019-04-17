export const customer_qe_fields = [
  { fieldtype: 'Section Break', label: __('Details'), collapsible: 1 },
  { fieldtype: 'Column Break', label: __('Bio') },
  {
    fieldtype: 'Data',
    fieldname: 'os_short_name',
    label: __('Short Name'),
  },
  {
    fieldtype: 'Data',
    fieldname: 'os_crp_no',
    label: __('CRP No'),
  },
  {
    fieldtype: 'Date',
    fieldname: 'os_date_of_birth',
    label: __('Date of Birth'),
  },
  {
    fieldtype: 'Data',
    fieldname: 'os_occupation',
    label: __('Occupation'),
  },
  {
    fieldtype: 'Data',
    fieldname: 'os_nationality',
    label: __('Nationality'),
  },
  { fieldtype: 'Column Break', label: __('Contact') },
  {
    fieldtype: 'Data',
    fieldname: 'os_office_number',
    options: 'Phone',
    label: __('Office Number'),
  },
  {
    fieldtype: 'Data',
    fieldname: 'os_mobile_number',
    options: 'Phone',
    label: __('Mobile Number'),
  },
  {
    fieldtype: 'Data',
    fieldname: 'os_home_number',
    options: 'Phone',
    label: __('Home Number'),
  },
  {
    fieldtype: 'Data',
    fieldname: 'os_other_number',
    options: 'Phone',
    label: __('Other Number'),
  },
  {
    fieldtype: 'Data',
    fieldname: 'os_email',
    options: 'Email',
    label: __('Email'),
  },
  {
    fieldtype: 'Small Text',
    fieldname: 'os_address',
    label: __('Address'),
  },
];

export default {
  get_variant_fields: function() {
    return customer_qe_fields;
  },
};
