import { make_data, make_multiselect } from './fields';

export default {
  filters: [
    make_multiselect({ fieldname: 'item_groups', options: 'Item Group' }),
    make_multiselect({ fieldname: 'brands', options: 'Brand' }),
    make_multiselect({ fieldname: 'item_codes', options: 'Item' }),
    make_data({ fieldname: 'item_name' }),
  ],
};
