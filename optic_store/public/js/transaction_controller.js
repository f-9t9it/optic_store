frappe.ui.form.off(cur_frm.doctype, 'scan_barcode');
frappe.ui.form.on(
  cur_frm.doctype,
  'scan_barcode',
  optic_store.scripts.extensions.scan_barcode
);

if (['Sales Invoice', 'Delivery Note'].includes(cur_frm.doctype)) {
  // this is necessary because batch_no set by scan_barcode overridden
  cur_frm.cscript.set_batch_number = function(cdt, cdn) {
    const doc = frappe.get_doc(cdt, cdn);
    if (doc && doc.has_batch_no && !doc.batch_no) {
      this._set_batch_number(doc);
    }
  };
}
