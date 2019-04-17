import InvoiceDialog, { print_invoice } from './InvoiceDialog';

export default class DeliverDialog {
  constructor(print_formats = []) {
    this.print_formats = print_formats;
    this.dialog = new frappe.ui.Dialog({
      title: 'Deliver & Print',
      fields: [
        {
          fieldname: 'print_sec',
          fieldtype: 'Section Break',
          label: __('Print Formats'),
        },
        ...this.print_formats.map(pf => ({
          fieldtype: 'Check',
          fieldname: pf,
          label: __(pf),
        })),
      ],
    });
  }
  create_and_print(frm) {
    const print_formats = this.print_formats;
    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action('OK', async function() {
      const { name } = frm.doc;
      const values = this.get_values();
      const enabled_print_formats = print_formats.filter(pf => values[pf]);
      this.hide();
      const { message: delivery_note_name } = await frappe.call({
        method: 'optic_store.api.sales_invoice.deliver_qol',
        freeze: true,
        freeze_message: __('Creating Delivery Note'),
        args: { name },
      });
      frm.reload_doc();
      enabled_print_formats.forEach(pf => {
        print_invoice(name, pf, 0);
      });
    });

    this.dialog.show();
  }
  async print_invoice(frm) {
    const print_formats = this.print_formats;
    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action('OK', function() {
      const { name } = frm.doc;
      const values = this.get_values();
      const enabled_print_formats = print_formats.filter(pf => values[pf]);
      this.hide();
      enabled_print_formats.forEach(pf => {
        print_invoice(name, pf, 0);
      });
    });
    this.dialog.show();
  }
}
