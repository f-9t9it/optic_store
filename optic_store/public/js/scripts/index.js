import optical_prescription from './optical_prescription';
import optical_store_settings from './optical_store_settings';
import optical_store_selling_settings from './optical_store_selling_settings';
import group_discount from './group_discount';
import gift_card from './gift_card';
import stock_transfer, { stock_transfer_item } from './stock_transfer';
import sales_order_bulk_update, { bulk_update_order } from './sales_order_bulk_update';
import xz_report from './xz_report';
import sms_template from './sms_template';
import custom_loyalty_entry from './custom_loyalty_entry';
import custom_purchase_receipt from './custom_purchase_receipt';
import email_alerts from './email_alerts';
import cashback_program from './cashback_program';
import * as extensions from './extensions';

export { default as payment_entry } from './payment_entry';
export {
  sales_invoice_item,
  sales_invoice_gift_card,
  sales_invoice_list,
  default as sales_invoice,
} from './sales_invoice';
export { delivery_note_item, default as delivery_note } from './delivery_note';
export { default as sales_order } from './sales_order';
export { default as customer } from './customer';
export { default as customer_qe } from './customer_qe';
export { default as employee } from './employee';
export { default as branch } from './branch';
export { default as item } from './item';
export { default as optical_prescription_qe } from './optical_prescription_qe';
export { default as batch_qe } from './batch_qe';
export { default as stock_entry } from './stock_entry';
export { default as salary_slip } from './salary_slip';
export { default as payroll_entry } from './payroll_entry';

export default {
  optical_prescription,
  optical_store_settings,
  optical_store_selling_settings,
  group_discount,
  gift_card,
  stock_transfer,
  stock_transfer_item,
  sales_order_bulk_update,
  bulk_update_order,
  xz_report,
  sms_template,
  custom_loyalty_entry,
  custom_purchase_receipt,
  email_alerts,
  cashback_program,
  extensions,
};
