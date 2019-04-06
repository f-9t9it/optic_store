export default {
  refresh: function(frm) {
    if (!frm.doc.__islocal) {
      const { gift_card_no } = frm.doc;
      frm
        .add_custom_button('Write Off', async function() {
          await frappe.call({
            method: 'optic_store.api.gift_card.write_off',
            args: { gift_card_no, posting_date: frappe.datetime.get_today() },
          });
          frm.reload_doc();
        })
        .addClass(
          frappe.user_roles.includes('Sales Manager') ? null : 'disabled'
        );
    }
  },
};
