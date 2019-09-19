export default {
  onload: function(frm) {
    frm.set_df_property('purpose', 'options', ['Material Transfer']);
  },
  refresh: function(frm) {
    if (frm.doc.__islocal) {
      frm.set_value('purpose', 'Material Transfer');
    }
  },
};
