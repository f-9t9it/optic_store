function enable_sph_reading(frm) {
  frm.toggle_enable('sph_reading_right', frm.doc.add_type_right === '');
  frm.toggle_enable('sph_reading_left', frm.doc.add_type_left === '');
}

function handle_add_sph(frm) {
  const { sph_right = 0, add_right = 0, sph_left = 0, add_left = 0 } = frm.doc;
  frm.set_value('sph_reading_right', sph_right + add_right);
  frm.set_value('sph_reading_left', sph_left + add_left);
}

export default {
  onload: enable_sph_reading,
  sph_right: handle_add_sph,
  sph_left: handle_add_sph,
  add_right: handle_add_sph,
  add_left: handle_add_sph,
  add_type_right: enable_sph_reading,
  add_type_left: enable_sph_reading,
};
