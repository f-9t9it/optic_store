export default {
  refresh: function(frm) {
    if (frm.doc.__islocal) {
      frm.get_field('discount_name').set_focus();
    }
  },
};
