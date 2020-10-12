export default {
  render_dialog: async function() {
    this._super();
    if (cur_frm) {
      const { doctype, item_code } = cur_frm.selected_doc || {};
      if (
        [
          'Stock Entry Detail',
          'Purchase Receipt Item',
          'Purchase Invoice Item',
        ].includes(doctype)
      ) {
        this.dialog.set_value('item', item_code);
        const { message: item = {} } = await frappe.db.get_value('Item', item_code, [
          'create_new_batch',
          'has_expiry_date',
        ]);
        if (cint(item.create_new_batch)) {
          const field = this.dialog.get_field('batch_id');
          field.df.reqd = 0;
          field.df.bold = 1;
          field.refresh();
        }
        if (cint(item.has_expiry_date)) {
          const field = this.dialog.get_field('expiry_date');
          field.df.reqd = 1;
          field.refresh();
        }
      }
    }
  },
};
