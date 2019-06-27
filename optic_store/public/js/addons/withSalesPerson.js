export default function withSalesPerson(Cart) {
  const isClass = Cart instanceof Function || Cart instanceof Class;
  if (!isClass) {
    return Cart;
  }
  return class CartWithSalesPerson extends Cart {
    make() {
      super.make();
      this.make_sale_sperson_field();
    }
    make_dom() {
      super.make_dom();
      this.wrapper.find('.cart-wrapper').after('<div class="sales_person-field" />');
    }
    reset() {
      super.reset();
      this.sales_person_field.set_value(this.frm.doc.os_sales_person);
    }
    async make_sale_sperson_field() {
      const sales_person_department = await frappe.db.get_single_value(
        'Optical Store Settings',
        'sales_person_department'
      );
      this.sales_person_field = frappe.ui.form.make_control({
        df: {
          fieldtype: 'Link',
          label: 'Sales Person',
          fieldname: 'sales_person',
          options: 'Employee',
          reqd: 1,
          get_query: function() {
            return { filters: [['department', '=', sales_person_department]] };
          },
          onchange: () => {
            this.frm.set_value('os_sales_person', this.sales_person_field.get_value());
          },
        },
        parent: this.wrapper.find('.sales_person-field'),
        render_input: true,
      });
      this.sales_person_field.set_value(this.frm.doc.os_sales_person);
    }
  };
}
