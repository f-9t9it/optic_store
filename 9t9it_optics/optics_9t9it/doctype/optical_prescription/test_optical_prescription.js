/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test('test: Optical Prescription', function(assert) {
  let done = assert.async();

  // number of asserts
  assert.expect(1);

  frappe.run_serially([
    // insert a new Optical Prescription
    () =>
      frappe.tests.make('Optical Prescription', [
        // values to be set
        { key: 'value' },
      ]),
    () => {
      assert.equal(cur_frm.doc.key, 'value');
    },
    () => done(),
  ]);
});
