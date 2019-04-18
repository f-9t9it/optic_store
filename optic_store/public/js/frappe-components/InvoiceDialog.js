export function print_invoice(sales_invoice_name, print_format, no_letterhead) {
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
}

export default class InvoiceDialog {
  constructor(print_formats = [], mode_of_payments = []) {
    this.mode_of_payments = mode_of_payments.map(mode_of_payment => ({
      mode_of_payment,
    }));
    this.print_formats = print_formats;
    this.dialog = new frappe.ui.Dialog({
      title: 'Invoice & Print',
      fields: [
        {
          fieldname: 'payment_sec',
          fieldtype: 'Section Break',
          label: __('Payments'),
        },
        {
          fieldname: 'payments',
          fieldtype: 'Table',
          fields: [
            {
              fieldname: 'mode_of_payment',
              fieldtype: 'Link',
              options: 'Mode of Payment',
              label: __('Mode of Payment'),
              in_list_view: 1,
            },
            {
              fieldname: 'amount',
              fieldtype: 'Currency',
              label: __('Amount'),
              in_list_view: 1,
            },
          ],
          in_place_edit: true,
          data: this.mode_of_payments,
          get_data: () => this.mode_of_payments,
        },
        {
          fieldname: 'print_sec',
          fieldtype: 'Section Break',
          label: __('Print Formats'),
        },
        ...this.print_formats.map(pf => ({
          fieldtype: 'Check',
          fieldname: pf,
          label: __(pf),
        })),
      ],
    });
  }
  create_and_print(frm) {
    const print_formats = this.print_formats;
    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action('OK', async function() {
      const { name } = frm.doc;
      const values = this.get_values();
      const enabled_print_formats = print_formats.filter(pf => values[pf]);
      const payments = values.payments.map(({ mode_of_payment, amount }) => ({
        mode_of_payment,
        amount,
      }));
      this.hide();
      const { message: sales_invoice_name } = await frappe.call({
        method: 'optic_store.api.sales_order.invoice_qol',
        freeze: true,
        freeze_message: __('Creating Sales Invoice'),
        args: { name, payments },
      });
      frm.reload_doc();
      enabled_print_formats.forEach(pf => {
        print_invoice(sales_invoice_name, pf, 0);
      });
    });

    this.dialog.set_df_property('payment_sec', 'hidden', 0);
    let amount_to_set = frm.doc.rounded_total;
    const gift_card_balance = frm.doc.os_gift_cards.reduce(
      (a, { balance }) => a + balance,
      0
    );
    const gift_card_gr = this.dialog.fields_dict.payments.grid.grid_rows.find(
      ({ doc }) => doc.mode_of_payment === 'Gift Card'
    );
    if (gift_card_balance && gift_card_gr) {
      gift_card_gr.doc.amount = Math.min(gift_card_balance, amount_to_set);
      gift_card_gr.refresh_field('amount');
      amount_to_set -= gift_card_gr.doc.amount;
    }
    const first_payment_gr = this.dialog.fields_dict.payments.grid.grid_rows.filter(
      ({ doc }) => doc.mode_of_payment !== 'Gift Card'
    )[0];
    if (first_payment_gr) {
      first_payment_gr.doc.amount = amount_to_set;
      first_payment_gr.refresh_field('amount');
    }
    this.dialog.show();
  }
  async print_invoice(frm) {
    const print_formats = this.print_formats;
    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action('OK', async function() {
      const { name } = frm.doc;
      const values = this.get_values();
      const enabled_print_formats = print_formats.filter(pf => values[pf]);
      this.hide();
      const { message: invoices = [] } = await frappe.call({
        method: 'optic_store.api.sales_order.get_invoice',
        args: { name },
      });
      invoices.forEach(sales_invoice_name => {
        enabled_print_formats.forEach(pf => {
          print_invoice(sales_invoice_name, pf, 0);
        });
      });
    });
    this.dialog.set_df_property('payment_sec', 'hidden', 1);
    this.dialog.show();
  }
}
