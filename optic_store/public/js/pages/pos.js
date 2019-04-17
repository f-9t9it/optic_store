export default function extend_pos(PosClass) {
  class PosClassExtended extends PosClass {
    async init_master_data(r) {
      super.init_master_data(r);
      try {
        const {
          message: { sales_persons = [], group_discounts = {} } = {},
        } = await frappe.call({
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
        this.group_discounts_data = group_discounts;
        this.make_sales_person_field();
        this.make_group_discount_field();
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
      this.make_group_discount_field();
    }
    create_invoice() {
      this.frm.doc.os_sales_person = this.sales_person_field.get_value();
      super.create_invoice();
    }
    toggle_totals_area(show) {
      super.toggle_totals_area(show);
      this.wrapper
        .find('.totals-area')
        .find('.group_discount-area')
        .toggle(!this.is_totals_area_collapsed);
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
    make_group_discount_field() {
      if (this.pos_profile_data.allow_user_to_edit_discount) {
        const group_discounts = Object.keys(this.group_discounts_data || {});
        if (!this.group_discount_field) {
          const $parent = $(`
            <div class="pos-list-row group_discount-area" style="display: none;">
              <div class="cell text-right">${__('Group Discount')}</div>
              <div class="cell price-cell group_discount" style="padding-left: 24px;"/>
            </div>
            `)
            .insertAfter(this.pos_bill.find('.net-total-area'))
            .find('.group_discount');
          this.group_discount_field = new frappe.ui.form.ControlAutocomplete({
            parent: $parent,
            df: { options: group_discounts },
          });
          this.group_discount_field.toggle_label(false);
          this.group_discount_field.refresh();
          this.group_discount_field.$input.on('change', () => {
            const discounts_by_brand =
              this.group_discounts_data[
                this.group_discount_field.get_value()
              ] || {};
            this.frm.doc.items.forEach(({ item_code, brand }) => {
              const discount_rate = discounts_by_brand[brand] || 0;
              this.update_discount(item_code, discount_rate);
            });
          });
        } else {
          this.group_discount_field.set_data(group_discounts);
        }
      }
    }
  }
  return PosClassExtended;
}
