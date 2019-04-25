import pick from 'lodash/pick';

import { customer_qe_fields } from '../scripts/customer_qe';

const CUSTOMER_DETAILS_FIELDS = customer_qe_fields
  .filter(({ fieldtype }) => ['Data', 'Date', 'Small Text'].includes(fieldtype))
  .map(({ fieldname }) => fieldname);

function list2dict(key, list) {
  return Object.assign({}, ...list.map(item => ({ [item[key]]: item })));
}

function set_description(field) {
  return function(description) {
    field.set_new_description(description);
  };
}

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
            loyalty_programs = [],
            gift_cards = [],
          } = {},
        } = await frappe.call({
          method: 'optic_store.api.pos.get_extended_pos_data',
          args: { company: this.pos_profile_data.company },
          freeze: true,
          freeze_message: __('Syncing extended details'),
        });
        this.sales_persons_data = sales_persons.map(({ name, employee_name }) => ({
          label: employee_name,
          value: name,
        }));
        this.group_discounts_data = group_discounts;
        this.customers_details_data = list2dict('name', customers_details);
        this.loyalty_programs_data = list2dict('name', loyalty_programs);
        this.gift_cards_data = list2dict('name', gift_cards);
        this.make_sales_person_field();
        this.make_group_discount_field();
      } catch (e) {
        console.warn(e);
        frappe.msgprint({
          indicator: 'orange',
          title: __('Warning'),
          message: __('Unable to load extended details. Usage will be restricted.'),
        });
      }
    }
    make_control() {
      super.make_control();
      this.make_sales_person_field();
      this.make_group_discount_field();
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
    validate() {
      if (!this.frm.doc.os_sales_person) {
        frappe.throw(__('Sales Person is mandatory'));
      }
      super.validate();
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
    make_keyboard() {
      super.make_keyboard();
      this.add_more_payment_options();
    }
    update_payment_amount() {
      const { idx: gift_card_idx } =
        this.frm.doc.payments.find(
          ({ mode_of_payment }) => mode_of_payment === 'Gift Card'
        ) || {};
      if (cint(gift_card_idx) === cint(this.idx)) {
        if (this.payment_val > flt(this.os_payment_fg.get_value('gift_card_balance'))) {
          this.selected_mode.val(0);
          return frappe.throw(
            __('Payment with Gift Card cannot exceed available balance')
          );
        }
      }
      super.update_payment_amount();
    }
    submit_invoice() {
      const gift_card_no = this.os_payment_fg.get_value('gift_card_no');
      const { amount } = this.frm.doc.payments.find(
        ({ mode_of_payment }) => mode_of_payment === 'Gift Card'
      ) || { amount: 0 };
      const gift_card = this.gift_cards_data[gift_card_no];
      if (gift_card) {
        this.gift_cards_data[gift_card_no] = Object.assign(gift_card, {
          balance: flt(gift_card.balance) - amount,
        });
      }
      super.submit_invoice();
    }

    make_sales_person_field() {
      if (!this.sales_person_field) {
        this.sales_person_field = new frappe.ui.form.ControlAutocomplete({
          parent: $('<div style="margin-top: 10px;" />').insertAfter(
            this.pos_bill.find('.totals-area')
          ),
          df: { options: this.sales_persons_data, label: __('Sales Person'), bold: 1 },
        });
        this.sales_person_field.refresh();
        this.sales_person_field.$input.on('change', () => {
          this.frm.doc.os_sales_person = this.sales_person_field.get_value();
        });
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
              this.group_discounts_data[this.group_discount_field.get_value()] || {};
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
    add_more_payment_options() {
      this.os_payment_fg = new frappe.ui.FieldGroup({
        parent: $('<div style="margin: 0 15px;" />').insertAfter(
          $(this.$body).find('.pos_payment .amount-row')
        ),
        fields: [
          {
            fieldtype: 'Section Break',
            label: __('Other Payments'),
            collapsible: 1,
          },
          {
            fieldtype: 'Column Break',
            label: __('Gift Card'),
          },
          {
            fieldname: 'gift_card_no',
            fieldtype: 'Data',
            label: __('Enter Gift Card No'),
          },
          {
            fieldname: 'gift_card_balance',
            fieldtype: 'Currency',
            label: __('Gift Card Balance'),
            read_only: 1,
            depends_on: 'gift_card_no',
          },
          {
            fieldtype: 'Column Break',
            label: __('Loyalty Program'),
          },
          {
            fieldname: 'loyalty_card_no',
            fieldtype: 'Data',
            label: __('Enter Loyalty Card No'),
          },
          {
            fieldname: 'loyalty_points_available',
            fieldtype: 'Int',
            label: __('Available Loyalty Points'),
            read_only: 1,
            depends_on: 'loyalty_card_no',
          },
          {
            fieldname: 'loyalty_points_redeem',
            fieldtype: 'Int',
            label: __('Points to Redeem'),
            depends_on: 'loyalty_card_no',
          },
          {
            fieldname: 'loyalty_amount_redeem',
            fieldtype: 'Currency',
            label: __('Amount to Redeem'),
            read_only: 1,
            depends_on: 'loyalty_card_no',
          },
        ],
      });
      this.os_payment_fg.make();

      const gift_card_field = this.os_payment_fg.get_field('gift_card_no');
      const set_gift_card_desc = set_description(gift_card_field);
      gift_card_field.$input.off('change');
      gift_card_field.$input.on('change', () => {
        const gift_card_no = gift_card_field.get_value();
        const details = this.gift_cards_data[gift_card_no];
        if (!details) {
          set_gift_card_desc(__('Unable to find Gift Card'));
        } else {
          const { name: gift_card, balance } = details;
          if (!balance) {
            set_gift_card_desc(__('Gift Card balance is depleted'));
          } else {
            set_gift_card_desc('');
            this.os_payment_fg.set_value('gift_card_balance', balance);
            this.frm.doc.os_gift_cards = [{ gift_card, balance }];
          }
        }
      });

      const loyalty_card_field = this.os_payment_fg.get_field('loyalty_card_no');
      const set_loyalty_card_desc = set_description(loyalty_card_field);
      loyalty_card_field.$input.off('change');
      loyalty_card_field.$input.on('change', () => {
        const loyalty_card_no = loyalty_card_field.get_value();
        const {
          os_loyalty_card_no: customer_card_no,
          loyalty_program: customer_loyalty_program,
          loyalty_points: customer_loyalty_points,
        } = this.customers_details_data[this.frm.doc.customer] || {};
        const { name: loyalty_program, conversion_rate } =
          this.loyalty_programs_data[customer_loyalty_program] || {};
        if (!loyalty_program) {
          set_loyalty_card_desc(__('Loyalty Program not found'));
        } else if (loyalty_program !== customer_loyalty_program) {
          set_loyalty_card_desc(__('Customer is not under this Loyalty Program'));
        } else if (loyalty_card_no !== customer_card_no) {
          set_loyalty_card_desc(
            __('The Loyalty Card does not belong to this Customer')
          );
        } else {
          set_loyalty_card_desc('');
          this.os_payment_fg.set_value(
            'loyalty_points_available',
            customer_loyalty_points
          );
        }
      });

      const loyalty_points_field = this.os_payment_fg.get_field(
        'loyalty_points_redeem'
      );
      loyalty_points_field.$input.off('change');
      loyalty_points_field.$input.on('change', () => {
        const loyalty_points = loyalty_points_field.get_value();
        const { loyalty_points: customer_loyalty_points = 0, loyalty_program } =
          this.customers_details_data[this.frm.doc.customer] || {};
        const { conversion_factor = 0 } =
          this.loyalty_programs_data[loyalty_program] || {};
        const { grand_total } = this.frm.doc;
        const allowed_amount = Math.min(
          flt(customer_loyalty_points) * conversion_factor,
          grand_total
        );
        const loyalty_amount =
          loyalty_points > allowed_amount ? 0 : flt(loyalty_points) * conversion_factor;
        this.os_payment_fg.set_value('loyalty_amount_redeem', loyalty_amount);
        if (loyalty_points > allowed_amount) {
          loyalty_points_field.$input.val(0);
          return frappe.throw(
            __(
              `Cannot redeem more than ${format_currency(
                allowed_amount,
                this.frm.doc.currency
              )}`
            )
          );
        }
        this.frm.doc = Object.assign(this.frm.doc, {
          redeem_loyalty_points: 1,
          os_loyalty_card_no: this.os_payment_fg.get_value('loyalty_card_no'),
          loyalty_program,
          loyalty_points,
          loyalty_amount,
        });
        this.selected_mode.val(grand_total - loyalty_amount);
        this.update_payment_amount();
      });
    }
  }
  return PosClassExtended;
}
