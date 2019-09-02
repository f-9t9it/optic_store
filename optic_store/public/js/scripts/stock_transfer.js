import Vue from 'vue/dist/vue.js';
import sumBy from 'lodash/sumBy';

import StockTransferDashboard from '../components/StockTransferDashboard.vue';
import { scan_barcode } from './extensions';

function set_queries(frm) {
  ['source_warehouse', 'target_warehouse'].forEach(field => {
    frm.set_query(field, function({ company }) {
      return { company, is_group: 0 };
    });
  });
  frm.set_query('batch_no', 'items', function(_, cdt, cdn) {
    const { item_code } = frappe.get_doc(cdt, cdn) || {};
    return { filters: { item: item_code } };
  });
}

function calc_and_set_row_amount(frm, cdt, cdn) {
  const { qty = 0, basic_rate = 0 } = frappe.model.get_doc(cdt, cdn) || {};
  const amount = qty * basic_rate;
  frappe.model.set_value(cdt, cdn, 'amount', qty * basic_rate);
  frappe.model.set_value(cdt, cdn, 'valuation_rate', amount / qty);
}

async function calc_and_set_total_amount(frm, cdt, cdn) {
  const items = frm.fields_dict.items.grid.grid_rows.map(({ doc }) => doc);
  frm.set_value('total_value', sumBy(items, 'amount'));
  return frm.set_value('total_qty', sumBy(items, 'qty'));
}

async function set_source_branch(frm) {
  const { message: branch } = await frappe.call({
    method: 'optic_store.api.customer.get_user_branch',
  });
  frm.set_value('source_branch', branch);
}

function render_dashboard_data(frm) {
  if (!frm.doc.__islocal) {
    frm.dashboard.show();
    const $wrapper = $('<div class="form-dashboard-section custom" />').appendTo(
      frm.dashboard.wrapper
    );
    const { items } = frm.doc;
    frm.brand_summary_vue = new Vue({
      data: { items },
      el: $wrapper.html('<div />').children()[0],
      render: function(h) {
        return h(StockTransferDashboard, { props: { items: this.items } });
      },
    });
  }
}

export const stock_transfer_item = {
  item_code: async function(frm, cdt, cdn) {
    const item = frappe.model.get_doc(cdt, cdn) || {};
    const { source_warehouse: warehouse, company } = frm.doc;
    const { item_code } = item;
    frappe.model.set_value(cdt, cdn, {
      qty: item_code ? 1 : 0,
      conversion_factor: 1,
    });
    if (item_code) {
      const {
        item_name,
        item_group,
        brand,
        has_batch_no,
        has_serial_no,
      } = await frappe.db.get_doc('Item', item_code);
      if ((has_batch_no && !item.batch_no) || (has_serial_no && !item.serial_no)) {
        // do not show selector if either batch_no or serial_no is used in scan_barcode
        erpnext.show_serial_batch_selector(
          frm,
          { item_code, has_batch_no, has_serial_no, warehouse },
          ({ batch_no, serial_no, qty }) => {
            frappe.model.set_value(cdt, cdn, 'qty', qty);
            if (has_batch_no) {
              frappe.model.set_value(cdt, cdn, 'batch_no', batch_no);
            }
            if (has_serial_no) {
              frappe.model.set_value(cdt, cdn, 'serial_no', serial_no);
            }
          }
        );
      } else {
        frappe.model.set_value(cdt, cdn, { item_name, item_group, brand });
        frm.refresh_field('items');
      }
      const [posting_date, posting_time] = frm.doc.outgoing_datetime.split(' ');
      const { serial_no, qty } = frappe.model.get_doc(cdt, cdn);
      const { message: basic_rate = 0 } = await frappe.call({
        method: 'erpnext.stock.utils.get_incoming_rate',
        args: {
          args: {
            item_code,
            posting_date,
            posting_time,
            warehouse,
            serial_no,
            company,
            qty,
          },
        },
      });
      frappe.model.set_value(cdt, cdn, 'basic_rate', basic_rate);
    }
  },
  qty: async function(frm) {
    await calc_and_set_row_amount(frm);
    if (frm.brand_summary_vue) {
      frm.brand_summary_vue.items = frm.doc.items;
    }
  },
  brand: function(frm) {
    if (frm.brand_summary_vue) {
      frm.brand_summary_vue.items = frm.doc.items;
    }
  },
  basic_rate: calc_and_set_row_amount,
  amount: calc_and_set_total_amount,
  items_remove: calc_and_set_row_amount,
};

function set_route_to_list(frm) {
  frm.page.actions.find('a.grey-link:contains("Receive")').on('click', function() {
    frappe.set_route('List', 'Stock Transfer');
  });
}

function toggle_incoming_datetime(frm) {
  frm.toggle_enable('incoming_datetime', frm.doc.workflow_state === 'In Transit');
  // frm.toggle_reqd('incoming_datetime', frm.doc.workflow_state === 'In Transit');
}

async function toggle_cancel_action(frm) {
  const { message: branch } = await frappe.call({
    method: 'optic_store.api.customer.get_user_branch',
  });
  frm.page.actions
    .find('a.grey-link:contains("Cancel")')
    .toggle(
      frm.doc.workflow_state === 'In Transit' && branch !== frm.doc.target_branch
    );
}

export default {
  setup: set_queries,
  refresh: function(frm) {
    if (frm.doc.__islocal) {
      frm.set_value('outgoing_datetime', frappe.datetime.now_datetime());
      set_source_branch(frm);
    }
    toggle_incoming_datetime(frm);
    render_dashboard_data(frm);
  },
  onload_post_render: function(frm) {
    // workflow related ui changes need to be here
    if (frm.doc.workflow_state === 'In Transit') {
      set_route_to_list(frm);
    }
  },
  company: set_queries,
  scan_barcode: function(frm) {
    if (!frm.doc.items) {
      frappe.model.add_child(frm.doc, 'Stock Transfer Item', 'items');
      frm.refresh_field('items');
    }
    scan_barcode(frm);
  },
};
