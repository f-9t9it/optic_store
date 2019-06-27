import flowRight from 'lodash/flowRight';

import withXzReport from './withXzReport';
import withSalesperson from './withSalesperson';
import withItemRates from './withItemRates';

export const extend_pos = flowRight([withXzReport]);

export const extend_cart = flowRight([withSalesperson]);

export const extend_items = flowRight([withItemRates]);
