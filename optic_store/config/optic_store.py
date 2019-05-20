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
                }
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
                {"type": "doctype", "name": "Optical Lab", "label": _("Optical Lab")},
                {
                    "type": "doctype",
                    "name": "Optical Store Settings",
                    "label": _("Optical Store Settings"),
                },
            ],
        },
    ]
