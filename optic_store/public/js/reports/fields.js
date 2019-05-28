import startCase from 'lodash/startCase';

export function make_date({ fieldname, label = null, ...rest }) {
  return Object.assign(
    {
      fieldname: fieldname,
      label: __(label || startCase(fieldname)),
      fieldtype: 'Date',
    },
    rest
  );
}

export function make_check({ fieldname, label = null, ...rest }) {
  return Object.assign(
    {
      fieldname: fieldname,
      label: __(label || startCase(fieldname)),
      fieldtype: 'Check',
    },
    rest
  );
}

export function make_multiselect({ fieldname, options, label = null, ...rest }) {
  return Object.assign(
    {
      fieldname,
      label: __(label || startCase(fieldname)),
      fieldtype: 'MultiSelect',
      get_data: function() {
        const values = frappe.query_report.get_filter_value(fieldname) || '';
        const names = values.split(/\s*,\s*/).filter(d => d);
        const txt = values.match(/[^,\s*]*$/)[0] || '';
        let data = [];
        frappe.call({
          type: 'GET',
          method: 'frappe.desk.search.search_link',
          async: false,
          no_spinner: true,
          args: { doctype: options, txt: txt, filters: { name: ['not in', names] } },
          callback: function({ results }) {
            data = results;
          },
        });
        return data;
      },
    },
    rest
  );
}
