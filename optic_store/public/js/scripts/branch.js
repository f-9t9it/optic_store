export default {
  refresh: async function(frm) {
    const { message: naming_series } = await frappe.call({
      method: 'optic_store.api.branch.get_naming_series',
    });
    if (naming_series) {
      const { sales_order, sales_invoice } = naming_series;
      frm.set_df_property('os_sales_order_naming_series', 'options', sales_order);
      frm.set_df_property('os_sales_invoice_naming_series', 'options', sales_invoice);
    }
  },
};
