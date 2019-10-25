async function set_loyalty_details(frm) {
  const { customer, company, posting_date } = frm.doc;
  const { message: loyalty } = await frappe.call({
    method:
      'erpnext.accounts.doctype.loyalty_program.loyalty_program.get_loyalty_program_details_with_points',
    args: { customer, company },
  });
  console.log(loyalty);
  if (loyalty) {
    const {
      loyalty_program,
      tier_name: loyalty_program_tier,
      loyalty_points: current_points,
      expiry_duration,
    } = loyalty;
    frm.set_value({
      loyalty_program,
      loyalty_program_tier,
      current_points,
      expiry_date: frappe.datetime.add_days(posting_date, expiry_duration),
    });
  }
}

function set_loyalty_balance(frm) {
  const { points = 0, current_points = 0 } = frm.doc;
  frm.set_value('balance_points', points + current_points);
}

export default {
  customer: set_loyalty_details,
  posting_date: set_loyalty_details,
  points: set_loyalty_balance,
  current_points: set_loyalty_balance,
};
