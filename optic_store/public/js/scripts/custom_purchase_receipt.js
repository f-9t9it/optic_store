function toggle_enable_posting_datetime(frm) {
  return frm.toggle_enable('posting_datetime', frm.doc.set_posting_time);
}

function set_amount(frm, cdt, cdn) {
  const { qty = 0, rate = 0 } = frappe.get_doc(cdt, cdn);
  return frappe.model.set_value(cdt, cdn, 'amount', flt(qty) * flt(rate));
}

const custom_purchase_receipt_item = {
  qty: set_amount,
  rate: set_amount,
};

export default {
  custom_purchase_receipt_item,
  refresh: async function(frm) {
    if (!frm.doc.posting_datetime) {
      await frm.set_value('posting_datetime', frappe.datetime.now_datetime());
    }
    toggle_enable_posting_datetime(frm);
  },
  set_posting_time: toggle_enable_posting_datetime,
};
