import { print_doc } from '../frappe-components/InvoiceDialog';

function show_print_buttons(frm) {
  const waitForButtons = setInterval(() => {
    if (frm.custom_buttons['Make Bank Entry']) {
      frm.add_custom_button('Print Salary Slips', async function() {
        if (!frappe.model.can_print(frm.doc.doctype, frm)) {
          frappe.msgprint(__('You are not allowed to print this document'));
          return;
        }
        const { name: payroll_entry } = frm.doc;
        const { message: salary_slips = [] } = await frappe.call({
          method: 'optic_store.api.salary_slip.get_salary_slips_from_payroll_entry',
          args: { payroll_entry },
          freeze: true,
        });
        salary_slips.forEach(salary_slip => {
          ['Payslip Type 1', 'Payslip Type 2'].forEach(print_format => {
            print_doc('Salary Slip', salary_slip, print_format, 0);
          });
        });
      });
      clearInterval(waitForButtons);
    }
  }, 300);
}

export default {
  refresh: function(frm) {
    if (frm.doc.docstatus === 1) {
      show_print_buttons(frm);
    }
  },
};
