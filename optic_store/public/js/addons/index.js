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
import withCashback from './withCashback';
import withLoyaltyCard from './withLoyaltyCard';
import withBranch from './withBranch';
import withItemListOverride from './withItemListOverride';
import withRecall from './withRecall';

export const extend_pos = flowRight([withKeyboardShortcuts, withXzReport, withBranch]);

export const extend_cart = flowRight([withRecall, withGroupDiscount, withSalesPerson]);

export const extend_items = flowRight([withItemRates, withItemListOverride]);

export const extend_payment = flowRight([
  withLoyaltyCard,
  withCashback,
  withAmountValidation,
  withGiftCard,
  withTabbedMops,
  withFieldsHidden,
  withPaymentValidation,
  paymentWithSalesPerson,
]);
