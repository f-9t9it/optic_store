['Sales Invoice', 'Sales Order', 'Stock Entry'].forEach(doctype => {
  frappe.ui.form.off(doctype, 'scan_barcode');
  frappe.ui.form.on(
    doctype,
    'scan_barcode',
    optic_store.scripts.extensions.scan_barcode
  );
});

if (['Sales Invoice'].includes(cur_frm.doctype)) {
  // this is necessary because batch_no set by scan_barcode overridden
  cur_frm.cscript.set_batch_number = function(cdt, cdn) {
    const doc = frappe.get_doc(cdt, cdn);
    if (doc && doc.has_batch_no && !doc.batch_no) {
      this._set_batch_number(doc);
    }
  };
}
