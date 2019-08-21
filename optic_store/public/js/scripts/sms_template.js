export default {
  onload: function(frm) {
    frm.set_query('ref_doctype', function() {
      return { filters: { istable: 0, issingle: 0 } };
    });
  },
};
