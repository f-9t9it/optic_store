export default function withBranch(Pos) {
  const isClass = Pos instanceof Function || Pos instanceof Class;
  if (!isClass) {
    return Pos;
  }
  return class PosWithBranch extends Pos {
    async make_sales_invoice_frm() {
      await super.make_sales_invoice_frm();
      const { message: branch } = await frappe.call({
        method: 'optic_store.api.customer.get_user_branch',
      });
      this.frm.set_value('os_branch', branch);
    }
  };
}
