# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, cint, add_days
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
    get_loyalty_program_details_with_points,
)
from functools import partial
from toolz import compose, pluck, unique, first, excepts

from optic_store.doc_events.sales_order import (
    validate_opened_xz_report,
    validate_rate_against_min_prices,
    before_insert as so_before_insert,
    before_save as so_before_save,
    before_submit as so_before_submit,
)
from optic_store.api.sales_invoice import validate_loyalty
from optic_store.api.cashback_program import (
    get_cashback_program,
    get_invoice_cashback_amount,
)


def before_naming(doc, method):
    naming_series = (
        frappe.db.get_value("Branch", doc.os_branch, "os_sales_invoice_naming_series")
        if doc.os_branch
        else None
    )
    if naming_series:
        doc.naming_series = naming_series


_get_gift_card_amounts = compose(
    sum,
    partial(map, lambda x: x.amount),
    partial(filter, lambda x: x.mode_of_payment == "Gift Card"),
)


def validate(doc, method):
    validate_opened_xz_report(doc.company, doc.pos_profile)
    gift_cards = map(
        lambda x: frappe.get_doc("Gift Card", x.gift_card), doc.os_gift_cards
    )
    map(partial(_validate_gift_card_expiry, doc.posting_date), gift_cards)
    if gift_cards:
        _validate_gift_card_balance(doc.payments, gift_cards)
    if cint(doc.redeem_loyalty_points):
        _validate_loyalty_card_no(doc.customer, doc.os_loyalty_card_no)
        validate_loyalty(doc)
    _validate_cashback(doc)
    if _contains_credit_note_payment(doc):
        _validate_credit_note(doc)
    if not doc.is_return:
        validate_rate_against_min_prices(doc)


def _contains_credit_note_payment(doc):
    credit_note_mop = frappe.db.get_single_value(
        "Optical Store Selling Settings", "credit_note_mop"
    )
    return cint(doc.is_pos) and credit_note_mop in [
        x.mode_of_payment for x in doc.payments
    ]


def _validate_gift_card_expiry(posting_date, giftcard):
    if giftcard.expiry_date and getdate(giftcard.expiry_date) < getdate(posting_date):
        frappe.throw(_("Gift Card {} has expired.".format(giftcard.gift_card_no)))


def _validate_gift_card_balance(payments, gift_cards):
    get_gift_card_balances = compose(sum, partial(map, lambda x: x.balance))
    if _get_gift_card_amounts(payments) > get_gift_card_balances(gift_cards):
        frappe.throw(_("Gift Card(s) has insufficient balance."))


def _validate_loyalty_card_no(customer, loyalty_card_no):
    if loyalty_card_no != frappe.db.get_value(
        "Customer", customer, "os_loyalty_card_no"
    ):
        frappe.throw(
            _(
                "Loyalty Card No: {} does not belong to this Customer".format(
                    loyalty_card_no
                )
            )
        )


def _validate_cashback(doc):
    cashback_mop = "Cashback"
    if cashback_mop not in [x.mode_of_payment for x in doc.payments if x.amount != 0]:
        return
    if not doc.os_cashback_receipt:
        frappe.throw(
            _(
                "Cashback Receipt required if using Mode of Payment {}".format(
                    frappe.bold(cashback_mop)
                )
            )
        )
    get_cb_redeemed_amt = compose(
        excepts(StopIteration, first, lambda _: 0),
        lambda _=None: [
            x.amount for x in doc.payments if x.mode_of_payment == cashback_mop
        ],
    )

    redeemed_amt = get_cb_redeemed_amt()
    balance_amt, expiry_date = frappe.db.get_value(
        "Cashback Receipt", doc.os_cashback_receipt, ["balance_amount", "expiry_date"]
    )
    if redeemed_amt > balance_amt:
        frappe.throw(
            _(
                "Redeemed cashback amount cannot be greater than available balance "
                "{}.".format(
                    frappe.bold(
                        frappe.utils.fmt_money(balance_amt, currency=doc.currency)
                    )
                )
            )
        )

    if getdate(doc.posting_date) > expiry_date:
        frappe.throw(_("Cashback Receipt has expired."))


def _validate_credit_note(doc):
    credit_note_mop, credit_note_expiry = frappe.db.get_single_value(
        "Optic Store Selling Settings", ["credit_note_mop", "credit_note_expiry"]
    )
    current_credit = frappe.db.sql(
        """
            SELECT SUM(credit_in_account_currency) - SUM(debit_in_account_currency)
            FROM `tabGL Entry`
            WHERE
                party_type = 'Customer' AND
                party = %(party)s AND
                company = %(company)s AND
                posting_date >= %(posting_date)s
        """,
        values={
            "party": doc.customer,
            "company": doc.company,
            "posting_date": frappe.utils.add_days(doc.posting_date, -credit_note_expiry)
            if credit_note_expiry
            else "1970-01-01",
        },
    )[0][0]
    if current_credit <= 0:
        frappe.throw(_("Customer does not have any credit note"))

    get_credit_note_amount = compose(
        lambda x: x.get("base_amount", 0),
        excepts(StopIteration, first, lambda _: {}),
        partial(filter, lambda x: x.mode_of_payment == credit_note_mop),
    )
    if get_credit_note_amount(doc.payments) > current_credit:
        frappe.throw(
            _(
                "Credit Note amount cannot exceed {}".format(
                    frappe.bold(
                        frappe.utils.fmt_money(current_credit, currency=doc.currency)
                    )
                )
            )
        )


def before_insert(doc, method):
    so_before_insert(doc, method)


def before_save(doc, method):
    so_before_save(doc, method)
    if doc.redeem_loyalty_points:
        lp_details = get_loyalty_program_details_with_points(
            doc.customer,
            loyalty_program=doc.loyalty_program,
            expiry_date=doc.posting_date,
            company=doc.company,
            silent=True,
        )
        doc.os_available_loyalty_points = lp_details.get("loyalty_points", 0)
    if doc.os_cashback_receipt:
        doc.os_cashback_balance = frappe.db.get_value(
            "Cashback Receipt", doc.os_cashback_receipt, "balance_amount"
        )


def before_submit(doc, method):
    """
        Service dates are set to None to disable monthly scheduled task
        `erpnext.accounts.deferred_revenue.convert_deferred_revenue_to_income`
    """
    so_before_submit(doc, method)
    for item in doc.items:
        is_gift_card = frappe.db.get_value("Item", item.item_code, "is_gift_card")
        if is_gift_card:
            item.service_start_date = None
            item.service_end_date = None
            item.service_stop_date = None


def on_submit(doc, method):
    _set_gift_card_validities(doc)
    _set_gift_card_balances(doc)
    _set_cashback_balances(doc)
    if doc.outstanding_amount == 0 and not doc.is_return:
        _create_cashback(doc)
    if doc.is_return:
        _update_cashback(doc)
    if doc.is_return and not doc.os_manual_return_dn and not doc.update_stock:
        _make_return_dn(doc)
    if _contains_credit_note_payment(doc):
        _reconcile_credit_note(doc)


def on_update_after_submit(doc, method):
    if doc.outstanding_amount == 0 and not doc.is_return:
        _create_cashback(doc)
    if doc.is_return:
        _update_cashback(doc)


def _set_gift_card_validities(doc):
    for row in doc.items:
        is_gift_card = frappe.db.get_value("Item", row.item_code, "is_gift_card")
        if is_gift_card and row.serial_no:
            for serial_no in row.serial_no.split("\n"):
                gift_card_no = frappe.db.exists(
                    "Gift Card", {"gift_card_no": serial_no}
                )
                if gift_card_no:
                    gift_card_validity = frappe.db.get_value(
                        "Item", row.item_code, "gift_card_validity"
                    )
                    frappe.db.set_value(
                        "Gift Card",
                        gift_card_no,
                        "expiry_date",
                        frappe.utils.add_days(doc.posting_date, gift_card_validity),
                    )


def _set_gift_card_balances(doc, cancel=False):
    amount_remaining = _get_gift_card_amounts(doc.payments)
    gift_cards = map(
        lambda x: frappe.get_doc("Gift Card", x.gift_card), doc.os_gift_cards
    )
    for gift_card in gift_cards:
        if amount_remaining < 0:
            break
        amount = min(
            amount_remaining,
            gift_card.balance if not cancel else gift_card.amount - gift_card.balance,
        )
        frappe.db.set_value(
            "Gift Card",
            gift_card.gift_card_no,
            "balance",
            gift_card.balance - amount if not cancel else gift_card.balance + amount,
        )
        amount_remaining -= amount


def _set_cashback_balances(doc, cancel=False):
    get_cb_redeemed_amt = compose(
        excepts(StopIteration, first, lambda _: 0),
        lambda _=None: [
            x.amount for x in doc.payments if x.mode_of_payment == "Cashback"
        ],
    )

    redeemed_amt = get_cb_redeemed_amt()
    if redeemed_amt > 0:
        cashback_receipt = frappe.get_doc("Cashback Receipt", doc.os_cashback_receipt)
        if cancel:
            cashback_receipt.redemptions = [
                x for x in cashback_receipt.redemptions if x.reference != doc.name
            ]
        else:
            cashback_receipt.append(
                "redemptions", {"reference": doc.name, "amount": redeemed_amt}
            )
        cashback_receipt.save(ignore_permissions=True)


def _create_cashback(doc):
    cashback_program = get_cashback_program(doc.os_branch, doc.posting_date)
    if not cashback_program or cashback_program.price_list != doc.selling_price_list:
        return
    cashback_amount = get_invoice_cashback_amount(doc.items, cashback_program)
    if not cashback_amount:
        return
    expiry_date = add_days(doc.posting_date, cashback_program.expiry_duration)
    frappe.get_doc(
        {
            "doctype": "Cashback Receipt",
            "origin": doc.name,
            "cashback_program": cashback_program.name,
            "expiry_date": expiry_date,
            "cashback_amount": cashback_amount,
        }
    ).insert(ignore_permissions=True)


def _update_cashback(doc, cancel=False):
    # only for returned invoices
    cashback_receipt_name = frappe.db.exists(
        "Cashback Receipt", {"origin": doc.return_against}
    )
    if not cashback_receipt_name:
        return
    cashback_receipt = frappe.get_doc("Cashback Receipt", cashback_receipt_name)
    cashback_program = frappe.get_doc(
        "Cashback Program", cashback_receipt.cashback_program
    )
    cashback_amount = get_invoice_cashback_amount(doc.items, cashback_program)
    if not cashback_amount:
        return
    updated_amount = (
        (cashback_receipt.cashback_amount - cashback_amount)
        if cancel
        else (cashback_receipt.cashback_amount + cashback_amount)
    )
    cashback_receipt.cashback_amount = updated_amount
    cashback_receipt.save()


def _delete_cashback(doc):
    cashback_receipt_name = frappe.db.exists("Cashback Receipt", {"origin": doc.name})
    if not cashback_receipt_name:
        return
    cashback_receipt = frappe.get_doc("Cashback Receipt", cashback_receipt_name)
    if len(cashback_receipt.redemptions) > 0:
        frappe.throw(
            _("{} cannot be cancelled because {} is redeemed.").format(
                frappe.get_desk_link("Sales Invoice", doc.name),
                "cancelled" if doc.docstatus == 2 else "returned",
                frappe.get_desk_link("Cashback Receipt", cashback_receipt_name),
            )
        )
    frappe.delete_doc(
        "Cashback Receipt", cashback_receipt.name, ignore_permissions=True
    )


def _make_return_dn(si_doc):
    get_dns = compose(list, unique, partial(pluck, "parent"), frappe.get_all)
    dns = get_dns(
        "Delivery Note Item",
        filters={"against_sales_invoice": si_doc.return_against, "docstatus": 1},
        fields=["parent"],
    )
    if not dns:
        return
    if len(dns) > 1:
        frappe.throw(
            _(
                "Multiple Delivery Notes found for this Sales Invoice. "
                "Please create Sales Return from the Delivery Note manually."
            )
        )
    doc = make_delivery_note(si_doc.return_against)
    for i, item in enumerate(doc.items):
        item.qty = si_doc.items[i].qty
        item.stock_qty = si_doc.items[i].stock_qty
    doc.is_return = 1
    doc.return_against = first(dns)
    doc.run_method("calculate_taxes_and_totals")
    doc.insert()
    doc.submit()


def before_cancel(doc, method):
    if _contains_credit_note_payment(doc):
        _reset_credit_notes_on_cancel(doc)


def on_cancel(doc, method):
    _set_gift_card_balances(doc, cancel=True)
    _set_cashback_balances(doc, cancel=True)
    if doc.is_return and not doc.os_manual_return_dn and not doc.update_stock:
        _cancel_return_dn(doc)
    if doc.is_return:
        _update_cashback(doc, cancel=True)
    else:
        _delete_cashback(doc)


def _cancel_return_dn(si_doc):
    get_dns = compose(list, unique, partial(pluck, "parent"), frappe.db.sql)
    dns = get_dns(
        """
            SELECT dni.parent AS parent
            FROM `tabDelivery Note Item` AS dni
            LEFT JOIN `tabDelivery Note` AS dn ON dn.name = dni.parent
            WHERE
                dn.docstatus = 1 AND
                dn.is_return = 1 AND
                dni.against_sales_invoice = %(against_sales_invoice)s
        """,
        values={"against_sales_invoice": si_doc.return_against},
        as_dict=1,
    )
    if not dns:
        return
    if len(dns) > 1:
        frappe.throw(
            _(
                "Multiple Delivery Notes found for this Sales Invoice. "
                "Please cancel from the return Delivery Note manually."
            )
        )
    doc = frappe.get_doc("Delivery Note", first(dns))
    for i, item in enumerate(doc.items):
        if (
            item.item_code != si_doc.items[i].item_code
            or item.qty != si_doc.items[i].qty
        ):
            frappe.throw(
                _(
                    "Mismatched <code>item_code</code> / <code>qty</code> "
                    "found in <em>items</em> table."
                )
            )
    doc.cancel()


def _reconcile_credit_note(doc):
    from erpnext.accounts.general_ledger import make_gl_entries

    credit_note_mop, credit_note_expiry = frappe.db.get_single_value(
        "Optic Store Selling Settings", ["credit_note_mop", "credit_note_expiry"]
    )

    issued_credit_notes = frappe.db.sql(
        """
            SELECT name, -outstanding_amount
            FROM `tabSales Invoice`
            WHERE
                company = %(company)s AND
                customer = %(customer)s AND
                status = 'Credit Note Issued' AND
                outstanding_amount < 0 AND
                posting_date >= %(posting_date)s
            ORDER BY posting_date
        """,
        values={
            "company": doc.company,
            "customer": doc.customer,
            "posting_date": frappe.utils.add_days(doc.posting_date, -credit_note_expiry)
            if credit_note_expiry
            else "1970-01-01",
        },
    )
    get_account_and_amount = compose(
        lambda x: (x.get("account"), x.get("base_amount")),
        excepts(StopIteration, first, lambda _: {}),
        partial(filter, lambda x: x.mode_of_payment == credit_note_mop),
    )
    account, to_allocate = get_account_and_amount(doc.payments)
    gl_entries = [
        doc.get_gl_dict(
            {
                "account": account,
                "against": doc.customer,
                "credit": to_allocate,
                "cost_center": doc.cost_center,
            },
            doc.party_account_currency,
        )
    ]
    for invoice, outstanding in issued_credit_notes:
        base_amount = min(outstanding, to_allocate)
        gl_entries.append(
            doc.get_gl_dict(
                {
                    "account": doc.debit_to,
                    "party_type": "Customer",
                    "party": doc.customer,
                    "against": account,
                    "debit": base_amount,
                    "against_voucher_type": "Sales Invoice",
                    "against_voucher": invoice,
                    "cost_center": doc.cost_center,
                    "remarks": "Credit Note Adjustment",
                },
                doc.party_account_currency,
            ),
        )
        to_allocate += base_amount
        if to_allocate == 0:
            break

    make_gl_entries(gl_entries)


def _reset_credit_notes_on_cancel(doc):
    redeemed_credit_notes = frappe.db.sql(
        """
            SELECT against_voucher, debit - credit
            FROM `tabGL Entry`
            WHERE
                voucher_type = 'Sales Invoice' AND
                voucher_no = %(voucher_no)s AND
                against_voucher_type = 'Sales Invoice' AND
                remarks = 'Credit Note Adjustment'
        """,
        values={"voucher_no": doc.name},
    )
    for invoice, amount in redeemed_credit_notes:
        doc = frappe.get_doc("Sales Invoice", invoice)
        bal = doc.outstanding_amount - amount
        doc.outstanding_amount = bal
        frappe.db.set_value("Sales Invoice", invoice, "outstanding_amount", bal)
        doc.set_status(update=True)
