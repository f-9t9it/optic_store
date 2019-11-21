async function get_mops(current) {
  const { message: all } = await frappe.call({
    method: 'optic_store.api.email_alerts.get_mops',
  });

  return promised_dialog({ title: __('Select Modes of Payment'), all, current });
}

async function get_branches(current) {
  const { message: all } = await frappe.call({
    method: 'optic_store.api.email_alerts.get_branches',
  });
  return promised_dialog({ title: __('Select Branches'), all, current });
}

function promised_dialog({ title, all, current }) {
  const make_field = item => ({
    fieldtype: 'Check',
    fieldname: item,
    label: __(item),
    default: (current || '').split('\n').includes(item),
  });

  return new Promise(resolve => {
    const dialog = new frappe.ui.Dialog({
      title,
      fields: [
        ...all.filter((_, i) => !(i % 2)).map(make_field),
        { fieldtype: 'Column Break' },
        ...all.filter((_, i) => i % 2).map(make_field),
      ],
    });
    dialog.set_primary_action('OK', () => {
      const values = dialog.get_values();
      resolve(all.filter(item => values[item]));
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
  select_branch: async function(frm) {
    const { branches_to_show } = frm.doc;
    const branches = await get_branches(branches_to_show);
    frm.set_value('branches_to_show', branches.join('\n'));
  },
};
