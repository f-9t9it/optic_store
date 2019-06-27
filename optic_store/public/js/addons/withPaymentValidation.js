import sumBy from 'lodash/sumBy';

export default function withPaymentValidation(Payment) {
  const isClass = Payment instanceof Function || Payment instanceof Class;
  if (!isClass) {
    return Payment;
  }
  return class PaymentWithPaymentValidation extends Payment {
    set_primary_action() {
      // complete override to validate exact payment
      this.dialog.set_primary_action(__('Submit'), () => {
        const {
          outstanding_amount = 0,
          write_off_amount = 0,
          change_amount = 0,
        } = this.frm.doc;
        if (outstanding_amount > 0 || write_off_amount > 0 || change_amount > 0) {
          return frappe.throw(
            __('<strong>Paid Amount</strong> must be exactly equal to the amount due')
          );
        } else {
          this.dialog.hide();
          this.events.submit_form();
        }
      });
    }
  };
}
