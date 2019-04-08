import Vue from 'vue/dist/vue.js';

import PrescriptionForm from '../components/PrescriptionForm.vue';

function enable_sph_reading(frm) {
  frm.toggle_enable('sph_reading_right', frm.doc.add_type_right === '');
  frm.toggle_enable('sph_reading_left', frm.doc.add_type_left === '');
}

function handle_add_sph(side) {
  return function(frm) {
    frm.set_value(
      `sph_reading_${side}`,
      parseFloat(frm.doc[`sph_${side}`]) + parseFloat(frm.doc[`add_${side}`])
    );
  };
}

function toggle_detail_entry(frm, state) {
  frm.toggle_display('details_simple_sec', !state);
  frm.toggle_display(['details_sec', 'pd_sec', 'prism_sec', 'iop_sec'], state);
}

function calc_total_pd(frm) {
  const { pd_right = 0, pd_left = 0 } = frm.doc;
  frm.set_value('pd_total', parseFloat(pd_right) + parseFloat(pd_left));
}

function update_fields(frm) {
  function scrub(field, value) {
    if (['va_right', 'va_left'].includes(field)) {
      return value.replace(/[^0-9\/]*/g, '');
    }
    if (['axis_right', 'axis_left'].includes(field)) {
      if (value < 0) {
        return 0;
      }
      return Math.min(value, 180);
    }
    if (['cyl_right', 'cyl_left'].includes(field)) {
      return Math.round(value * 4) / 4;
    }
    return value;
  }
  return function(field, value) {
    const scrubbed = scrub(field, value);
    frm.set_value(field, scrubbed);
    return scrubbed;
  };
}

function render_detail_vue(frm) {
  const { $wrapper } = frm.get_field('details_html');
  $wrapper.empty();
  if (frm.doc.__islocal) {
    // this makes the below fields reactive in vue
    frm.doc = Object.assign(frm.doc, {
      add_right: undefined,
      add_left: undefined,
      sph_reading_right: undefined,
      sph_reading_left: undefined,
      va_right: undefined,
      va_left: undefined,
      pd_total: undefined,
    });
  }
  return new Vue({
    el: $wrapper.html('<div />').children()[0],
    data: { doc: frm.doc },
    render: function(h) {
      return h(PrescriptionForm, {
        props: {
          doc: this.doc,
          update: update_fields(frm),
          fields: frm.fields_dict,
        },
      });
    },
  });
}

function setup_route_back(frm) {
  if (frappe._from_link && frappe._from_link.frm) {
    const { doctype, docname } = frappe._from_link.frm;
    // disable native route back for save events. will handle submits by own
    frappe._from_link.frm = null;
    return ['Form', doctype, docname];
  }
  return null;
}

function set_expiry_date(frm) {
  frm.set_value(
    'expiry_date',
    frappe.datetime.add_months(frm.doc.test_date, 6)
  );
}

export default {
  setup: async function(frm) {
    const { message: settings = {} } = await frappe.db.get_value(
      'Optical Store Settings',
      null,
      'prescription_entry'
    );
    toggle_detail_entry(frm, settings.prescription_entry === 'ERPNext');
  },
  onload: function(frm) {
    enable_sph_reading(frm);
    frm.detail_vue = render_detail_vue(frm);
    frm.route_back = setup_route_back(frm);
  },
  refresh: function(frm) {
    frm.detail_vue.doc = frm.doc;
    if (frm.doc.__islocal) {
      set_expiry_date(frm);
    }
  },
  test_date: set_expiry_date,
  on_submit: async function(frm) {
    if (frm.route_back) {
      await frappe.set_route(frm.route_back);
      if (frappe._from_link_scrollY) {
        frappe.utils.scroll_to(frappe._from_link_scrollY);
      }
    }
  },
  sph_right: handle_add_sph('right'),
  sph_left: handle_add_sph('left'),
  add_right: function(frm) {
    handle_add_sph('right')(frm);
    if (!frm.doc.add_left) {
      frm.set_value('add_left', frm.doc.add_right);
    }
  },
  add_left: handle_add_sph('left'),
  add_type_right: enable_sph_reading,
  add_type_left: enable_sph_reading,
  pd_right: calc_total_pd,
  pd_left: calc_total_pd,
};
