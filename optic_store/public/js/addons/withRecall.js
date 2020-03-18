export default function withRecall(Cart) {
  const isClass = Cart instanceof Function || Cart instanceof Class;
  if (!isClass) {
    return Cart;
  }
  return class CartWithRecall extends Cart {
    make() {
      super.make();
      this._make_recall_fields();
    }
    make_dom() {
      super.make_dom();
      this.wrapper.find('.loyalty-program-field').before(`
        <div class="recall-area">
          <div class="recall-field"></div>
          <div class="recall_months-field"></div>
          <div class="recall_reason-field"></div>
        </div>
      `);
    }
    reset() {
      super.reset();
      ['os_recall', 'os_recall_months', 'os_recall_reason'].forEach(fieldname => {
        this.recall_fields[fieldname].set_value(this.frm.doc[fieldname]);
      });
    }
    _make_recall_fields() {
      this.recall_fields = {
        os_recall: frappe.ui.form.make_control({
          df: {
            label: 'Recall',
            fieldtype: 'Check',
            fieldname: 'os_recall',
            onchange: () => {
              const os_recall = this.recall_fields.os_recall.get_value();
              ['os_recall_months', 'os_recall_reason'].forEach(fieldname => {
                this.recall_fields[fieldname].df.hidden = os_recall ? 0 : 1;
                this.recall_fields[fieldname].refresh();
              });
              this.frm.set_value({ os_recall });
            },
          },
          parent: this.wrapper.find('.recall-area > .recall-field'),
          render_input: true,
        }),
        os_recall_months: frappe.ui.form.make_control({
          df: {
            fieldname: 'os_recall_months',
            fieldtype: 'Int',
            label: 'Recall Months',
            hidden: 1,
            onchange: () => {
              const os_recall_months = this.recall_fields.os_recall_months.get_value();
              this.frm.set_value({ os_recall_months });
            },
          },
          parent: this.wrapper.find('.recall-area > .recall_months-field'),
          render_input: true,
        }),
        os_recall_reason: frappe.ui.form.make_control({
          df: {
            fieldname: 'os_recall_reason',
            fieldtype: 'Data',
            label: 'Recall Reason',
            hidden: 1,
            onchange: () => {
              const os_recall_reason = this.recall_fields.os_recall_reason.get_value();
              this.frm.set_value({ os_recall_reason });
            },
          },
          parent: this.wrapper.find('.recall-area > .recall_reason-field'),
          render_input: true,
        }),
      };
    }
  };
}
