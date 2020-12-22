# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "module_name": "Optic Store",
            "category": "Modules",
            "label": _("Optic Store"),
            "color": "grey",
            "icon": "octicon octicon-file-directory",
            "type": "module",
            "link": "#point-of-sale",
        },
        {
            "module_name": "Point of Sale",
            "category": "Modules",
            "label": _("Point of Sale"),
            "color": "#FF4136",
            "icon": "fa fa-shopping-cart",
            "type": "link",
            "standard": 1,
            "link": "#point-of-sale",
            "onboard_present": 1
        },
        {
            "module_name": "XZ Report",
            "category": "Modules",
            "label": _("XZ Report"),
            "color": "#FF4136",
            "icon": "fa fa-tasks",
            "type": "link",
            "standard": 1,
            "link": "#List/XZ Report",
            "onboard_present": 1
        }
    ]
