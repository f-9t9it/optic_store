export default function withSalesPerson(Cart) {
  const isClass = Cart instanceof Function || Cart instanceof Class;
  if (!isClass) {
    return Cart;
  }
  return class CartWithSalesPerson extends Cart {
    make() {
      super.make();
      this._make_sale_sperson_fields();
    }
    make_dom() {
      super.make_dom();
      this.wrapper.find('.cart-wrapper').after(`
        <div class="sales_person-area">
          <div class="sales_person-field" />
          <div class="sales_person_name-field" />
        </div>
      `);
    }
    reset() {
      super.reset();
      this.sales_person_field.set_value(this.frm.doc.os_sales_person);
    }
    async _make_sale_sperson_fields() {
      const sales_person_department = await frappe.db.get_single_value(
        'Optical Store Settings',
        'sales_person_department'
      );
      async function get_employee_name(employee) {
        if (!employee) {
          return null;
        }
        const {
          message: { employee_name },
        } = await frappe.db.get_value('Employee', employee, 'employee_name');
        return employee_name;
      }

      this.wrapper.find('.sales_person-area').css({ 'margin-bottom': '10px' });
      const sales_person_field = this.wrapper.find(
        '.sales_person-area > .sales_person-field'
      );
      const sales_person_name_field = this.wrapper
        .find('.sales_person-area > .sales_person_name-field')
        .css({ padding: '4px', 'font-style': 'italic' });
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
          onchange: async function() {
            const sales_person = this.sales_person_field.get_value();
            const sales_person_name = await get_employee_name(sales_person);
            this.frm.set_value({
              os_sales_person: sales_person,
              os_sales_person_name: sales_person_name,
            });
            sales_person_name_field.empty().text(sales_person_name || '');
          }.bind(this),
        },
        parent: sales_person_field,
        render_input: true,
      });
      this.sales_person_field.set_value(this.frm.doc.os_sales_person);

      sales_person_field.find('.frappe-control').css({ 'margin-bottom': 0 });
      sales_person_field.find('.form-group').css({ 'margin-bottom': 0 });
      sales_person_field.find('.help-box').css({ display: 'none' });
    }
  };
}

export function paymentWithSalesPerson(Payment) {
  const isClass = Payment instanceof Function || Payment instanceof Class;
  if (!isClass) {
    return Payment;
  }
  return class PaymentWithSalesPerson extends Payment {
    open_modal() {
      if (!this.frm.doc.os_sales_person) {
        frappe.throw(__('Sales Person is mandatory'));
      }
      super.open_modal();
    }
  };
}
