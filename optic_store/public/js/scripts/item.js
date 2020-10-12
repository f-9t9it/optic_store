import PricelistDialog from '../frappe-components/PricelistDialog';

function toggle_naming(frm) {
  const { manual_item_code } = frm.doc;
  frm.toggle_display('item_code', manual_item_code);
  frm.toggle_reqd('item_code', manual_item_code);
  frm.toggle_display('naming_series', !manual_item_code);
}

function enable_gift_card(frm) {
  const { is_gift_card } = frm.doc;
  frm.toggle_reqd('gift_card_value', is_gift_card);
  frm.set_value('has_serial_no', is_gift_card);
  frm.set_value('deferred_revenue_account', is_gift_card);
}

function render_price_button(frm) {
  frm.add_custom_button(__('Set Prices'), function() {
    frm.pricelist_dialog.set_prices(frm);
    frm.pricelist_dialog.render_dialog(frm);
  });
}

function hide_actions(frm) {
  // this is a hack to make native ui elements
  if (!frm.doc.__islocal && frm.doc.is_stock_item) {
    const hide_buttons = setInterval(() => {
      const move_btns = frm.dashboard.wrapper.find('.btn-move');
      if (move_btns.length > 0) {
        move_btns.parent().hide();
        clearInterval(hide_buttons);
      }
    }, 60);
  }
}

export default {
  setup: async function(frm) {
    const { price_lists = [] } = await frappe.db.get_doc('Optical Store Settings');
    const price_lists_scrubbed = price_lists.map(({ price_list }) => price_list);
    frm.pricelist_dialog = new PricelistDialog(price_lists_scrubbed);
  },
  refresh: function(frm) {
    frm.toggle_display('manual_item_code', frm.doc.__islocal);
    if (!frm.doc.__islocal) {
      render_price_button(frm);
    }

    // hide stock actions beside stock level rows
    hide_actions(frm);
  },
  manual_item_code: toggle_naming,
  is_gift_card: enable_gift_card,
  os_commission_by: function(frm) {
    const { os_commission_by } = frm.doc;
    frm.fields_dict['os_commissions'].grid.set_column_disp(
      'commission_rate',
      os_commission_by === 'Percentage'
    );
    frm.fields_dict['os_commissions'].grid.set_column_disp(
      'commission_amount',
      os_commission_by === 'Amount'
    );
    const field_map = {
      Percentage: 'commission_rate',
      Amount: 'commission_amount',
    };
    if (field_map[os_commission_by]) {
      frm.fields_dict['os_commissions'].grid.grid_rows
        .map(({ doc }) => doc)
        .map(({ doctype: cdt, name: cdn }) =>
          frappe.model.set_value(cdt, cdn, field_map[os_commission_by], null)
        );
    }
  },
};
