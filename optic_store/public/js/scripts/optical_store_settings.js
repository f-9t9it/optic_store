function pf_query_filter(doctype) {
  return [['doc_type', '=', doctype], ['print_format_type', '=', 'Server']];
}

export default {
  refresh: function(frm) {
    frm.set_query('print_format', 'order_pfs', (doc, cdt, cdn) => {
      const { is_invoice_pf = 0 } = frappe.get_doc(cdt, cdn) || {};
      return {
        filters: is_invoice_pf
          ? pf_query_filter('Sales Invoice')
          : pf_query_filter('Sales Order'),
      };
    });
    frm.set_query('print_format', 'invoice_pfs', {
      filters: pf_query_filter('Sales Invoice'),
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
          frm.reload_doc();
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
