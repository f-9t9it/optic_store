// Copyright (c) 2019, 9T9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Optical Settings', {
  refresh: function(frm) {
    if (frm.doc.defaults_installed !== 'Yes') {
      frm.add_custom_button('Setup Defaults', async function() {
        await frappe.call({
          method: 'optics_9t9it.api.install.setup_defaults',
        });
        await frm.set_value('defaults_installed', 'Yes');
        frm.save();
      });
    }
  },
});
