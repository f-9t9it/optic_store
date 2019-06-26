import flowRight from 'lodash/flowRight';

import withSalesperson from './withSalesperson';

export const extend_cart = flowRight([withSalesperson]);
