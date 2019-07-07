import startCase from 'lodash/startCase';

function make_base(fieldtype = 'Data', { fieldname, label = null, ...rest }) {
  return Object.assign(
    {
      fieldtype,
      fieldname,
      label: __(label || startCase(fieldname)),
    },
    rest
  );
}

export function make_data(args) {
  return make_base('Data', args);
}

export function make_date(args) {
  return make_base('Date', args);
}

export function make_check(args) {
  return make_base('Check', args);
}

export function make_link(args) {
  return make_base('Link', args);
}

export function make_select(args) {
  return make_base('Select', args);
}

export function make_multiselect(args) {
  const { fieldname, options } = args;
  return make_base(
    'MultiSelect',
    Object.assign(
      {
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
      args
    )
  );
}
