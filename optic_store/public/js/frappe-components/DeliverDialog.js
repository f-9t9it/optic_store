import { print_invoice } from './InvoiceDialog';

export default class DeliverDialog {
  constructor(print_formats = []) {
    this.print_formats = print_formats;
    this.dialog = new frappe.ui.Dialog({
      title: 'Deliver & Print',
      fields: [
        {
          fieldname: 'payment_sec',
          fieldtype: 'Section Break',
          label: __('Payments'),
        },
        {
          fieldname: 'mode_of_payment',
          fieldtype: 'Link',
          options: 'Mode of Payment',
          label: __('Mode of Payment'),
        },
        {
          fieldname: 'gift_card_no',
          fieldtype: 'Data',
          label: __('Gift Card No'),
          hidden: 1,
        },
        {
          fieldname: 'gift_card_balance',
          fieldtype: 'Int',
          label: __('Gift Card Balance'),
          read_only: 1,
          hidden: 1,
        },
        {
          fieldtype: 'Column Break',
        },
        {
          fieldname: 'paid_amount',
          fieldtype: 'Currency',
          label: __('Amount to Pay'),
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
    this.init_state = {
      mode_of_payment: null,
      paid_amount: 0,
      gift_card_balance: 0,
    };
  }
  async create_and_print(frm) {
    this.state = Object.assign({}, this.init_state);

    this.dialog.fields_dict.mode_of_payment.change = async function() {
      const mode_of_payment = this.dialog.get_value('mode_of_payment');
      const is_gift_card = mode_of_payment === 'Gift Card';
      ['gift_card_no', 'gift_card_balance'].forEach(field =>
        this.dialog.fields_dict[field].toggle(is_gift_card)
      );
      this.state = Object.assign({}, this.state, { mode_of_payment });
    }.bind(this);

    this.dialog.fields_dict.gift_card_no.change = async function() {
      const gift_card_no = this.dialog.get_value('gift_card_no');
      await this.handle_gift_card(frm, gift_card_no);
      this.state = Object.assign({}, this.state, { gift_card_no });
    }.bind(this);

    this.dialog.fields_dict.paid_amount.change = async function() {
      const paid_amount = this.dialog.get_value('paid_amount') || 0;
      const min_amount =
        this.mode_of_payment === 'Gift Card'
          ? Math.min(this.state.gift_card_balance, frm.doc.outstanding_amount)
          : frm.doc.outstanding_amount;
      if (paid_amount > min_amount) {
        return frappe.throw(
          __(
            `Amount to Redeem cannot exceed ${format_currency(
              min_amount,
              frm.doc.currency
            )}`
          )
        );
      }
      this.state = Object.assign({}, this.state, { paid_amount });
    }.bind(this);

    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action(
      'OK',
      async function() {
        const { name } = frm.doc;
        const values = this.dialog.get_values();
        const enabled_print_formats = this.print_formats.filter(pf => values[pf]);
        const {
          mode_of_payment,
          paid_amount,
          gift_card_no,
          gift_card_balance = 0,
        } = values;
        this.dialog.fields_dict.paid_amount.change();
        if (mode_of_payment === 'Gift Card' && !gift_card_no) {
          return frappe.throw(__('Gift Card No is required'));
        }
        this.dialog.hide();
        const { message: { delivery_note, payment_entry } = {} } = await frappe.call({
          method: 'optic_store.api.sales_invoice.deliver_qol',
          freeze: true,
          freeze_message: __('Creating Payment Entry / Delivery Note'),
          args: { name, mode_of_payment, paid_amount, gift_card_no },
        });
        frm.reload_doc();
        enabled_print_formats.forEach(pf => {
          print_invoice(name, pf, 0);
        });
      }.bind(this)
    );

    this.dialog.set_df_property('payment_sec', 'hidden', 0);
    this.dialog.fields_dict.mode_of_payment.bind_change_event();
    this.dialog.fields_dict.paid_amount.bind_change_event();
    this.dialog.fields_dict.gift_card_no.bind_change_event();
    await this.dialog.set_values({
      mode_of_payment: 'Cash',
      paid_amount: frm.doc.outstanding_amount,
    });
    this.dialog.fields_dict.mode_of_payment.change();

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
      this.state = Object.assign({}, this.state, { gift_card_balance });
    } else {
      this.dialog.set_values({ gift_card_balance: 0 });
    }
  }
  async print_invoice(frm) {
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
    this.dialog.set_df_property('payment_sec', 'hidden', 1);
    this.dialog.show();
  }
}
