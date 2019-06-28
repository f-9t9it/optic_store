import flowRight from 'lodash/flowRight';

import withXzReport from './withXzReport';
import withSalesPerson, { paymentWithSalesPerson } from './withSalesPerson';
import withItemRates from './withItemRates';
import withPaymentValidation from './withPaymentValidation';
import withFieldsHidden from './withFieldsHidden';
import withTabbedMops from './withTabbedMops';
import withKeyboardShortcuts from './withKeyboardShortcuts';
import withGroupDiscount from './withGroupDiscount';
import withGiftCard from './withGiftCard';

export const extend_pos = flowRight([withKeyboardShortcuts, withXzReport]);

export const extend_cart = flowRight([withGroupDiscount, withSalesPerson]);

export const extend_items = flowRight([withItemRates]);

export const extend_payment = flowRight([
  withPaymentValidation,
  withGiftCard,
  withTabbedMops,
  withFieldsHidden,
  paymentWithSalesPerson,
]);
