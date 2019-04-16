import Vue from 'vue/dist/vue.js';

import PrescriptionForm from '../components/PrescriptionForm.vue';
import InvoiceDialog from '../frappe-components/InvoiceDialog';

export function setup_orx_name(frm) {
  const { customer, orx_type: type } = frm.doc;
  if (customer && type) {
    const orx_name = frm.get_docfield('orx_name');
    orx_name.get_route_options_for_new_doc = function(field) {
      return { customer, type };
    };
    frm.set_query('orx_name', function() {
      return {
        query: 'optic_store.api.optical_prescription.query_latest',
        filters: { customer, type },
      };
    });
  }
}

export async function render_prescription(frm) {
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
  if (frm.doc.docstatus === 1 && frm.doc.status !== 'Closed') {
    if (flt(frm.doc.per_billed, 6) < 100) {
      frm.add_custom_button(__('Invoice & Print'), function() {
        frm.invoice_dialog && frm.invoice_dialog.create_and_print(frm);
      });
    } else {
      frm.add_custom_button(__('Print Invoice'), function() {
        frm.invoice_dialog && frm.invoice_dialog.print_invoice(frm);
      });
    }
  }
}

export async function apply_group_discount(frm) {
  const { orx_group_discount } = frm.doc;
  const items = frm
    .get_field('items')
    .grid.grid_rows.map(({ doc: { doctype, name: docname, item_code } }) => ({
      doctype,
      docname,
      item_code,
    }));
  if (orx_group_discount) {
    try {
      const { message: discounts } = await frappe.call({
        method: 'optic_store.api.group_discount.get_item_discounts',
        args: {
          discount_name: orx_group_discount,
          item_codes: items.map(({ item_code }) => item_code),
        },
      });
      items.forEach(({ doctype, docname, item_code }) => {
        const { discount_rate = 0 } =
          discounts.find(d => d.item_code === item_code) || {};
        frappe.model.set_value(
          doctype,
          docname,
          'discount_percentage',
          discount_rate
        );
      });
    } catch (e) {
      frappe.throw(__('Cannot apply Group Discount'));
    }
  } else {
    items.forEach(({ doctype, docname }) => {
      frappe.model.set_value(doctype, docname, 'discount_percentage', 0);
    });
  }
}

function handle_order_type(frm) {
  const { os_order_type } = frm.doc;
  frm.toggle_display('orx_sec', ['Sales', 'Eye Test'].includes(os_order_type));
  if (os_order_type === 'Eye Test') {
    frm.set_query('item_code', 'items', function() {
      return {
        filters: { item_group: 'Services' },
      };
    });
  }
}

export async function set_fields(frm) {
  const [{ message: warehouse }, { message: branch }] = await Promise.all([
    frappe.call({
      method: 'optic_store.api.sales_order.get_warehouse',
      args: { user: frappe.session.user },
    }),
    frappe.call({
      method: 'optic_store.api.customer.get_user_branch',
    }),
  ]);
  frm.set_value('set_warehouse', warehouse);
  frm.set_value('os_branch', branch);
}

export default {
  setup: async function(frm) {
    const { invoice_pfs = [], invoice_mops = [] } = await frappe.db.get_doc(
      'Optical Store Settings'
    );
    const print_formats = invoice_pfs.map(({ print_format }) => print_format);
    const mode_of_payments = invoice_mops.map(
      ({ mode_of_payment }) => mode_of_payment
    );
    frm.invoice_dialog = new InvoiceDialog(print_formats, mode_of_payments);
  },
  refresh: function(frm) {
    render_prescription(frm);
    render_invoice_button(frm);
    handle_order_type(frm);
    if (frm.doc.__islocal) {
      set_fields(frm);
    }
  },
  customer: setup_orx_name,
  orx_type: setup_orx_name,
  orx_name: render_prescription,
  orx_group_discount: apply_group_discount,
};
