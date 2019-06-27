function seg_mops(payments, alt_tab_val) {
  return payments
    .filter(({ os_in_alt_tab }) => os_in_alt_tab === alt_tab_val)
    .map(({ mode_of_payment }) => mode_of_payment);
}

export default function withTabbedMops(Payment) {
  const isClass = Payment instanceof Function || Payment instanceof Class;
  if (!isClass) {
    return Payment;
  }
  return class PaymentWithTabbedMops extends Payment {
    make() {
      this.tabs = {
        base: seg_mops(this.frm.doc.payments, 0),
        alt: seg_mops(this.frm.doc.payments, 1),
      };
      super.make();
      const $toggle_mops = $(`
        <ul class="nav nav-tabs" role="tablist">
          <li role="presentation" class="active">
            <a class="toggle-base" role="tab" data-toggle="tab">${__('Base')}</a>
          </li>
          <li role="presentation">
            <a class="toggle-alt" role="tab" data-toggle="tab">${__('Alternate')}</a>
          </li>
        </ul>
      `).appendTo(this.dialog.get_field('toggle_mops').$wrapper);
      $toggle_mops.click('on', e => {
        Object.keys(this.tabs).forEach(tab => {
          this.tabs[tab].forEach(mop => {
            this.dialog.set_df_property(
              mop,
              'hidden',
              !$(e.target).hasClass(`toggle-${tab}`)
            );
          });
        });
      });
    }
    get_fields() {
      const fields = super.get_fields();
      return [
        { fieldtype: 'HTML', fieldname: 'toggle_mops' },
        ...fields.map(x =>
          this.tabs.alt.includes(x.fieldname) ? Object.assign(x, { hidden: 1 }) : x
        ),
      ];
    }
  };
}
