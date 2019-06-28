import { apply_group_discount } from '../scripts/sales_order';

export default function withGroupDiscount(Cart) {
  const isClass = Cart instanceof Function || Cart instanceof Class;
  if (!isClass) {
    return Cart;
  }
  return class CartWithGroupDiscount extends Cart {
    make() {
      super.make();
      this.make_group_discount_field();
    }
    make_dom() {
      super.make_dom();
      $(`
        <div class="group_discount">
          <div class="list-item">
          <div class="list-item__content list-item__content--flex-2 text-muted">${__(
            'Group Discount'
          )}</div>
          <div class="list-item__content group_discount-field" />
          </div>
        </div>
      `)
        .insertAfter(this.wrapper.find('.cart-wrapper .taxes-and-totals'))
        .hide();
    }
    reset() {
      super.reset();
      this.group_discount_field.set_value(this.frm.doc.orx_group_discount);
    }
    make_group_discount_field() {
      this.group_discount_field = frappe.ui.form.make_control({
        df: {
          fieldtype: 'Link',
          fieldname: 'group_discount',
          only_select: 1,
          options: 'Group Discount',
          onchange: async function(e) {
            await this.frm.set_value(
              'orx_group_discount',
              this.group_discount_field.get_value()
            );
            await apply_group_discount(this.frm);
            this.frm.doc.items.forEach(this.update_item.bind(this));
            this.update_taxes_and_totals();
            this.update_grand_total();
          }.bind(this),
        },
        parent: this.wrapper.find('.group_discount-field'),
        render_input: true,
      });
      this.group_discount_field.$wrapper.css('margin-bottom', '0');
      this.group_discount_field.$wrapper.find('.control-label').hide();
    }
    toggle_taxes_and_totals(flag) {
      super.toggle_taxes_and_totals(flag);
      this.wrapper.find('.group_discount').toggle(this.tax_area_is_shown);
    }
  };
}
