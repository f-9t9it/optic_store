if (erpnext.stock.select_batch_and_serial_no) {
  const select_batch_and_serial_no = erpnext.stock.select_batch_and_serial_no;
  erpnext.stock.select_batch_and_serial_no = (frm, item) => {
    if (item && item.has_batch_no && frm.doc.purpose === 'Material Receipt') {
      frappe.require('assets/erpnext/js/utils/serial_no_batch_selector.js', function() {
        const SerialNoBatchSelector = optic_store.extend_batch_selector(
          erpnext.SerialNoBatchSelector
        );
        new SerialNoBatchSelector({
          frm: frm,
          item: item,
          warehouse_details: {
            type: 'Target Warehouse',
            name: cstr(item.t_warehouse) || '',
          },
        });
      });
    } else {
      select_batch_and_serial_no(frm, item);
    }
  };
}
