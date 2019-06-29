import flowRight from 'lodash/flowRight';

import withSalesperson from './withSalesperson';
import withItemRates from './withItemRates';

export const extend_cart = flowRight([withSalesperson]);

export const extend_items = flowRight([withItemRates]);
