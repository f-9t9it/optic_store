import {
  render_prescription,
  set_fields,
  setup_orx_name,
  apply_group_discount,
  handle_gift_card_entry,
} from './sales_order';

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

export const sales_invoice_gift_cards = {
  balance: set_gift_card_payment,
  os_gift_cards_remove: set_gift_card_payment,
};

export default {
  refresh: function(frm) {
    frm.set_query('gift_card', 'os_gift_cards', function() {
      return {
        filters: [['balance', '>', 0]],
      };
    });
    render_prescription(frm);
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
