# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.utils import today

from optic_store.api.customer import get_user_branch


def before_insert(doc, method):
    if not doc.branch:
        doc.branch = get_user_branch()

    doc.os_permit_sms = 1
    doc.os_permit_email = 1


def before_save(doc, method):
    if not doc.os_loyalty_activation_date:
        if doc.loyalty_program:
            old_doc = doc.get_doc_before_save()
            if old_doc and not old_doc.loyalty_program:
                doc.os_loyalty_activation_date = today()
