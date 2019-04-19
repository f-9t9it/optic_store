import pick from 'lodash/pick';

import { customer_qe_fields } from '../scripts/customer_qe';

const CUSTOMER_DETAILS_FIELDS = customer_qe_fields
  .filter(({ fieldtype }) => ['Data', 'Date', 'Small Text'].includes(fieldtype))
  .map(({ fieldname }) => fieldname);

export default function extend_pos(PosClass) {
  class PosClassExtended extends PosClass {
    async init_master_data(r) {
      super.init_master_data(r);
      try {
        const {
          message: {
            sales_persons = [],
            group_discounts = {},
            customers_details = [],
          } = {},
        } = await frappe.call({
          method: 'optic_store.api.pos.get_extended_pos_data',
          args: { company: this.pos_profile_data.company },
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
        this.customers_details_data = customers_details.reduce(
          (a, x) => Object.assign(a, { [x.name]: x }),
          {}
        );
        this.make_sales_person_field();
        this.make_group_discount_field();
      } catch (e) {
        console.warn(e);
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
    update_customer(new_customer) {
      super.update_customer(new_customer);
      this.customer_doc.sections.forEach((section, i) => {
        if (i > 0) {
          section.wrapper.hide();
        }
      });
      this.customer_doc.add_fields(customer_qe_fields);
      this.customer_doc.set_values(
        pick(
          this.customers_details_data[this.frm.doc.customer] || {},
          CUSTOMER_DETAILS_FIELDS
        )
      );
    }
    make_offline_customer(new_customer) {
      super.make_offline_customer(new_customer);
      const values = this.customer_doc.get_values();
      this.customers_details_data[this.frm.doc.customer] = Object.assign(
        {},
        this.customers_details_data[this.frm.doc.customer],
        pick(values, CUSTOMER_DETAILS_FIELDS)
      );
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
