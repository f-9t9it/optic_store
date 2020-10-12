export default function withItemListOverride(Items) {
  const isClass = Items instanceof Function || Items instanceof Class;
  if (!isClass) {
    return Items;
  }
  return class ItemsWithItemListOverride extends Items {
    async get_items({
      start = 0,
      page_length = 40,
      search_value = '',
      item_group = this.parent_item_group,
    } = {}) {
      const { customer, pos_profile, selling_price_list: price_list } = this.frm.doc;
      const { message } = await frappe.call({
        method: 'erpnext.selling.page.point_of_sale.point_of_sale.get_items',
        freeze: true,
        args: {
          start,
          page_length,
          price_list,
          item_group,
          search_value,
          pos_profile,
          customer,
        },
      });
      return message;
    }
  };
}
