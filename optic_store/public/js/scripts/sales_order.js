import Vue from 'vue/dist/vue.js';

import PrescriptionForm from '../components/PrescriptionForm.vue';
import InvoiceDialog from '../frappe-components/InvoiceDialog';
import { SPEC_TYPES } from '../utils/data';

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
    frm.set_value('os_orx_notes', doc.notes);
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
        frm.invoice_dialog && frm.invoice_dialog.print(frm);
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
      return Promise.all(
        items.map(({ doctype, docname, item_code }) => {
          const { discount_rate = 0 } =
            discounts.find(d => d.item_code === item_code) || {};
          return frappe.model.set_value(
            doctype,
            docname,
            'discount_percentage',
            discount_rate
          );
        })
      );
    } catch (e) {
      frappe.throw(__('Cannot apply Group Discount'));
    }
  }
  return Promise.all(
    items.map(({ doctype, docname }) =>
      frappe.model.set_value(doctype, docname, 'discount_percentage', 0)
    )
  );
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

export async function set_gift_card(frm, gift_card_no) {
  function respond(message, clear_field = false) {
    return { clear_field, message };
  }

  if (!gift_card_no) {
    return respond('');
  }

  const already_added = frm.doc.os_gift_cards
    .map(({ gift_card }) => gift_card.toLowerCase())
    .includes(gift_card_no.toLowerCase());
  if (already_added) {
    return respond(__('Gift Card already selected for this transaction'));
  }

  const posting_date = frm.doc.posting_date || frm.doc.transaction_date;
  const { message: details } = await frappe.call({
    method: 'optic_store.api.gift_card.get_details',
    args: { gift_card_no, posting_date },
  });
  if (!details) {
    return respond(__('Unable to find Gift Card'));
  }

  const { gift_card, balance, has_expired } = details;
  if (!balance) {
    return respond(__('Gift Card balance is depleted'), true);
  }
  if (has_expired) {
    return respond(__('Gift Card has expired'), true);
  }

  // using this instead of just frm.add_child because
  // Sales Invoice Gift Card 'balance' can only be triggered by set_value
  const row = frappe.model.add_child(
    frm.doc,
    'Sales Invoice Gift Card',
    'os_gift_cards'
  );
  await frappe.model.set_value(row.doctype, row.name, { gift_card, balance });
  frm.refresh_field('os_gift_cards');
  return respond('', true);
}

export async function handle_gift_card_entry(frm) {
  const { os_gift_card_entry: gift_card_no } = frm.doc;
  const { clear_field, message } = await set_gift_card(frm, gift_card_no);
  if (clear_field) {
    await frm.set_value('os_gift_card_entry', null);
  }
  frm.get_field('os_gift_card_entry').set_new_description(message);
  return false;
}

export async function setup_employee_queries(frm) {
  const settings = await frappe.db.get_doc('Optical Store Settings');
  ['sales_person', 'dispensor', 'lab_tech']
    .map(employee => ({
      field: `os_${employee}`,
      department: settings[`${employee}_department`],
    }))
    .forEach(({ field, department }) => {
      frm.set_query(field, { filters: [['department', '=', department]] });
    });
}

export function set_spec_types_options(frm) {
  frm.set_df_property('os_type_of_spectacle', 'options', ['', ...SPEC_TYPES]);
}

async function set_naming_series(frm) {
  const { os_branch: branch } = frm.doc;
  if (branch) {
    const {
      message: { os_sales_order_naming_series } = {},
    } = await frappe.db.get_value('Branch', branch, 'os_sales_order_naming_series');
    frm.set_value('naming_series', os_sales_order_naming_series);
  }
}

export function hide_actions(frm) {
  // this is a hack to make native ui elements
  const hide_buttons = setInterval(() => {
    const make_btns = frm.page.inner_toolbar.find('div[data-label="Make"]');
    if (make_btns.length > 0) {
      make_btns.hide();
      clearInterval(hide_buttons);
    }
  }, 60);

  if (!frappe.user_roles.includes('System Manager')) {
    const hide_links = setInterval(() => {
      const links = frm.dashboard.links_area.find('div[data-doctype="Delivery Note"]');
      if (links.length > 0) {
        links.hide();
        clearInterval(hide_links);
      }
    }, 60);
  }
}

export default {
  setup: async function(frm) {
    const { order_pfs = [], invoice_mops = [] } = await frappe.db.get_doc(
      'Optical Store Settings'
    );
    const print_formats = order_pfs.map(({ print_format }) => print_format);
    const mode_of_payments = invoice_mops.map(({ mode_of_payment }) => mode_of_payment);
    frm.invoice_dialog = new InvoiceDialog(print_formats, mode_of_payments);

    const transaction_controller = new erpnext.TransactionController({ frm });
    if (frm.fields_dict['items'].grid.get_field('batch_no')) {
      frm.set_query('batch_no', 'items', function(doc, cdt, cdn) {
        return transaction_controller.set_query_for_batch(doc, cdt, cdn);
      });
    }
    transaction_controller.scan_barcode();
  },
  onload: function(frm) {
    setup_employee_queries(frm);
    set_spec_types_options(frm);
  },
  refresh: function(frm) {
    render_prescription(frm);
    render_invoice_button(frm);
    handle_order_type(frm);
    if (frm.doc.__islocal) {
      set_fields(frm);
    }
    hide_actions(frm);
  },
  customer: setup_orx_name,
  os_branch: set_naming_series,
  orx_type: setup_orx_name,
  orx_name: render_prescription,
  orx_group_discount: apply_group_discount,
  os_gift_card_entry: handle_gift_card_entry,
};
