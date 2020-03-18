function setup_queries(frm) {
  frm.set_query('price_list', ({}) => ({ filters: { enabled: 1, selling: 1 } }));
  frm.set_query('branch', 'branches', () => ({
    filters: { disabled: 0 },
  }));
  frm.set_query('item_group', 'item_groups', () => ({
    filters: { is_group: 0 },
  }));
  frm.set_query('expense_account', ({ company }) => ({
    filters: { company, root_type: 'Expense' },
  }));
  frm.set_query('cost_center', ({ company }) => ({
    filters: { company, is_group: 0 },
  }));
}

export default {
  setup: setup_queries,
};
