import Vue from 'vue/dist/vue.js';

import CustomerDashboard from '../components/CustomerDashboard.vue';

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
    const $wrapper = $(
      '<div class="form-dashboard-section custom" />'
    ).appendTo(frm.dashboard.wrapper);
    const { message: props } = await frappe.call({
      method: 'optic_store.api.customer.get_dashboard_data',
      args: { customer: frm.doc.name },
    });
    frm.prescription_chart_vue = new Vue({
      el: $wrapper.html('<div />').children()[0],
      render: h => h(CustomerDashboard, { props }),
    });
  }
}

export default {
  onload: set_branch,
  refresh: render_prescription_data,
};
