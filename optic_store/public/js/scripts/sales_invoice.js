import sumBy from 'lodash/sumBy';

import {
  render_prescription,
  set_fields,
  setup_orx_name,
  apply_group_discount,
  handle_gift_card_entry,
  setup_employee_queries,
  set_spec_types_options,
  hide_actions,
} from './sales_order';
import DeliverDialog from '../frappe-components/DeliverDialog';

function set_gift_card_payment(frm) {
  // do nothing for now
  return;
  const payments = frm.get_field('payments');
  if (payments) {
    const row =
      (payments.grid.grid_rows || [])
        .map(({ doc }) => doc)
        .find(({ mode_of_payment }) => mode_of_payment === 'Gift Card') ||
      frappe.model.add_child(frm.doc, 'Sales Invoice Payment', 'payments');

    const amount = sumBy(frm.doc.os_gift_cards, 'balance');
    const { rounded_total, grand_total } = frm.doc;

    frappe.model.set_value(
      row.doctype,
      row.name,
      'amount',
      Math.min(amount, rounded_total || grand_total)
    );
    payments.refresh();
  }
}

async function render_qol_button(frm) {
  if (frm.doc.docstatus === 1) {
    const actual_qty = frm.doc.items.reduce((a, { qty }) => a + qty, 0);
    const delivered_qty = frm.doc.items.reduce(
      (a, { delivered_qty }) => a + delivered_qty,
      0
    );
    const { status, update_stock } = frm.doc;
    const { message: so_statuses = [] } = await frappe.call({
      method: 'optic_store.api.sales_invoice.get_ref_so_statuses',
      args: { sales_invoice: frm.doc.name },
    });

    const can_be_paid = ['Unpaid', 'Overdue'].includes(status);
    const can_be_collected =
      !so_statuses.some(state => state !== 'Ready to Deliver') &&
      cint(update_stock) !== 1 &&
      actual_qty > delivered_qty;

    if (can_be_paid) {
      frm.add_custom_button(__('Payment Top Up'), function() {
        const deliver = false;
        frm.deliver_dialog && frm.deliver_dialog.payment_and_deliver(frm, deliver);
      });
    }

    if (can_be_collected) {
      frm.add_custom_button(__('Collect Order'), function() {
        const deliver = true;
        frm.deliver_dialog && frm.deliver_dialog.payment_and_deliver(frm, deliver);
      });
    }

    if (!can_be_paid || !can_be_collected) {
      frm.add_custom_button(__('Print Invoice'), function() {
        frm.deliver_dialog && frm.deliver_dialog.print(frm);
      });
    }
  }
}

function render_return_button(frm) {
  const { docstatus, is_return, outstanding_amount = 0, grand_total = 0 } = frm.doc;
  if (
    docstatus === 1 &&
    !is_return &&
    (outstanding_amount >= 0 || Math.abs(flt(outstanding_amount)) < flt(grand_total)) &&
    ['Accounts Manager', 'Accounts User', 'System Manager'].some(role =>
      frappe.user_roles.includes(role)
    )
  ) {
    frm.add_custom_button('Return / Credit Note', function() {
      frappe.model.open_mapped_doc({
        method:
          'erpnext.accounts.doctype.sales_invoice.sales_invoice.make_sales_return',
        frm,
      });
    });
  }
}

async function get_cost_center(frm) {
  if (frm.os_cost_center) {
    return frm.os_cost_center;
  }
  const { message: { os_cost_center } = {} } = await frappe.db.get_value(
    'Branch',
    frm.doc.os_branch,
    'os_cost_center'
  );
  frm.os_cost_center = os_cost_center;
  return os_cost_center;
}

export async function set_cost_center(frm) {
  const { os_branch } = frm.doc;
  if (os_branch) {
    const cost_center = await get_cost_center(frm);
    frm.doc.items.forEach(({ doctype: cdt, name: cdn }) => {
      frappe.model.set_value(cdt, cdn, 'cost_center', cost_center);
    });
  }
}

export async function handle_items_cost_center(frm, cdt, cdn) {
  const { cost_center } = frappe.get_doc(cdt, cdn);
  const branch_cost_center = await get_cost_center(frm);
  if (branch_cost_center !== cost_center) {
    frappe.model.set_value(cdt, cdn, 'cost_center', branch_cost_center);
  }
}

async function set_naming_series(frm) {
  const { os_branch: branch } = frm.doc;
  if (branch) {
    const {
      message: { os_sales_invoice_naming_series } = {},
    } = await frappe.db.get_value('Branch', branch, 'os_sales_invoice_naming_series');
    frm.set_value('naming_series', os_sales_invoice_naming_series);
  }
}

export const sales_invoice_item = {
  items_add: handle_items_cost_center,
};

export const sales_invoice_gift_card = {
  balance: set_gift_card_payment,
  os_gift_cards_remove: set_gift_card_payment,
};

export default {
  setup: async function(frm) {
    const { invoice_pfs = [], invoice_mops = [] } = await frappe.db.get_doc(
      'Optical Store Settings'
    );
    const print_formats = invoice_pfs.map(({ print_format }) => print_format);
    const mode_of_payments = invoice_mops.map(({ mode_of_payment }) => mode_of_payment);
    frm.deliver_dialog = new DeliverDialog(print_formats, mode_of_payments);
  },
  onload: async function(frm) {
    setup_employee_queries(frm);
    set_spec_types_options(frm);
    if (frm.is_new()) {
      await set_fields(frm);
      if (frm.doc.items.length > 0) {
        set_cost_center(frm);
      }
    }
  },
  refresh: function(frm) {
    frm.set_query('gift_card', 'os_gift_cards', function() {
      return {
        filters: [['balance', '>', 0]],
      };
    });
    render_prescription(frm);
    render_qol_button(frm);

    hide_actions(frm);
    render_return_button(frm);
  },
  os_branch: function(frm) {
    set_naming_series(frm);
    set_cost_center(frm);
  },
  customer: setup_orx_name,
  orx_type: setup_orx_name,
  orx_name: render_prescription,
  orx_group_discount: apply_group_discount,
  os_gift_card_entry: handle_gift_card_entry,
  redeem_loyalty_points: function(frm) {
    frm.toggle_reqd('os_loyalty_card_no', frm.doc.redeem_loyalty_points);
  },
};
