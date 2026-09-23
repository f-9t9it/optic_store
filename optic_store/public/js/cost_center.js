frappe.ui.form.on(cur_frm.doctype, {
    cost_center: function(frm) {
        if (frm.doc.cost_center) {
        for (let i = 0; i < frm.doc.items.length; i++) {
            frm.doc.items[i].cost_center = frm.doc.cost_center;
        }
        frm.refresh_field('items');
        }
    },
    items_add: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (frm.doc.cost_center) {
            row.cost_center = frm.doc.cost_center;
            frm.refresh_field('items');
        }
    }

})
