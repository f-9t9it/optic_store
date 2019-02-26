import Vue from 'vue/dist/vue.js';

import PrescriptionView from '../components/PrescriptionView.vue';

function orx_query(frm) {
  const { customer, orx_type: type } = frm.doc;
  if (customer && type) {
    frm.set_query('orx_name', function() {
      return {
        query: 'optics_9t9it.api.optical_prescription.query_latest',
        filters: { customer, type },
      };
    });
  }
}

export default {
  customer: orx_query,
  orx_type: orx_query,
  orx_name: async function(frm) {
    const { orx_name } = frm.doc;
    const { $wrapper } = frm.get_field('orx_html');
    $wrapper.empty();
    if (orx_name) {
      const doc = await frappe.db.get_doc('Optical Prescription', orx_name);
      frm.orx_vue = new Vue({
        el: $wrapper.html('<div />').children()[0],
        render: h => h(PrescriptionView, { props: { doc } }),
      });
    }
  },
};
