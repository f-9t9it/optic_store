import Vue from 'vue/dist/vue.js';

import PrescriptionForm from '../components/PrescriptionForm.vue';

function enable_sph_reading(frm) {
  frm.toggle_enable('sph_reading_right', frm.doc.add_type_right === '');
  frm.toggle_enable('sph_reading_left', frm.doc.add_type_left === '');
}

function handle_add_sph(frm) {
  const { sph_right = 0, add_right = 0, sph_left = 0, add_left = 0 } = frm.doc;
  frm.set_value(
    'sph_reading_right',
    parseFloat(sph_right) + parseFloat(add_right)
  );
  frm.set_value(
    'sph_reading_left',
    parseFloat(sph_left) + parseFloat(add_left)
  );
}

function toggle_detail_entry(frm, state) {
  frm.toggle_display('details_simple_sec', !state);
  frm.toggle_display(['details_sec', 'pd_sec', 'prism_sec', 'iop_sec'], state);
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
    const { $wrapper } = frm.get_field('details_html');
    $wrapper.empty();
    frm.detail_vue = new Vue({
      el: $wrapper.html('<div />').children()[0],
      data: { doc: frm.doc },
      render: function(h) {
        return h(PrescriptionForm, {
          props: {
            doc: this.doc,
            update: (field, value) => frm.set_value(field, value),
          },
        });
      },
    });
  },
  refresh: function(frm) {
    frm.detail_vue.doc = frm.doc;
  },
  sph_right: handle_add_sph,
  sph_left: handle_add_sph,
  add_right: handle_add_sph,
  add_left: handle_add_sph,
  add_type_right: enable_sph_reading,
  add_type_left: enable_sph_reading,
};
