import sumBy from 'lodash/sumBy';

import { set_gift_card } from '../scripts/sales_order';

export default function withGiftCard(Payment) {
  const isClass = Payment instanceof Function || Payment instanceof Class;
  if (!isClass) {
    return Payment;
  }
  return class PaymentWithGiftCard extends Payment {
    get_fields() {
      const fields = super.get_fields();
      const slice_idx = fields.findIndex(({ fieldname }) => fieldname === 'numpad') + 1;
      return [
        ...fields.slice(0, slice_idx),
        {
          fieldtype: 'Section Break',
          label: __('Gift Card'),
          collapsible: 1,
          collapsible_depends_on: 'gift_card_no',
        },
        {
          fieldname: 'gift_card_no',
          fieldtype: 'Data',
          label: __('Enter Gift Card No'),
          onchange: this._set_gift_card_amounts.bind(this),
        },
        {
          fieldtype: 'Column Break',
        },
        {
          fieldname: 'gift_card_balance',
          fieldtype: 'Currency',
          label: __('Gift Card Balance'),
          read_only: 1,
        },
        ...fields.slice(slice_idx),
      ];
    }
    async _set_gift_card_amounts() {
      this.frm.clear_table('os_gift_cards');
      const { message } = await set_gift_card(
        this.frm,
        this.dialog.get_value('gift_card_no')
      );
      this.dialog.set_value(
        'gift_card_balance',
        sumBy(this.frm.doc.os_gift_cards, 'balance')
      );
      this.dialog.get_field('gift_card_no').set_description(message);
    }
  };
}
