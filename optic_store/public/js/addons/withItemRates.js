export default function withItemRates(Items) {
  const isClass = Items instanceof Function || Items instanceof Class;
  if (!isClass) {
    return Items;
  }
  return class ItemsWithItemRates extends Items {
    get_item_html(item) {
      const {
        item_code,
        os_minimum_selling_rate: ms1 = 0,
        os_minimum_selling_2_rate: ms2 = 0,
      } = item;
      const $template = $('<div />').append(super.get_item_html(item));
      if (ms1 || ms2) {
        $(
          `<span>
          <div>MS1: ${format_currency(ms1, this.frm.doc.currency)}</div>
          <div>MS2: ${format_currency(ms2, this.frm.doc.currency)}</div>
          </span>`
        )
          .css({
            position: 'absolute',
            left: '0',
            top: '0',
            padding: '5px 9px',
            'background-color': 'rgba(141, 153, 166, 0.6)',
            color: '#fff',
            'border-radius': '3px',
            'font-size': '0.75em',
          })
          .appendTo(`a[data-item-code="${item_code}"] > div.image-field`);
      }
      return $template.html();
    }
  };
}
