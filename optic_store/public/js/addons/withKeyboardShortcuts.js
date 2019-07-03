export default function withKeyboardShortcuts(Pos) {
  const isClass = Pos instanceof Function || Pos instanceof Class;
  if (!isClass) {
    return Pos;
  }
  return class PosWithKeyboardShortcuts extends Pos {
    make() {
      $(document).on('keydown', e => {
        if (frappe.get_route_str() === 'point-of-sale') {
          if (this.cart && e.keyCode === 120) {
            e.preventDefault();
            this.cart.events.on_numpad(__('Pay'));
          } else if (e.ctrlKey && e.keyCode === 80) {
            e.preventDefault();
            if (this.frm.doc.docstatus === 1) {
              if (this.frm.msgbox && this.frm.msgbox.is_visible) {
                this.frm.msgbox.hide();
              }
              this.frm.print_preview.printit();
            }
          } else if (e.ctrlKey && e.keyCode === 66) {
            e.preventDefault();
            if (this.frm.msgbox && this.frm.msgbox.is_visible) {
              this.frm.msgbox.hide();
            }
            this.make_new_invoice();
          }
        }
      });
      return super.make();
    }
  };
}
