export default {
  refresh: function(frm) {
    frm.set_query('default_print_format', {
      filters: [['doc_type', '=', 'Sales Invoice']],
    });
    frm.set_query('item_group', 'dashboard_item_groups', {
      filters: [['is_group', '=', '0']],
    });
    frm.set_query('gift_card_deferred_revenue', {
      filters: [['root_type', '=', 'Liability'], ['is_group', '=', '0']],
    });

    // hack to enable this button during development
    const development = true;
    if (development || frm.doc.defaults_installed !== 'Yes') {
      frm.add_custom_button('Setup Defaults', async function() {
        try {
          await frappe.call({
            method: 'optic_store.api.install.setup_defaults',
            freeze: true,
            freeze_message: __('Setting up defaults...'),
          });
          await frm.set_value('defaults_installed', 'Yes');
          await frm.save();
          frappe.show_alert({
            message: __('Defaults setup successfully'),
            indicator: 'green',
          });
        } catch (e) {
          frappe.throw(__('Something happened. Unable to setup defaults.'));
        }
      });
    }
  },
};
