import pick from 'lodash/pick';
import groupBy from 'lodash/groupBy';
import mapValues from 'lodash/mapValues';
import sumBy from 'lodash/sumBy';
import isEqual from 'lodash/isEqual';

import { print_doc, set_amount } from './InvoiceDialog';

export default class DeliverDialog {
  constructor(print_formats = [], mode_of_payments = []) {
    this.mode_of_payments = mode_of_payments.map(mode_of_payment => ({
      mode_of_payment,
    }));
    this.print_formats = print_formats;
    this.batches = [];
    this.warehouse = null;
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
          fieldname: 'batch_sec',
          fieldtype: 'Section Break',
          label: __('Batches'),
        },
        {
          fieldname: 'batches',
          fieldtype: 'Table',
          fields: [
            {
              fieldname: 'item_code',
              fieldtype: 'Link',
              options: 'Item',
              label: __('Item Code'),
              read_only: 1,
              in_list_view: 1,
            },
            {
              fieldname: 'batch_no',
              fieldtype: 'Link',
              options: 'Batch',
              label: __('Batch No'),
              in_list_view: 1,
              get_query: function({ item_code }) {
                return { filters: { item: item_code } };
              },
            },
            {
              fieldname: 'available_qty',
              fieldtype: 'Float',
              label: __('Available Qty'),
              read_only: 1,
              in_list_view: 1,
            },
            {
              fieldname: 'qty',
              fieldtype: 'Float',
              label: __('Invoice Qty'),
              in_list_view: 1,
            },
          ],
          in_place_edit: true,
          data: this.batches,
          get_data: () => this.batches,
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
          default: 1,
        })),
      ],
    });
  }
  async payment_and_deliver(frm, deliver = false) {
    this.dialog.fields_dict.gift_card_no.change = async function() {
      const gift_card_no = this.dialog.get_value('gift_card_no');
      await this.handle_gift_card(frm, gift_card_no);
      this.set_payments(frm);
    }.bind(this);

    const { message: warehouse } = await frappe.call({
      method: 'optic_store.api.sales_order.get_warehouse',
      args: { branch: frm.doc.os_branch },
    });
    this.dialog.fields_dict.batches.grid.fields_map.batch_no.change = async function() {
      const { item_code, batch_no } = this.doc;
      const set_value = qty =>
        this.grid_row.on_grid_fields_dict.available_qty.set_value(qty);
      if (!warehouse || !batch_no) {
        return set_value(0);
      }
      const { message: available_qty } = await frappe.call({
        method: 'erpnext.stock.doctype.batch.batch.get_batch_qty',
        args: { batch_no, item_code, warehouse },
      });
      if (typeof available_qty !== 'number') {
        return set_value(0);
      }
      return set_value(available_qty);
    };

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
        const total_paid = flt(
          payments.reduce((a, { amount = 0 }) => a + amount, 0),
          precision('outstanding_amount')
        );
        if (total_paid > frm.doc.outstanding_amount) {
          return frappe.throw(__('Paid amount cannot be greater than outstanding'));
        }
        if (deliver && total_paid !== frm.doc.outstanding_amount) {
          return frappe.throw(__('Paid amount must be equal to outstanding'));
        }
        try {
          await frappe.call({
            method: 'optic_store.api.sales_invoice.deliver_qol',
            freeze: true,
            freeze_message: __('Creating Payment Entry / Delivery Note'),
            args: {
              name,
              payments,
              deliver: deliver ? 1 : 0,
              batches: deliver
                ? values.batches
                    .filter(({ batch_no, qty }) => batch_no && qty)
                    .map(batch => pick(batch, ['item_code', 'batch_no', 'qty']))
                : null,
            },
          });
          this.dialog.hide();
          enabled_print_formats.forEach(pf => {
            print_doc('Sales Invoice', name, pf, 0);
          });
        } finally {
          frm.reload_doc();
        }
      }.bind(this)
    );

    this.dialog.set_df_property(
      'gift_card_sec',
      'hidden',
      frm.doc.outstanding_amount > 0 ? 0 : 1
    );
    this.dialog.set_df_property(
      'payment_sec',
      'hidden',
      frm.doc.outstanding_amount > 0 ? 0 : 1
    );
    this.dialog.fields_dict.gift_card_no.bind_change_event();

    await this.set_batches(frm, warehouse); // this will set this.batches
    this.dialog.set_df_property(
      'batch_sec',
      'hidden',
      deliver && this.batches.length > 0 ? 0 : 1
    );

    await this.dialog.set_values({ gift_card_no: null, gift_card_balance: null });
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
      set_amount(gr, 0);
    });

    let amount_to_set = frm.doc.outstanding_amount;
    const gift_card_balance = this.dialog.get_value('gift_card_balance');
    const gift_card_gr = this.dialog.fields_dict.payments.grid.grid_rows.find(
      ({ doc }) => doc.mode_of_payment === 'Gift Card'
    );
    if (gift_card_balance && gift_card_gr) {
      set_amount(gift_card_gr, Math.min(gift_card_balance, amount_to_set));
      amount_to_set -= gift_card_gr.doc.amount;
    }
    const first_payment_gr = this.dialog.fields_dict.payments.grid.grid_rows.filter(
      ({ doc }) => doc.mode_of_payment !== 'Gift Card'
    )[0];
    if (first_payment_gr) {
      set_amount(first_payment_gr, amount_to_set);
    }
  }
  async _get_batch_items(items, warehouse) {
    const has_batch_results = await Promise.all(
      items.map(({ item_code }) =>
        frappe.db.get_value('Item', item_code, ['item_code', 'has_batch_no'])
      )
    );
    const batch_items = has_batch_results
      .map(({ message = {} }) => message)
      .filter(({ has_batch_no }) => has_batch_no)
      .map(({ item_code }) => item_code);
    const rows = items
      .filter(({ item_code }) => batch_items.includes(item_code))
      .map(item => pick(item, ['item_code', 'batch_no', 'qty']));
    const qty_results = await Promise.all(
      rows.map(({ item_code, batch_no }) =>
        batch_no
          ? frappe.call({
              method: 'erpnext.stock.doctype.batch.batch.get_batch_qty',
              args: { batch_no, item_code, warehouse },
            })
          : {}
      )
    );
    const qtys = qty_results.map(({ message = {} }) =>
      typeof message === 'number' ? message : null
    );
    return rows.map((item, idx) => Object.assign(item, { available_qty: qtys[idx] }));
  }
  async set_batches(frm, warehouse) {
    this.batches = await this._get_batch_items(frm.doc.items, warehouse);
    this.dialog.fields_dict.batches.refresh();
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
        print_doc('Sales Invoice', name, pf, 0);
      });
    });
    this.dialog.set_df_property('gift_card_sec', 'hidden', 1);
    this.dialog.set_df_property('payment_sec', 'hidden', 1);
    this.dialog.show();
  }
}
