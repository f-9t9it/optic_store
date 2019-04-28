/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test('test: Sales Order Bulk Update', function(assert) {
  let done = assert.async();

  // number of asserts
  assert.expect(1);

  frappe.run_serially([
    // insert a new Sales Order Bulk Update
    () =>
      frappe.tests.make('Sales Order Bulk Update', [
        // values to be set
        { key: 'value' },
      ]),
    () => {
      assert.equal(cur_frm.doc.key, 'value');
    },
    () => done(),
  ]);
});
