export default function withLoyaltyCard(Payment) {
  const isClass = Payment instanceof Function || Payment instanceof Class;
  if (!isClass) {
    return Payment;
  }
  return class PaymentWithLoyaltyCard extends Payment {
    get_fields() {
      const fields = super.get_fields();
      const slice_idx = fields.findIndex(
        ({ fieldname }) => fieldname === 'redeem_loyalty_points'
      );

      const get_field_overrides = (field, idx) => {
        if (idx === slice_idx - 1) {
          return {
            label: 'Loyalty Program',
            collapsible: 1,
            collapsible_depends_on: 'redeem_loyalty_points',
          };
        }
        const { fieldname } = field;
        if (fieldname === 'redeem_loyalty_points') {
          const { onchange } = field;
          return {
            onchange: async function(e) {
              const redeem_loyalty_points = cint(
                this.dialog.get_value('redeem_loyalty_points')
              );
              // TODO: when PR #18111 is merged
              if (!cint(redeem_loyalty_points)) {
                await Promise.all([
                  this.frm.set_value('loyalty_points', 0),
                  this.dialog.set_value('loyalty_points', 0),
                ]);
              }
              onchange(e);
              this.dialog.set_df_property(
                'loyalty_card_no',
                'reqd',
                redeem_loyalty_points
              );
            }.bind(this),
          };
        }
        if (fieldname === 'loyalty_points') {
          return { read_only: 1 };
        }
        return {};
      };

      return [
        ...fields.slice(0, slice_idx + 1),
        {
          fieldname: 'loyalty_card_no',
          fieldtype: 'Data',
          label: __('Enter Loyalty Card No'),
          depends_on: 'redeem_loyalty_points',
          onchange: this.set_loyalty_card_no.bind(this),
        },
        ...fields.slice(slice_idx + 1),
      ].map((x, idx) => Object.assign(x, get_field_overrides(x, idx)));
    }
    async set_loyalty_card_no() {
      const loyalty_card_no = this.dialog.get_value('loyalty_card_no');
      if (loyalty_card_no) {
        try {
          // this is just to validate the loyalty card no
          await this.validate_loyalty_card_no();
        } catch (e) {
          this.frm.set_value('os_loyalty_card_no', null);
          this.frm.set_value('loyalty_points', 0);
          this.dialog.set_df_property('loyalty_points', 'read_only', 1);
          frappe.throw(e.message);
        }
      }
      this.frm.set_value('os_loyalty_card_no', loyalty_card_no);
      this.dialog.set_df_property('loyalty_points', 'read_only', !loyalty_card_no);
    }
    async validate_loyalty_card_no() {
      const { customer, posting_date: expiry_date, company } = this.frm.doc;
      const loyalty_card_no = this.dialog.get_value('loyalty_card_no');
      return frappe.call({
        method: 'optic_store.api.loyalty_program.get_customer_loyalty_details',
        args: { customer, loyalty_card_no, expiry_date, company },
      });
    }
    async validate() {
      await this.validate_loyalty_card_no();
      return super.validate();
    }
    async update_loyalty_points() {
      // TODO: when PR #18111 is merged
      const { loyalty_points, loyalty_amount } = this.frm.doc;
      await Promise.all([
        this.dialog.set_value('loyalty_points', loyalty_points),
        this.dialog.set_value('loyalty_amount', loyalty_amount),
      ]);
      this.update_payment_amount();
      this.show_paid_amount();
    }
  };
}
