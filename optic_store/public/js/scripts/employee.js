import { set_nationality_options } from './customer';

export default {
  onload: set_nationality_options,
  refresh: function(frm) {
    if (
      !['HR Manager', 'Account Manager', 'System Manager'].some(role =>
        frappe.user_roles.includes(role)
      )
    ) {
      frm.$wrapper.find('.form-sidebar > .form-attachments').hide();
    }
  },
};
