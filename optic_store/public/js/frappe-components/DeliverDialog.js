import { print_invoice } from './InvoiceDialog';

export default class DeliverDialog {
  constructor(print_formats = [], mode_of_payments = []) {
    this.mode_of_payments = mode_of_payments.map(mode_of_payment => ({
      mode_of_payment,
    }));
    this.print_formats = print_formats;
    this.dialog = new frappe.ui.Dialog({
      title: 'Deliver & Print',
      fields: [
        {
          fieldname: 'gift_card_sec',
          fieldtype: 'Section Break',
          label: __('Gift Card'),
        },
        {
          fieldname: 'gift_card_no',
          fieldtype: 'Data',
          label: __('Gift Card No'),
        },
        {
          fieldtype: 'Column Break',
        },
        {
          fieldname: 'gift_card_balance',
          fieldtype: 'Int',
          label: __('Gift Card Balance'),
          read_only: 1,
        },
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
  async payment(frm) {
    this.dialog.fields_dict.gift_card_no.change = async function() {
      const gift_card_no = this.dialog.get_value('gift_card_no');
      await this.handle_gift_card(frm, gift_card_no);
      this.set_payments(frm);
    }.bind(this);

    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action(
      'OK',
      async function() {
        const { name } = frm.doc;
        const values = this.dialog.get_values();
        const enabled_print_formats = this.print_formats.filter(pf => values[pf]);
        const { gift_card_no } = values;
        const payments = values.payments
          .filter(({ amount }) => amount)
          .map(({ mode_of_payment, amount }) =>
            Object.assign(
              {
                mode_of_payment,
                amount,
              },
              mode_of_payment === 'Gift Card' ? { gift_card_no } : {}
            )
          );
        if (
          payments.reduce((a, { amount = 0 }) => a + amount, 0) >
          frm.doc.outstanding_amount
        ) {
          return frappe.throw(__('Paid amount cannot be greater than outstanding'));
        }
        this.dialog.hide();
        await frappe.call({
          method: 'optic_store.api.sales_invoice.payment_qol',
          freeze: true,
          freeze_message: __('Creating Payment Entries'),
          args: { name, payments },
        });
        frm.reload_doc();
        enabled_print_formats.forEach(pf => {
          print_invoice(name, pf, 0);
        });
      }.bind(this)
    );

    this.dialog.set_df_property('gift_card_sec', 'hidden', 0);
    this.dialog.set_df_property('payment_sec', 'hidden', 0);
    this.dialog.fields_dict.gift_card_no.bind_change_event();

    this.set_payments(frm);
    await this.dialog.set_values({ gift_card_no: null, gift_card_balance: null });
    this.dialog.show();
  }
  async deliver(frm) {
    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action(
      'OK',
      async function() {
        const { name } = frm.doc;
        const values = this.dialog.get_values();
        const enabled_print_formats = this.print_formats.filter(pf => values[pf]);
        this.dialog.hide();
        await frappe.call({
          method: 'optic_store.api.sales_invoice.deliver_qol',
          freeze: true,
          freeze_message: __('Creating Payment Entry / Delivery Note'),
          args: { name },
        });
        frm.reload_doc();
        enabled_print_formats.forEach(pf => {
          print_invoice(name, pf, 0);
        });
      }.bind(this)
    );

    this.dialog.set_df_property('gift_card_sec', 'hidden', 1);
    this.dialog.set_df_property('payment_sec', 'hidden', 1);
    this.dialog.show();
  }
  async handle_gift_card(frm, gift_card_no) {
    if (gift_card_no) {
      const {
        message: { gift_card, balance: gift_card_balance = 0, has_expired } = {},
      } = await frappe.call({
        method: 'optic_store.api.gift_card.get_details',
        args: { gift_card_no, posting_date: frappe.datetime.get_today() },
      });
      if (!gift_card) {
        return frappe.throw(__('Gift Card not found'));
      }
      if (has_expired) {
        return frappe.throw(__('Gift Card expired'));
      }
      this.dialog.set_values({ gift_card_balance });
    } else {
      this.dialog.set_values({ gift_card_balance: 0 });
    }
  }
  set_payments(frm) {
    this.dialog.fields_dict.payments.grid.grid_rows.forEach(gr => {
      gr.doc.amount = 0;
      gr.refresh_field('amount');
    });

    let amount_to_set = frm.doc.outstanding_amount;
    const gift_card_balance = this.dialog.get_value('gift_card_balance');
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
  }
  async print(frm) {
    const print_formats = this.print_formats;
    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action('OK', function() {
      const { name } = frm.doc;
      const values = this.get_values();
      const enabled_print_formats = print_formats.filter(pf => values[pf]);
      this.hide();
      enabled_print_formats.forEach(pf => {
        print_invoice(name, pf, 0);
      });
    });
    this.dialog.set_df_property('gift_card_sec', 'hidden', 1);
    this.dialog.set_df_property('payment_sec', 'hidden', 1);
    this.dialog.show();
  }
}
