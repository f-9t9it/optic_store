import flowRight from 'lodash/flowRight';

import withXzReport from './withXzReport';
import withSalesPerson, { paymentWithSalesPerson } from './withSalesPerson';
import withItemRates from './withItemRates';
import withPaymentValidation from './withPaymentValidation';
import withAmountValidation from './withAmountValidation';
import withFieldsHidden from './withFieldsHidden';
import withTabbedMops from './withTabbedMops';
import withKeyboardShortcuts from './withKeyboardShortcuts';
import withGroupDiscount from './withGroupDiscount';
import withGiftCard from './withGiftCard';
import withLoyaltyCard from './withLoyaltyCard';

export const extend_pos = flowRight([withKeyboardShortcuts, withXzReport]);

export const extend_cart = flowRight([withGroupDiscount, withSalesPerson]);

export const extend_items = flowRight([withItemRates]);

export const extend_payment = flowRight([
  withLoyaltyCard,
  withAmountValidation,
  withGiftCard,
  withTabbedMops,
  withFieldsHidden,
  withPaymentValidation,
  paymentWithSalesPerson,
]);
