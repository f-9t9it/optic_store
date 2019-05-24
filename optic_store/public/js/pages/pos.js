import pick from 'lodash/pick';
import keyBy from 'lodash/keyBy';
import mapValues from 'lodash/mapValues';
import JsBarcode from 'jsbarcode';

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

function add_search_params_to_customer_mapper(customers_details = {}) {
  const search_fields = ['os_cpr_no', 'os_mobile_number', 'old_customer_id'];
  return function(item) {
    const { value, searchtext: searchtext_ori = '' } = item;
    const customer = customers_details[value];
    if (customer) {
      const searchtext = search_fields.reduce((a, param) => {
        const x = customer[param] && customer[param].toLowerCase();
        return x && !a.includes(x) ? `${a} ${x}` : a;
      }, searchtext_ori);
      return Object.assign(item, { searchtext });
    }
    return item;
  };
}

function make_customer_search_subtitle(customers_details = {}) {
  const search_fields = [
    'customer_name',
    'os_cpr_no',
    'os_mobile_number',
    'old_customer_id',
  ];
  return function({ value }) {
    const customer = customers_details[value];
    if (customer) {
      return search_fields
        .map(param => customer[param])
        .filter(value => value)
        .join(' | ');
    }
    return '';
  };
}

function get_barcode_uri(text) {
  return JsBarcode(document.createElement('canvas'), text, {
    height: 40,
    displayValue: false,
  })._renderProperties.element.toDataURL();
}

function get_offline_customer(customer) {
  const docjson = (JSON.parse(localStorage.getItem('customer_details')) || {})[
    customer
  ];
  return docjson ? JSON.parse(docjson) : null;
}

export default function extend_pos(PosClass) {
  class PosClassExtended extends PosClass {
    onload() {
      super.onload();
      this.batch_dialog = new frappe.ui.Dialog({
        title: __('Select Batch No'),
        fields: [
          {
            fieldname: 'batch',
            fieldtype: 'Select',
            label: __('Batch No'),
            reqd: 1,
          },
        ],
      });
    }
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
            territories = [],
            customer_groups = [],
            batch_details = [],
            branch_details = {},
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
        this.customers_master_data = { territories, customer_groups };
        this.loyalty_programs_data = list2dict('name', loyalty_programs);
        this.gift_cards_data = list2dict('name', gift_cards);
        this.batch_details = batch_details;
        this.batch_no_data = mapValues(batch_details, x => x.map(({ name }) => name));
        this.branch_details = branch_details;
        this.make_sales_person_field();
        this.make_group_discount_field();
        this.set_opening_entry();
      } catch (e) {
        console.warn(e);
        frappe.msgprint({
          indicator: 'orange',
          title: __('Warning'),
          message: __('Unable to load extended details. Usage will be restricted.'),
        });
      }
    }
    create_new() {
      super.create_new();
      if (this.sales_person_field) {
        this.sales_person_field.set_value('');
      }
    }
    make_control() {
      super.make_control();
      this.make_sales_person_field();
      this.make_group_discount_field();
      this.bind_keyboard_shortcuts();
    }
    toggle_totals_area(show) {
      super.toggle_totals_area(show);
      this.wrapper
        .find('.totals-area')
        .find('.group_discount-area')
        .toggle(!this.is_totals_area_collapsed);
      this.pos_bill.find('.discount-amount-area').hide();
    }
    make_customer() {
      super.make_customer();
      this.party_field.awesomeplete.item = ({ label, value }, input) => {
        const get_subtitle = make_customer_search_subtitle(this.customers_details_data);
        const html = `
          <a>
            <p>${__(label || value)}</p>
            <p class="text-muted ellipsis">${get_subtitle({ value })}</p>
          </a>
        `;

        return $('<li />')
          .data('item.autocomplete', { value })
          .html(html)
          .get(0);
      };
    }
    prepare_customer_mapper(key) {
      const super_fn = super.prepare_customer_mapper;

      function extended_fn(key) {
        let startsuper = Date.now();
        super_fn.bind(this)(key);
        let startext = Date.now();
        const search = (key || '').toLowerCase().trim();
        const reg = new RegExp(
          search.replace(new RegExp('%', 'g'), '\\w*\\s*[a-zA-Z0-9]*')
        );
        let count = 0;
        const customers_mapper_ext = key
          ? this.customers
              .filter(({ name }) => {
                if (count >= 30) {
                  return false;
                }
                const detail =
                  this.customers_details_data && this.customers_details_data[name];
                if (detail) {
                  const will_add =
                    !this.customers_mapper.map(({ value }) => value).includes(name) &&
                    (reg.test(detail['old_customer_id']) ||
                      reg.test(detail['os_cpr_no']) ||
                      reg.test(detail['os_mobile_number']));
                  if (will_add) {
                    count++;
                  }
                  return will_add;
                }
                return false;
              })
              .map(({ name, customer_name, customer_group, territory }) => ({
                label: name,
                value: name,
                customer_name,
                customer_group,
                territory,
                searchtext: [name, customer_name, customer_group, territory]
                  .join(' ')
                  .toLowerCase(),
              }))
          : [];
        this.customers_mapper = [...customers_mapper_ext, ...this.customers_mapper].map(
          add_search_params_to_customer_mapper(this.customers_details_data)
        );
        this.party_field.awesomeplete.list = this.customers_mapper;
        if (window.OS_DEBUG) {
          console.log(
            `[ ${String(key).padEnd(12)} ] : ${(Date.now() - startsuper) /
              1000}s / ${(Date.now() - startext) / 1000}s`
          );
        }
      }

      // required because this.party_field.$input event references this and
      // might run before super_fn executes and sets this.customers_mapper
      if (!this.customers_mapper) {
        this.customers_mapper = [];
      }

      if (this.os_timer_pcm) {
        window.cancelAnimationFrame(this.os_timer_pcm);
      }
      this.os_timer_pcm = window.requestAnimationFrame(extended_fn.bind(this, key));
    }
    update_customer(new_customer) {
      super.update_customer(new_customer);
      this.customer_doc.sections.forEach((section, i) => {
        if (i > 0) {
          section.wrapper.hide();
        }
      });
      this.customer_doc.add_fields([
        {
          fieldtype: 'Select',
          fieldname: 'territory',
          label: __('Territory'),
          default: this.pos_profile_data.territory,
          options: this.customers_master_data.territories,
        },
        { fieldtype: 'Column Break' },
        {
          fieldtype: 'Select',
          fieldname: 'customer_group',
          label: __('Customer Group'),
          default: this.pos_profile_data.customer_group,
          options: this.customers_master_data.customer_groups,
        },
      ]);
      this.customer_doc.add_fields(customer_qe_fields);
      this.customer_doc.set_values(
        pick(this.customers_details_data[this.frm.doc.customer] || {}, [
          ...CUSTOMER_DETAILS_FIELDS,
          'territory',
          'customer_group',
        ])
      );
    }
    get_prompt_details() {
      super.get_prompt_details();
      const { territory, customer_group } = this.customer_doc.get_values();
      this.prompt_details.territory = territory;
      this.prompt_details.customer_group = customer_group;
      return JSON.stringify(this.prompt_details);
    }
    set_item_details(item_code, field, value, remove_zero_qty_items) {
      super.set_item_details(item_code, field, value, remove_zero_qty_items);
      if (field === 'rate') {
        const item = this.frm.doc.items.find(({ item_code: x }) => x === item_code);
        if (item) {
          const { rate, price_list_rate } = item;
          item.discount_percentage = flt(
            (1 - flt(rate) / flt(price_list_rate)) * 100.0,
            precision('discount_percentage')
          );
          this.update_paid_amount_status(false);
        }
      }
    }
    make_item_list(customer) {
      super.make_item_list(customer);
      const items = keyBy(this.item_data, 'name');
      this.wrapper
        .find('.item-list')
        .find('.image-view-body')
        .children('a')
        .each((i, a) => {
          const { itemCode: item_code } = $(a).data();
          const {
            os_minimum_selling_rate: ms1 = 0,
            os_minimum_selling_2_rate: ms2 = 0,
          } = items[item_code] || {};
          if (ms1 || ms2) {
            $(
              `<span>
                <div>MS1: ${format_currency(ms1, this.frm.doc.currency)}</div>
                <div>MS2: ${format_currency(ms2, this.frm.doc.currency)}</div>
              </span>`
            )
              .css({
                position: 'absolute',
                left: '0',
                top: '0',
                padding: '5px 9px',
                'background-color': 'rgba(141, 153, 166, 0.6)',
                color: '#fff',
                'border-radius': '3px',
                'font-size': '0.75em',
              })
              .appendTo($(a).find('.image-field'));
          }
        });
    }
    validate() {
      if (!this.frm.doc.os_sales_person) {
        frappe.throw(__('Sales Person is mandatory'));
      } else if (
        !this.sales_persons_data
          .map(({ value }) => value)
          .includes(this.frm.doc.os_sales_person)
      ) {
        frappe.throw(__(`Sales Person: ${this.frm.doc.os_sales_person} is not valid`));
      }
      super.validate();
    }
    mandatory_batch_no() {
      const { has_batch_no, item_code } = this.items[0];
      this.batch_dialog.get_field('batch').$input.empty();
      this.batch_dialog.get_primary_btn().off('click');
      this.batch_dialog.get_close_btn().off('click');
      if (has_batch_no && !this.item_batch_no[item_code]) {
        (this.batch_details[item_code] || []).forEach(({ name, expiry_date, qty }) => {
          this.batch_dialog
            .get_field('batch')
            .$input.append(
              $('<option />', { value: name }).text(
                `${name} | ${
                  expiry_date ? frappe.datetime.str_to_user(expiry_date) : '--'
                } | ${qty}`
              )
            );
        });
        this.batch_dialog.get_field('batch').set_input();
        this.batch_dialog.set_primary_action(__('Submit'), () => {
          const batch_no = this.batch_dialog.get_value('batch');
          const item = this.frm.doc.items.find(item => item.item_code === item_code);
          if (item) {
            item.batch_no = batch_no;
          }
          this.item_batch_no[item_code] = batch_no;
          this.batch_dialog.hide();
          this.set_focus();
        });
        this.batch_dialog.get_close_btn().on('click', () => {
          this.item_code = item_code;
          this.render_selected_item();
          this.remove_selected_item();
          this.wrapper.find('.selected-item').empty();
          this.item_code = null;
          this.set_focus();
        });
        this.batch_dialog.show();
        this.batch_dialog.$wrapper.find('.modal-backdrop').off('click');
      }
    }
    make_offline_customer(new_customer) {
      super.make_offline_customer(new_customer);
      const values = this.customer_doc.get_values();
      const is_new = !this.customers_details_data[this.frm.doc.customer];
      const current = this.customers_details_data[this.frm.doc.customer] || {};
      this.customers_details_data[this.frm.doc.customer] = Object.assign(
        {
          customer_pos_id: values.customer_pos_id,
          full_name: values.full_name,
        },
        current,
        pick(values, CUSTOMER_DETAILS_FIELDS),
        {
          customer_name:
            values.full_name !== current.customer_name
              ? values.full_name
              : current.customer_name,
          is_new,
        }
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
    refresh() {
      super.refresh();
      if (!this.xreport) {
        this.set_opening_entry();
      }
    }
    make_menu_list() {
      super.make_menu_list();
      this.page.menu
        .find('a.grey-link:contains("Cashier Closing")')
        .parent()
        .hide();
      this.page.add_menu_item(
        'XZ Report',
        async function() {
          if (this.connection_status) {
            if (!this.xreport) {
              await this.set_opening_entry();
            }
            frappe.dom.freeze('Syncing');
            this.sync_sales_invoice();
            await frappe.after_server_call();
            frappe.set_route('Form', 'XZ Report', this.xreport, {
              end_time: frappe.datetime.now_datetime(),
            });
            frappe.dom.unfreeze();
            this.xreport = null;
          } else {
            frappe.msgprint({
              message: __('Please perform this when online.'),
            });
          }
        }.bind(this)
      );
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
    create_invoice() {
      const get_customer_doc = customer => {
        const doc = this.customers_details_data[customer];
        const offline_doc = get_offline_customer(customer);
        return Object.assign({}, doc, offline_doc, {
          is_new: doc ? doc.hasOwnProperty('is_new') && doc.is_new : true,
          customer_id: doc ? doc.name : null,
          customer_name:
            (doc && doc.customer_name) || (offline_doc && offline_doc.full_name),
        });
      };
      const invoice_data = super.create_invoice();
      // this is possible because invoice_data already references this.frm.doc
      // this will be used by the print format to render barcodes
      this.frm.doc.pos_name_barcode_uri = get_barcode_uri(
        this.frm.doc.offline_pos_name
      );
      this.frm.doc.branch_doc = this.branch_details || {};
      this.frm.doc.customer_doc = get_customer_doc(this.frm.doc.customer);
      const sales_person =
        this.sales_persons_data.find(
          ({ value }) => value === this.frm.doc.os_sales_person
        ) || {};
      this.frm.doc.sales_person_name = sales_person.label;
      this.update_invoice();
      return invoice_data;
    }
    set_interval_for_si_sync() {
      setInterval(() => {
        this.freeze_screen = false;
        this.sync_sales_invoice();
      }, 3600000);
    }
    show_amounts() {
      super.show_amounts();
      this.dialog
        .get_primary_btn()
        .toggleClass('disabled', this.frm.doc.grand_total !== this.frm.doc.paid_amount);
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
      }
      this.sales_person_field.set_data(this.sales_persons_data);
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
    bind_keyboard_shortcuts() {
      $(document).on('keydown', e => {
        if (frappe.get_route_str() === 'pos') {
          if (this.numeric_keypad && e.keyCode === 120) {
            e.preventDefault();
            e.stopPropagation();
            if (this.dialog && this.dialog.is_visible) {
              this.dialog.hide();
            } else {
              $(this.numeric_keypad)
                .find('.pos-pay')
                .trigger('click');
            }
          } else if (this.frm.doc.docstatus == 1 && e.ctrlKey && e.keyCode === 80) {
            e.preventDefault();
            e.stopPropagation();
            if (this.msgprint) {
              this.msgprint.msg_area.find('.print_doc').click();
            } else {
              this.page.btn_secondary.trigger('click');
            }
          } else if (e.ctrlKey && e.keyCode === 66) {
            e.preventDefault();
            e.stopPropagation();
            if (this.msgprint) {
              this.msgprint.msg_area.find('.new_doc').click();
            } else {
              this.page.btn_primary.trigger('click');
            }
          }
        }
      });
    }
    async set_opening_entry() {
      const { company, os_branch: branch } = this.doc;
      const { name: pos_profile } = this.pos_profile_data;
      const { message: xreport } = await frappe.call({
        method: 'optic_store.api.xz_report.get_unclosed',
        args: { user: frappe.session.user, pos_profile, company, branch },
      });
      if (xreport) {
        this.xreport = xreport;
      } else {
        const dialog = new frappe.ui.Dialog({
          title: __('Enter Opening Cash'),
          fields: [
            {
              fieldtype: 'Datetime',
              fieldname: 'start_time',
              label: __('Start Datetime'),
              default: frappe.datetime.now_datetime(),
            },
            { fieldtype: 'Column Break' },
            {
              fieldtype: 'Currency',
              fieldname: 'opening_cash',
              label: __('Amount'),
            },
          ],
        });
        dialog.show();
        dialog.get_close_btn().hide();
        dialog.set_primary_action(
          'Enter',
          async function() {
            try {
              const { start_time, opening_cash } = dialog.get_values();
              const { message: xreport } = await frappe.call({
                method: 'optic_store.api.xz_report.create_opening',
                args: { start_time, opening_cash, company, pos_profile },
              });
              if (!xreport) {
                throw new Error();
              }
              this.xreport = xreport;
            } catch (e) {
              frappe.msgprint({
                message: __('Unable to create XZ Report opening entry.'),
                title: __('Warning'),
                indicator: 'orange',
              });
            } finally {
              dialog.hide();
              dialog.$wrapper.remove();
            }
          }.bind(this)
        );
      }
    }

    make_payment() {
      if (this.dialog) {
        this.dialog.$wrapper.remove();
      }
      super.make_payment();
      ['.change_amount', '.write_off_amount'].forEach(q => {
        this.dialog.$body
          .find(q)
          .parent()
          .addClass('hidden');
      });
    }
    show_payment_details() {
      const multimode_payments = $(this.$body).find('.multimode-payments').html(`
        <ul class="nav nav-tabs" role="tablist">
          <li role="presentation" class="active">
            <a role="tab" data-toggle="tab" data-target="#multimode_loc">${__(
              'Base'
            )}</a>
          </li>
          <li role="presentation">
            <a role="tab" data-toggle="tab" data-target="#multimode_alt">${__(
              'Alternate'
            )}</a>
          </li>
        </ul>
        <div class="tab-content">
          <div role="tabpanel" class="tab-pane active" id="multimode_loc" />
          <div role="tabpanel" class="tab-pane" id="multimode_alt" />
        </div>
      `);
      const multimode_loc = multimode_payments.find('#multimode_loc');
      const multimode_alt = multimode_payments.find('#multimode_alt');
      const is_alt_currency = mop =>
        (
          this.doc.payments.find(({ mode_of_payment }) => mode_of_payment === mop) || {
            os_in_alt_tab: 0,
          }
        ).os_in_alt_tab;
      const { currency } = this.frm.doc;
      if (this.frm.doc.payments.length) {
        this.frm.doc.payments.forEach(
          ({ mode_of_payment, amount, idx, type, os_in_alt_tab }) => {
            $(
              frappe.render_template('payment_details', {
                mode_of_payment,
                amount,
                idx,
                currency,
                type,
              })
            ).appendTo(
              is_alt_currency(mode_of_payment) ? multimode_alt : multimode_loc
            );
            if (type === 'Cash' && amount === this.frm.doc.paid_amount) {
              this.idx = idx;
              this.selected_mode = $(this.$body).find(`input[idx='${this.idx}']`);
              this.highlight_selected_row();
              this.bind_amount_change_event();
            }
          }
        );
      } else {
        $('<p>No payment mode selected in pos profile</p>').appendTo(
          multimode_payments
        );
      }
    }
    set_payment_primary_action() {
      // totally override validation to check for zero amount to enable payment thru
      // loyalty program
      this.dialog.set_primary_action(__('Submit'), () => {
        if (this.frm.doc.change_amount !== 0) {
          return frappe.throw(
            __(
              '<strong>Change Amount</strong> must be zero. Please verify that ' +
                '<strong>Paid Amount</strong> does not exceed billed amount'
            )
          );
        }
        if (this.frm.doc.grand_total !== this.frm.doc.paid_amount) {
          return frappe.throw(
            __(
              '<strong>Paid Amount</strong> must be equal to <strong>Total Amount</strong>'
            )
          );
        }
        this.dialog.hide();
        this.submit_invoice();
      });
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
