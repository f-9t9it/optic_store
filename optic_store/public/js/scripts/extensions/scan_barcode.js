function get_price(prices, price_list) {
  const { price_list_rate = 0 } = prices.find(p => p.price_list === price_list) || {};
  return price_list_rate;
}

export default async function scan_barcode_handler(frm) {
  function set_description(msg) {
    frm.fields_dict['scan_barcode'].set_new_description(__(msg));
  }

  const { scan_barcode: search_value, items } = frm.doc;

  if (search_value) {
    const { message: data } = await frappe.call({
      method:
        'erpnext.selling.page.point_of_sale.point_of_sale.search_serial_or_batch_or_barcode_number',
      args: { search_value },
    });
    if (!data || Object.keys(data).length === 0) {
      set_description('Cannot find Item with this barcode');
      return;
    }
    const row =
      items.find(({ item_code, batch_no }) => {
        if (batch_no) {
          return item_code == data.item_code && batch_no == data.batch_no;
        }
        return item_code === data.item_code;
      }) ||
      items.find(({ item_code }) => !item_code) ||
      frappe.model.add_child(frm.doc, frm.fields_dict['items'].grid.doctype, 'items');

    if (row.item_code) {
      set_description(`Row #${row.idx}: Qty increased by 1`);
    } else {
      set_description(`Row #${row.idx}:Item added`);
    }

    frm.from_barcode = true;

    const { qty = 0 } = row;
    await frappe.model.set_value(
      row.doctype,
      row.name,
      Object.assign(data, {
        qty: cint(frm.doc.is_return) ? qty - 1 : qty + 1,
      })
    );

    if (
      frappe.meta.has_field(row.doctype, 'os_minimum_selling_rate') &&
      (!row.os_minimum_selling_rate || !row.os_minimum_selling_2_rate)
    ) {
      const { message: prices } = await frappe.call({
        method: 'optic_store.api.item.get_prices',
        args: { item_code: row.item_code },
      });
      const os_minimum_selling_rate = get_price(prices, 'Minimum Selling');
      const os_minimum_selling_2_rate = get_price(prices, 'Minimum Selling 2');
      frappe.model.set_value(row.doctype, row.name, {
        os_minimum_selling_rate,
        os_minimum_selling_2_rate,
      });
    }

    frm.fields_dict['scan_barcode'].set_value('');
  }
  return false;
}
