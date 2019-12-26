function will_hide_new_action() {
  return (
    frappe.user_roles.includes('Branch User') &&
    !frappe.user_roles.includes('Stock Manager')
  );
}

const listview_settings = {
  onload: function(lv) {
    if (will_hide_new_action()) {
      lv.page.btn_primary.hide();
    }
  },
};

export default {
  listview_settings,
  onload: function(frm) {
    if (!['Stock Manager'].some(role => frappe.user_roles.includes(role))) {
      frm.set_df_property('purpose', 'options', ['Material Transfer']);
    }
  },
  refresh: function(frm) {
    if (will_hide_new_action()) {
      frm.page.menu
        .find(`a:contains('${__('New Stock Entry')}')`)
        .parent()
        .addClass('hidden');
    }
    if (
      !['Stock Manager'].some(role => frappe.user_roles.includes(role)) &&
      frm.doc.__islocal
    ) {
      frm.set_value('purpose', 'Material Transfer');
    }
  },
};
