// Copyright (c) 2019, 9T9IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Optical Prescription', {
  onload: function(frm) {
    frm.trigger('enable_sph_reading');
  },
  sph_right: function(frm) {
    frm.trigger('handle_add_sph');
  },
  sph_left: function(frm) {
    frm.trigger('handle_add_sph');
  },
  add_right: function(frm) {
    frm.trigger('handle_add_sph');
  },
  add_left: function(frm) {
    frm.trigger('handle_add_sph');
  },
  add_type_right: function(frm) {
    frm.trigger('enable_sph_reading');
  },
  add_type_left: function(frm) {
    frm.trigger('enable_sph_reading');
  },
  enable_sph_reading: function(frm) {
    frm.toggle_enable('sph_reading_right', frm.doc.add_type_right === '');
    frm.toggle_enable('sph_reading_left', frm.doc.add_type_left === '');
  },
  handle_add_sph: function(frm) {
    const {
      sph_right = 0,
      add_right = 0,
      sph_left = 0,
      add_left = 0,
    } = frm.doc;
    frm.set_value('sph_reading_right', sph_right + add_right);
    frm.set_value('sph_reading_left', sph_left + add_left);
  },
});
