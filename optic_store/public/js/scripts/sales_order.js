import Vue from 'vue/dist/vue.js';

import PrescriptionForm from '../components/PrescriptionForm.vue';
import InvoiceDialog from '../frappe-components/InvoiceDialog';

function orx_query(frm) {
  const { customer, orx_type: type } = frm.doc;
  if (customer && type) {
    frm.set_query('orx_name', function() {
      return {
        query: 'optic_store.api.optical_prescription.query_latest',
        filters: { customer, type },
      };
    });
  }
}

async function render_prescription(frm) {
  const { orx_name } = frm.doc;
  const { $wrapper } = frm.get_field('orx_html');
  $wrapper.empty();
  if (orx_name) {
    const doc = await frappe.db.get_doc('Optical Prescription', orx_name);
    frm.orx_vue = new Vue({
      el: $wrapper.html('<div />').children()[0],
      render: h => h(PrescriptionForm, { props: { doc } }),
    });
  }
}

function render_invoice_button(frm) {
  // from /erpnext/selling/doctype/sales_order/sales_order.js
  if (
    frm.invoice_dialog &&
    frm.doc.docstatus === 1 &&
    frm.doc.status !== 'Closed'
  ) {
    if (flt(frm.doc.per_billed, 6) < 100) {
      frm.add_custom_button(__('Invoice & Print'), function() {
        frm.invoice_dialog.create_and_print(frm);
      });
    } else {
      frm.add_custom_button(__('Print Invoice'), function() {
        frm.invoice_dialog.print_invoice(frm);
      });
    }
  }
}

export default {
  setup: function(frm) {
    frm.invoice_dialog = new InvoiceDialog();
  },
  refresh: function(frm) {
    render_prescription(frm);
    render_invoice_button(frm);
  },
  customer: orx_query,
  orx_type: orx_query,
  orx_name: render_prescription,
};
