export default {
  refresh: async function(frm) {
    if (frm.doc.__islocal) {
      const { message: branch } = await frappe.call({
        method: 'optic_store.api.customer.get_user_branch',
      });
      frm.set_value('os_branch', branch);
    }
  },
};
