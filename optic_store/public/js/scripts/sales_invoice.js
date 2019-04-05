export default {
  refresh: function(frm) {
    frm.set_query('gift_card', 'os_gift_cards', function() {
      return {
        filters: [['balance', '>', 0]],
      };
    });
  },
};
