// async function request(args) {

// }

export default class InvoiceDialog {
  constructor() {
    this.dialog = new frappe.ui.Dialog({
      title: 'Invoice & Print',
      fields: [
        {
          label: 'Mode of Payment',
          fieldname: 'mode_of_payment',
          fieldtype: 'Link',
          options: 'Mode of Payment',
        },
        {
          label: 'Amount',
          fieldname: 'amount',
          fieldtype: 'Currency',
        },
      ],
    });
  }
  async create_and_print(frm) {
    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action('OK', async function() {
      const { name } = frm.doc;
      const { mode_of_payment, amount } = this.get_values();
      this.hide();
      const {
        message: { sales_invoice_name, print_format, no_letterhead },
      } = await frappe.call({
        method: 'optic_store.api.sales_order.invoice_qol',
        freeze: true,
        freeze_message: __('Creating Sales Invoice'),
        args: { name, mode_of_payment, amount },
      });
      frm.reload_doc();

      // from /frappe/public/js/frappe/form/print.js
      const w = window.open(
        frappe.urllib.get_full_url(
          `/printview?doctype=${encodeURIComponent(
            'Sales Invoice'
          )}&name=${encodeURIComponent(
            sales_invoice_name
          )}&trigger_print=1&format=${encodeURIComponent(
            print_format
          )}&no_letterhead=${no_letterhead ? '1' : '0'}&_lang=en`
        )
      );
      if (!w) {
        frappe.msgprint(__('Please enable pop-ups'));
      }
    });

    const { message: settings = {} } = await frappe.db.get_value(
      'Optical Store Settings',
      null,
      'mode_of_payment'
    );
    await Promise.all([
      this.dialog.set_value('mode_of_payment', settings.mode_of_payment),
      this.dialog.set_value('amount', frm.doc.rounded_total),
    ]);
    this.dialog.show();
  }
}
