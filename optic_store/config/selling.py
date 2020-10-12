# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("SMS"),
            "items": [
                {"type": "doctype", "name": "SMS Template", "label": _("SMS Template")}
            ],
        }
    ]
