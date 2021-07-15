erpnext.pos.PointOfSale = optic_store.addons.extend_pos(erpnext.pos.PointOfSale);
POSCart = optic_store.addons.extend_cart(POSCart);
POSItems = optic_store.addons.extend_items(POSItems);
Payment = optic_store.addons.extend_payment(Payment);

// from erpnext/public/js/controllers/transaction.js
erpnext.show_serial_batch_selector = function (
  frm,
  d,
  callback,
  on_close,
  show_dialog
) {
  frappe.require('assets/erpnext/js/utils/serial_no_batch_selector.js', function () {
    erpnext.SerialNoBatchSelector = erpnext.SerialNoBatchSelector.extend(
      optic_store.scripts.serial_no_batch_selector
    );
    new erpnext.SerialNoBatchSelector(
      {
        frm: frm,
        item: d,
        warehouse_details: {
          type: 'Warehouse',
          name: d.warehouse,
        },
        callback: callback,
        on_close: on_close,
      },
      show_dialog
    );
  });
};
