function toggle_naming(frm) {
  const { manual_item_code } = frm.doc;
  frm.toggle_display('item_code', manual_item_code);
  frm.toggle_reqd('item_code', manual_item_code);
  frm.toggle_display('naming_series', !manual_item_code);
}

export default {
  refresh: function(frm) {
    frm.toggle_display('manual_item_code', frm.doc.__islocal);
  },
  manual_item_code: toggle_naming,
};
