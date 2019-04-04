function toggle_naming(frm) {
  const { manual_item_code } = frm.doc;
  frm.toggle_display('item_code', manual_item_code);
  frm.toggle_reqd('item_code', manual_item_code);
  frm.toggle_display('naming_series', !manual_item_code);
}

function enable_gift_card(frm) {
  const { is_gift_card } = frm.doc;
  frm.toggle_reqd('gift_card_value', is_gift_card);
  frm.set_value('has_serial_no', is_gift_card);
  frm.set_value('deferred_revenue_account', is_gift_card);
}

export default {
  refresh: function(frm) {
    frm.toggle_display('manual_item_code', frm.doc.__islocal);
  },
  manual_item_code: toggle_naming,
  is_gift_card: enable_gift_card,
};
