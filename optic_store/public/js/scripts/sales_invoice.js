import {
  render_prescription,
  set_fields,
  setup_orx_name,
  apply_group_discount,
  handle_gift_card_entry,
} from './sales_order';
import DeliverDialog from '../frappe-components/DeliverDialog';

function set_gift_card_payment(frm) {
  const payments = frm.get_field('payments');
  if (payments) {
    const row =
      (payments.grid.grid_rows || [])
        .map(({ doc }) => doc)
        .find(({ mode_of_payment }) => mode_of_payment === 'Gift Card') ||
      frappe.model.add_child(frm.doc, 'Sales Invoice Payment', 'payments');

    const amount = (frm.get_field('os_gift_cards').grid.grid_rows || [])
      .map(({ doc }) => doc.balance)
      .reduce((a, x = 0) => a + x, 0);
    const { rounded_total } = frm.doc;

    frappe.model.set_value(
      row.doctype,
      row.name,
      'amount',
      Math.min(amount, rounded_total)
    );
    payments.refresh();
  }
}

function render_deliver_button(frm) {
  if (frm.doc.docstatus === 1) {
    const actual_qty = frm.doc.items.reduce((a, { qty }) => a + qty, 0);
    const delivered_qty = frm.doc.items.reduce(
      (a, { delivered_qty }) => a + delivered_qty,
      0
    );
    if (delivered_qty < actual_qty) {
      frm.add_custom_button(__('Deliver & Print'), function() {
        frm.deliver_dialog && frm.deliver_dialog.create_and_print(frm);
      });
    } else {
      frm.add_custom_button(__('Print Invoice'), function() {
        frm.deliver_dialog && frm.deliver_dialog.print_invoice(frm);
      });
    }
  }
}

export const sales_invoice_gift_cards = {
  balance: set_gift_card_payment,
  os_gift_cards_remove: set_gift_card_payment,
};

export default {
  setup: async function(frm) {
    const { invoice_pfs = [] } = await frappe.db.get_doc(
      'Optical Store Settings'
    );
    const print_formats = invoice_pfs.map(({ print_format }) => print_format);
    frm.deliver_dialog = new DeliverDialog(print_formats);
  },
  refresh: function(frm) {
    frm.set_query('gift_card', 'os_gift_cards', function() {
      return {
        filters: [['balance', '>', 0]],
      };
    });
    render_prescription(frm);
    render_deliver_button(frm);
    if (frm.doc.__islocal) {
      set_fields(frm);
    }
  },
  os_gift_card_entry: handle_gift_card_entry,
  customer: setup_orx_name,
  orx_type: setup_orx_name,
  orx_name: render_prescription,
  orx_group_discount: apply_group_discount,
};
