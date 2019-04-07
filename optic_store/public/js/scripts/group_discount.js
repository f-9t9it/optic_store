export default {
  refresh: function(frm) {
    if (frm.doc.__islocal) {
      frm.get_field('discount_name').set_focus();
      frappe.model.add_child(
        frm.doc,
        'Group Discount Brand Category',
        'discounts'
      );
      frm.refresh_field('discounts');
    }
  },
};
