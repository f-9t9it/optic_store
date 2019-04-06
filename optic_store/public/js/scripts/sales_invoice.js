export default {
  refresh: function(frm) {
    frm.set_query('gift_card', 'os_gift_cards', function() {
      return {
        filters: [['balance', '>', 0]],
      };
    });
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
            frm.add_child('os_gift_cards', { gift_card, balance });
            set_desc('');
            frm.refresh_field('os_gift_cards');
          }
          frm.set_value('os_gift_card_entry', null);
        }
      }
    }
    return false;
  },
};
