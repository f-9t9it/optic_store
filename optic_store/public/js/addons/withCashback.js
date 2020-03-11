import sumBy from 'lodash/sumBy';

export default function withCashback(Payment) {
  const isClass = Payment instanceof Function || Payment instanceof Class;
  if (!isClass) {
    return Payment;
  }
  return class PaymentWithCashback extends Payment {
    get_fields() {
      const fields = super.get_fields();
      const slice_idx =
        fields.findIndex(({ fieldname }) => fieldname === 'redeem_loyalty_points') - 1;
      return [
        ...fields.slice(0, slice_idx),
        {
          fieldtype: 'Section Break',
          label: __('Cashback'),
          collapsible: 1,
          collapsible_depends_on: 'cashback_receipt',
        },
        {
          label: __('Enter Cashback Receipt No'),
          fieldname: 'cashback_receipt',
          fieldtype: 'Link',
          options: 'Cashback Receipt',
          get_query: () => ({
            filters: [
              ['balance_amount', '>', 0],
              ['expiry_date', '>=', frappe.datetime.get_today()],
            ],
          }),
          onchange: this._set_cashback_amounts.bind(this),
        },
        {
          fieldtype: 'Column Break',
        },
        {
          fieldname: 'cashback_available',
          fieldtype: 'Currency',
          label: __('Cashback Available'),
          read_only: 1,
        },
        ...fields.slice(slice_idx),
      ];
    }
    async _set_cashback_amounts() {
      const cashback_receipt = this.dialog.get_value('cashback_receipt');
      if (cashback_receipt) {
        const {
          message: { balance_amount: cashback_available = 0 } = {},
        } = await frappe.db.get_value(
          'Cashback Receipt',
          cashback_receipt,
          'balance_amount'
        );
        this.dialog.set_values({ cashback_available });
      } else {
        this.dialog.set_values({ cashback_available: null });
      }
      this.frm.set_value('os_cashback_receipt', cashback_receipt);
    }
  };
}
