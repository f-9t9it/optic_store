// Copyright (c) 2019, 9T9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Optical Store Settings', {
  refresh: function(frm) {
    // hack to enable this button during development
    const development = true;
    if (development || frm.doc.defaults_installed !== 'Yes') {
      frm.add_custom_button('Setup Defaults', async function() {
        await frappe.call({
          method: 'optic_store.api.install.setup_defaults',
        });
        await frm.set_value('defaults_installed', 'Yes');
        frm.save();
      });
    }
  },
});
