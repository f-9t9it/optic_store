# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import add_days, flt
from frappe.model.document import Document
from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
    get_loyalty_program_details_with_points,
)
from erpnext.accounts.doctype.loyalty_point_entry.loyalty_point_entry import (
    get_loyalty_point_entries,
    get_redemption_details,
)


class CustomLoyaltyEntry(Document):
    def before_save(self):
        loyalty = get_loyalty_program_details_with_points(
            self.customer, company=self.company
        )
        if not self.expiry_date:
            self.expiry_date = add_days(self.posting_date, loyalty.expiry_duration)
        self.loyalty_program = loyalty.loyalty_program
        self.loyalty_program_tier = loyalty.tier_name
        self.current_points = loyalty.loyalty_points
        self.balance_points = self.current_points + self.points

    def on_submit(self):
        if self.points > 0:
            self._add_points()
        else:
            self._deduct_points()

    def on_cancel(self):
        self._delete_entry()

    def _add_points(self):
        # copied from sales_invoice:make_loyalty_point_entry
        frappe.get_doc(
            {
                "doctype": "Loyalty Point Entry",
                "company": self.company,
                "loyalty_program": self.loyalty_program,
                "loyalty_program_tier": self.loyalty_program_tier,
                "customer": self.customer,
                "os_custom_loyalty_entry": self.name,
                "loyalty_points": self.points,
                "expiry_date": self.expiry_date,
                "posting_date": self.posting_date,
            }
        ).save(ignore_permissions=1)

    def _deduct_points(self):
        # copied from sales_invoice:apply_loyalty_points
        loyalty_point_entries = get_loyalty_point_entries(
            self.customer, self.loyalty_program, self.company, self.posting_date
        )
        redemption_details = get_redemption_details(
            self.customer, self.loyalty_program, self.company
        )

        points_to_redeem = -self.points
        for lpe in loyalty_point_entries:
            if lpe.os_custom_loyalty_entry == self.name:
                continue
            available_points = lpe.loyalty_points - flt(
                redemption_details.get(lpe.name)
            )
            redeemed_points = min(points_to_redeem, available_points)
            frappe.get_doc(
                {
                    "doctype": "Loyalty Point Entry",
                    "company": self.company,
                    "loyalty_program": self.loyalty_program,
                    "loyalty_program_tier": lpe.loyalty_program_tier,
                    "customer": self.customer,
                    "os_custom_loyalty_entry": self.name,
                    "redeem_against": lpe.name,
                    "loyalty_points": -1 * redeemed_points,
                    "expiry_date": lpe.expiry_date,
                    "posting_date": self.posting_date,
                }
            ).save(ignore_permissions=1)
            points_to_redeem -= redeemed_points
            if points_to_redeem < 1:
                break

    def _delete_entry(self):
        lpe = frappe.db.exists(
            "Loyalty Point Entry", {"os_custom_loyalty_entry": self.name}
        )
        if not lpe:
            return

        if frappe.get_all("Loyalty Point Entry", filters={"redeem_against": lpe}):
            frappe.throw(_("Cannot be cancelled because points are already redeemed"))

        frappe.delete_doc("Loyalty Point Entry", lpe)
