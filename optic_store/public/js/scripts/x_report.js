async function set_missing_fields(frm) {
  const { user, pos_profile, start_time, end_time } = frm.doc;
  if (!user) {
    frm.set_value('user', frappe.session.user);
  }
  if (!pos_profile) {
    const { message: pos_profile = {} } = await frappe.call({
      method: 'erpnext.stock.get_item_details.get_pos_profile',
      args: { company: frappe.defaults.get_user_default('company') },
    });
    frm.set_value('pos_profile', pos_profile.name);
  }
  if (frm.doc.__islocal && !start_time) {
    frm.set_value('start_time', frappe.datetime.now_datetime());
  }
  if (!frm.doc.__islocal && frm.doc.docstatus === 0 && !end_time) {
    frm.set_value('end_time', frappe.datetime.now_datetime());
  }
}

async function set_report_details(frm) {
  const { user, pos_profile, start_time, end_time } = frm.doc;
  if (user && pos_profile && start_time && end_time) {
    await frappe.call({
      method: 'set_report_details',
      doc: frm.doc,
    });
    frm.refresh();
    calculate_cash(frm);
  }
}

async function calculate_cash(frm) {
  const {
    opening_cash = 0,
    closing_cash = 0,
    cash_sales = 0,
    cash_returns = 0,
    cash_pe_received = 0,
  } = frm.doc;
  const expected_cash = opening_cash + cash_sales + cash_returns + cash_pe_received;
  frm.set_value('expected_cash', expected_cash);
  frm.set_value('difference_cash', expected_cash - closing_cash);
}

export default {
  onload: function(frm) {
    frm.set_query('pos_profile', ({ user }) => ({ filters: { user } }));
  },
  refresh: set_missing_fields,
  user: set_report_details,
  pos_profile: async function(frm) {
    const { pos_profile } = frm.doc;
    if (pos_profile) {
      const { message: { company } = {} } = await frappe.db.get_value(
        'POS Profile',
        pos_profile,
        'company'
      );
      frm.set_value('company', company);
    }
    set_report_details(frm);
  },
  start_time: set_report_details,
  end_time: set_report_details,
  opening_cash: calculate_cash,
  closing_cash: calculate_cash,
};
