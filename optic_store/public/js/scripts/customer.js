import Vue from 'vue/dist/vue.js';

import CustomerDashboard from '../components/CustomerDashboard.vue';
import { NATIONALITIES } from '../utils/data';

async function set_branch(frm) {
  if (frm.doc.__islocal) {
    const { message: branch } = await frappe.call({
      method: 'optic_store.api.customer.get_user_branch',
    });
    frm.set_value('branch', branch);
  }
}

async function render_prescription_data(frm) {
  if (!frm.doc.__islocal) {
    const $wrapper = $('<div class="form-dashboard-section custom" />').appendTo(
      frm.dashboard.wrapper
    );
    const { message: props } = await frappe.call({
      method: 'optic_store.api.customer.get_dashboard_data',
      args: { customer: frm.doc.name },
    });
    if (props) {
      frm.prescription_chart_vue = new Vue({
        el: $wrapper.html('<div />').children()[0],
        render: h => h(CustomerDashboard, { props }),
      });
    }
  }
}

export function set_nationality_options(frm) {
  frm.set_df_property('os_nationality', 'options', ['', ...NATIONALITIES]);
}

export default {
  onload: function(frm) {
    set_branch(frm);
    set_nationality_options(frm);
  },
  refresh: render_prescription_data,
};
