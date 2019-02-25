// Copyright (c) 2019, 9T9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Optical Settings', {
  refresh: function(frm) {
    if (frm.doc.fixtures_installed !== 'Yes') {
      frm.add_custom_button('Install Fixtures', async function() {
        await frappe.call({
          method: 'optics_9t9it.api.install.setup_fixtures',
        });
        await frm.set_value('fixtures_installed', 'Yes');
        frm.save();
      });
    }
  },
});
