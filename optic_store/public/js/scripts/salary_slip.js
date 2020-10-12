import { print_doc } from '../frappe-components/InvoiceDialog';

function show_print_buttons(frm) {
  frm.add_custom_button('Print Salary Slips', () => {
    if (!frappe.model.can_print(frm.doc.doctype, frm)) {
      frappe.msgprint(__('You are not allowed to print this document'));
      return;
    }
    const { name } = frm.doc;
    ['Payslip Type 1', 'Payslip Type 2'].forEach(print_format => {
      print_doc('Salary Slip', name, print_format, 0);
    });
  });
}

export default {
  refresh: function(frm) {
    if (!frm.doc.__islocal) {
      show_print_buttons(frm);
    }
  },
};
