POSCart = optic_store.addons.extend_cart(POSCart);

erpnext.show_serial_batch_selector = function(frm, d, callback, on_close, show_dialog) {
  frappe.require('assets/erpnext/js/utils/serial_no_batch_selector.js', function() {
    const SerialNoBatchSelector = frappe.get_route().includes('point-of-sale')
      ? optic_store.extend_batch_selector(erpnext.SerialNoBatchSelector)
      : erpnext.SerialNoBatchSelector;
    new SerialNoBatchSelector(
      {
        frm: frm,
        item: d,
        warehouse_details: { type: 'Warehouse', name: d.warehouse },
        callback: callback,
        on_close: on_close,
      },
      show_dialog
    );
  });
};
