import {
  render_prescription,
  set_fields,
  setup_orx_name,
  apply_group_discount,
} from './sales_order';

function set_gift_card_payment(frm) {
  const row =
    (frm.get_field('payments').grid.grid_rows || [])
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
  frm.refresh_field('payments');
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
  os_gift_card_entry: async function(frm) {
    function set_desc(description) {
      frm.get_field('os_gift_card_entry').set_new_description(description);
    }
    const { posting_date, os_gift_card_entry: gift_card_no } = frm.doc;
    if (gift_card_no) {
      const already_added = (
        frm.get_field('os_gift_cards').grid.grid_rows || []
      )
        .map(({ doc }) => doc.gift_card)
        .includes(gift_card_no);
      if (already_added) {
        set_desc(__('Gift Card already present in Table'));
      } else {
        const { message: details } = await frappe.call({
          method: 'optic_store.api.gift_card.get_details',
          args: { gift_card_no, posting_date },
        });
        if (!details) {
          set_desc(__('Unable to find Gift Card'));
        } else {
          const { gift_card, balance, has_expired } = details;
          if (!balance) {
            set_desc(__('Gift Card balance is depleted'));
          } else if (has_expired) {
            set_desc(__('Gift Card has expired'));
          } else {
            // using this instead of just frm.add_child because
            // Sales Invoice Gift Card 'balance' can only be triggered by set_value
            const row = frappe.model.add_child(
              frm.doc,
              'Sales Invoice Gift Card',
              'os_gift_cards'
            );
            frappe.model.set_value(row.doctype, row.name, {
              gift_card,
              balance,
            });
            set_desc('');
            frm.refresh_field('os_gift_cards');
          }
          frm.set_value('os_gift_card_entry', null);
        }
      }
    }
    return false;
  },
  customer: setup_orx_name,
  orx_type: setup_orx_name,
  orx_name: render_prescription,
  orx_group_discount: apply_group_discount,
};
