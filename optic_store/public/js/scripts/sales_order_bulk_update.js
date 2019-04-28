import Vue from 'vue/dist/vue.js';

function render_actions(frm) {
  const { company, state, action, orders_query = [], orders_process = [] } = frm.doc;
  frm.page.btn_primary.toggleClass('disabled', !(orders_process.length > 0) || !action);
  frm.page.btn_secondary.text(__(orders_query.length > 0 ? 'Refresh' : 'Fetch'));
  frm.page.btn_secondary.toggleClass('disabled', !company || !state);
}

function fetch_sales_orders(frm) {
  return async function() {
    frm.clear_table('orders_query');
    frm.clear_table('orders_process');
    const { company, state, branch, from_date, to_date } = frm.doc;
    const { message: sales_orders = [] } = await frappe.call({
      method: 'optic_store.api.sales_order.get_sales_orders',
      args: { company, state, branch, from_date, to_date },
      freeze: true,
      freeze_message: __('Fetching Sales Orders'),
    });
    sales_orders.forEach(({ sales_order, lab_tech }) => {
      const { name } = frappe.model.add_child(
        frm.doc,
        'Bulk Update Order',
        'orders_query'
      );
      frappe.model.set_value('Bulk Update Order', name, { sales_order, lab_tech });
    });
    frm.refresh();
  };
}

function update_sales_orders(frm) {
  return async function() {
    const { orders_process = [], action, lab_tech } = frm.doc;
    await frappe.call({
      method: 'optic_store.api.sales_order.update_sales_orders',
      args: {
        sales_orders: orders_process.map(({ sales_order }) => sales_order),
        action,
        lab_tech,
      },
      freeze: true,
      freeze_message: __('Updating Sales Orders'),
    });
    fetch_sales_orders(frm)();
  };
}

export const bulk_update_order = {
  orders_query_add: render_actions,
  orders_query_remove: render_actions,
  orders_process_add: render_actions,
  orders_process_remove: render_actions,
};

export default {
  setup: async function(frm) {
    const { message: states } = await frappe.call({
      method: 'optic_store.api.sales_order.get_workflow_states',
    });
    frm.set_df_property('state', 'options', states);
  },
  refresh: function(frm) {
    frm.disable_save();
    frm.page.clear_icons();
    frm.page.set_primary_action(__('Update'), update_sales_orders(frm));
    frm.page.set_secondary_action(__('Fetch'), fetch_sales_orders(frm));
    render_actions(frm);
  },
  company: render_actions,
  state: async function(frm) {
    render_actions(frm);
    const { state } = frm.doc;
    if (state) {
      const { message: actions } = await frappe.call({
        method: 'optic_store.api.sales_order.get_next_workflow_actions',
        args: { state },
      });
      frm.set_df_property('action', 'options', actions);
    }
  },
  action: function(frm) {
    const { action } = frm.doc;
    frm.toggle_display('lab_tech', ['Proceed to Deliver'].includes(action));
    render_actions(frm);
  },
  scan_order: function(frm) {
    function set_desc(description) {
      frm.get_field('scan_order').set_new_description(description);
    }
    const { scan_order, orders_query = [], orders_process = [] } = frm.doc;
    if (scan_order) {
      const selected = orders_query.find(
        ({ sales_order }) => sales_order === scan_order
      );
      if (!selected) {
        set_desc(__('Sales Order not present in queried result'));
      } else {
        const already_present = orders_process
          .map(({ sales_order }) => sales_order)
          .includes(scan_order);
        if (!already_present) {
          const { sales_order, lab_tech } = selected;
          const { name } = frappe.model.add_child(
            frm.doc,
            'Bulk Update Order',
            'orders_process'
          );
          frappe.model.set_value('Bulk Update Order', name, { sales_order, lab_tech });
        }
        frappe.model.clear_doc('Bulk Update Order', selected.name);
        frm.refresh();
        set_desc('');
        frm.set_value('scan_order', null);
      }
    }
    return false;
  },
};
