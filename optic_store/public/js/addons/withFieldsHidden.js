import sumBy from 'lodash/sumBy';

export default function withFieldsHidden(Payment) {
  const isClass = Payment instanceof Function || Payment instanceof Class;
  if (!isClass) {
    return Payment;
  }
  return class PaymentWithFieldsHidden extends Payment {
    get_fields() {
      const fields = super.get_fields();
      const section_idx =
        fields.findIndex(({ fieldname }) => fieldname === 'write_off_amount') - 1;
      return fields.map((x, i) =>
        i === section_idx ? Object.assign(x, { hidden: 1 }) : x
      );
    }
  };
}
