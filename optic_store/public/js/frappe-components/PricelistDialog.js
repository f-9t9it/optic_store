export default class PricelistDialog {
  constructor(price_lists = []) {
    this.price_lists = price_lists;
    this.dialog = new frappe.ui.Dialog({
      title: 'Set Prices',
      fields: this.price_lists.map(pl => ({
        fieldtype: 'Currency',
        fieldname: pl,
        label: __(pl),
      })),
    });
    console.log(this.dialog);
  }
  async set_prices(frm) {
    const { message: prices } = await frappe.call({
      method: 'optic_store.api.item.get_prices',
      args: { item_code: frm.doc.item_code },
    });
    prices.forEach(({ price_list, price_list_rate }) => {
      this.dialog.replace_field(price_list, {
        fieldtype: 'Currency',
        fieldname: price_list,
        label: __(price_list),
        default: price_list_rate,
      });
    });
  }
  render_dialog(frm) {
    const price_lists = this.price_lists;
    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action('OK', async function() {
      const { name: item_code } = frm.doc;
      const values = this.get_values();
      const prices = price_lists.map(price_list => ({
        price_list,
        price_list_rate: values[price_list],
      }));
      this.hide();
      await frappe.call({
        method: 'optic_store.api.item.update_prices',
        args: { item_code, prices },
      });
      frm.reload_doc();
    });

    this.dialog.show();
  }
}
