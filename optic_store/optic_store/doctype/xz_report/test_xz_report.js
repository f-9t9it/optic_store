/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test('test: XZ Report', function(assert) {
  let done = assert.async();

  // number of asserts
  assert.expect(1);

  frappe.run_serially([
    // insert a new XZ Report
    () =>
      frappe.tests.make('XZ Report', [
        // values to be set
        { key: 'value' },
      ]),
    () => {
      assert.equal(cur_frm.doc.key, 'value');
    },
    () => done(),
  ]);
});
