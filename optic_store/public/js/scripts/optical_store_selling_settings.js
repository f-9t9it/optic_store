export default {
  refresh: function(frm) {
    frm.set_query('cashback_expense_account', {
      filters: { root_type: 'Expense', is_group: 0 },
    });
  },
};
