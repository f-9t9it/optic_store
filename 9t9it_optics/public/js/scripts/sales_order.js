function orx_query(frm) {
  const { customer, orx_type: type } = frm.doc;
  if (customer && type) {
    frm.set_query('orx_name', function() {
      return {
        query: '9t9it_optics.api.optical_prescription.query_latest',
        filters: { customer, type },
      };
    });
  }
}

export default {
  customer: orx_query,
  orx_type: orx_query,
};
