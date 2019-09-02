['Sales Order'].forEach(doctype => {
  frappe.ui.form.off(doctype, 'scan_barcode');
  frappe.ui.form.on(
    doctype,
    'scan_barcode',
    optic_store.scripts.extensions.scan_barcode
  );
});
