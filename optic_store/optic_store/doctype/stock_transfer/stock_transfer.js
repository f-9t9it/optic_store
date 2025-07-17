frappe.ui.form.on('Stock Transfer', {
 refresh: function(frm) {
    showReceiveButton(frm) ;
 },
 onload_post_render: function(frm) {
    showReceiveButton(frm) ;
 }

});


function showReceiveButton(frm) {
  if(frm.doc.workflow_state === 'In Transit') {
  frappe.call({
  method: "optic_store.optic_store.doctype.stock_transfer.stock_transfer.showReceive",
  args: {
    branch: frm.doc.target_branch
  },
  callback: function(systemRoleRes) {
    console.log(systemRoleRes);
    if (systemRoleRes.message) {
    }
  }
});
  }
}