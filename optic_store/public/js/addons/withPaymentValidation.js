import sumBy from 'lodash/sumBy';

export default function withPaymentValidation(Payment) {
  const isClass = Payment instanceof Function || Payment instanceof Class;
  if (!isClass) {
    return Payment;
  }
  return class PaymentWithPaymentValidation extends Payment {
    set_primary_action() {
      // complete override to validate exact payment
      this.dialog.set_primary_action(
        __('Submit'),
        async function() {
          try {
            await this.validate();
            this.dialog.hide();
            this.events.submit_form();
          } catch (e) {
            frappe.throw(e);
          }
        }.bind(this)
      );
    }
    validate() {}
  };
}
