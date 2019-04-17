export default function extend_pos(PosClass) {
  class PosClassExtended extends PosClass {
    async init_master_data(r) {
      super.init_master_data(r);
      try {
        const { message: { sales_persons = [] } = {} } = await frappe.call({
          method: 'optic_store.api.pos.get_extended_pos_data',
          freeze: true,
          freeze_message: __('Syncing extended details'),
        });
        this.sales_persons_data = sales_persons.map(
          ({ name, employee_name }) => ({
            label: employee_name,
            value: name,
          })
        );
        this.make_sales_person_field();
      } catch (e) {
        frappe.msgprint({
          indicator: 'orange',
          title: __('Warning'),
          message: __(
            'Unable to load extended details. Usage will be restricted.'
          ),
        });
      }
    }
    make_control() {
      super.make_control();
      this.make_sales_person_field();
    }
    create_invoice() {
      this.frm.doc.os_sales_person = this.sales_person_field.get_value();
      super.create_invoice();
    }
    make_sales_person_field() {
      if (!this.sales_person_field) {
        this.sales_person_field = new frappe.ui.form.ControlAutocomplete({
          parent: $('<div style="margin-top: 10px;" />').insertAfter(
            this.pos_bill.find('.totals-area')
          ),
          df: { options: this.sales_persons_data, label: __('Sales Person') },
        });
        this.sales_person_field.refresh();
      } else {
        this.sales_person_field.set_data(this.sales_persons_data);
      }
    }
  }
  return PosClassExtended;
}
