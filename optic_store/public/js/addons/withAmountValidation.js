import sumBy from 'lodash/sumBy';

export default function withAmountValidation(Payment) {
  const isClass = Payment instanceof Function || Payment instanceof Class;
  if (!isClass) {
    return Payment;
  }
  return class PaymentWithAmountValidation extends Payment {
    validate() {
      const {
        outstanding_amount = 0,
        write_off_amount = 0,
        change_amount = 0,
      } = this.frm.doc;
      if (outstanding_amount > 0 || write_off_amount > 0 || change_amount > 0) {
        frappe.throw(
          __('<strong>Paid Amount</strong> must be exactly equal to the amount due')
        );
      }
      return super.validate();
    }
  };
}
