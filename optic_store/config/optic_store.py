# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Documents"),
            "items": [
                {"type": "doctype", "name": "Sales Order", "label": _("Sales Order")},
                {
                    "type": "doctype",
                    "name": "Optical Prescription",
                    "label": _("Optical Prescription"),
                },
                {
                    "type": "doctype",
                    "name": "Stock Transfer",
                    "label": _("Stock Transfer"),
                },
                {
                    "type": "doctype",
                    "name": "Custom Purchase Receipt",
                    "label": _("Custom Purchase Receipt"),
                },
                {
                    "type": "doctype",
                    "name": "Custom Loyalty Entry",
                    "label": _("Custom Loyalty Entry"),
                },
                {
                    "type": "doctype",
                    "name": "Old Sales Record",
                    "label": _("Old Sales Record"),
                },
            ],
        },
        {
            "label": _("Tools"),
            "items": [
                {"type": "doctype", "name": "XZ Report", "label": _("XZ Report")},
                {"type": "page", "name": "pos", "label": _("POS")},
                {
                    "type": "doctype",
                    "name": "Sales Order Bulk Update",
                    "label": _("Sales Order Bulk Update"),
                },
            ],
        },
        {
            "label": _("Reports"),
            "items": [
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Item-wise Stock",
                    "label": _("Item-wise Stock"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Brand-wise Stock",
                    "label": _("Brand-wise Stock"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Branch Stock",
                    "label": _("Branch Stock"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Simple Stock Balance",
                    "label": _("Simple Stock Balance"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Payment Summary",
                    "label": _("Payment Summary"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Sales Summary by Product",
                    "label": _("Sales Summary by Product"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Item Sell Out History",
                    "label": _("Item Sell Out History"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Customer-wise Invoice",
                    "label": _("Customer-wise Invoice"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Loyalty Card Activation",
                    "label": _("Loyalty Card Activation"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Loyalty Point Ledger",
                    "label": _("Loyalty Point Ledger"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Customer Loyalty Point",
                    "label": _("Customer Loyalty Point"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Loyalty Point Expiry",
                    "label": _("Loyalty Point Expiry"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Stock Ledger 2",
                    "label": _("Stock Ledger 2"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Stock Movement Analysis",
                    "label": _("Stock Movement Analysis"),
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Salary Report for Bank",
                    "label": _("Salary Report for Bank"),
                },
            ],
        },
        {
            "label": _("Setup"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Brand Category",
                    "label": _("Brand Category"),
                },
                {
                    "type": "doctype",
                    "name": "Group Discount",
                    "label": _("Group Discount"),
                },
                {"type": "doctype", "name": "Gift Card", "label": _("Gift Card")},
                {
                    "type": "doctype",
                    "name": "Cashback Program",
                    "label": _("Cashback Program"),
                },
                {"type": "doctype", "name": "Optical Lab", "label": _("Optical Lab")},
                {
                    "type": "doctype",
                    "name": "Optical Store Settings",
                    "label": _("Optical Store Settings"),
                },
                {
                    "type": "doctype",
                    "name": "Optical Store Selling Settings",
                    "label": _("Optical Store Selling Settings"),
                },
                {
                    "type": "doctype",
                    "name": "Optical Store HR Settings",
                    "label": _("Optical Store HR Settings"),
                },
                {"type": "doctype", "name": "Email Alerts", "label": _("Email Alerts")},
            ],
        },
    ]
