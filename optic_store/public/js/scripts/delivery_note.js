import { set_cost_center, handle_items_cost_center } from './sales_invoice';

async function set_fields(frm) {
  const { message: branch } = await frappe.call({
    method: 'optic_store.api.customer.get_user_branch',
  });
  frm.set_value('os_branch', branch);
}

export const delivery_note_item = {
  items_add: handle_items_cost_center,
};

export default {
  onload: function(frm) {
    if (frm.is_new() && frm.doc.items.length > 0) {
      set_cost_center(frm);
    }
  },
  refresh: function(frm) {
    if (frm.doc.__islocal) {
      set_fields(frm);
    }
  },
  os_branch: set_cost_center,
};
