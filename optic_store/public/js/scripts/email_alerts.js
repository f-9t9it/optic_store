async function get_mops(current_mops) {
  const { message: mops } = await frappe.call({
    method: 'optic_store.api.email_alerts.get_mops',
  });

  const make_field = mop => ({
    fieldtype: 'Check',
    fieldname: mop,
    label: __(mop),
    default: (current_mops || '').split('\n').includes(mop),
  });

  return new Promise(resolve => {
    const dialog = new frappe.ui.Dialog({
      title: 'Select Modes of Payment',
      fields: [
        ...mops.filter((_, i) => !(i % 2)).map(make_field),
        { fieldtype: 'Column Break' },
        ...mops.filter((_, i) => i % 2).map(make_field),
      ],
    });
    dialog.set_primary_action('OK', () => {
      const values = dialog.get_values();
      resolve(mops.filter(mop => values[mop]));
      dialog.hide();
    });
    dialog.show();
  });
}

export const email_alerts_grouped_mop = {
  select: async function(frm, cdt, cdn) {
    const { mops: current_mops } = frappe.get_doc(cdt, cdn);
    const mops = await get_mops(current_mops);
    frappe.model.set_value(cdt, cdn, 'mops', mops.join('\n'));
  },
};

export default {
  email_alerts_grouped_mop,
};
