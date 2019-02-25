# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from optics_9t9it.api.customer import get_user_branch


def before_save(doc, method):
    if doc.is_new() and not doc.branch:
        doc.branch = get_user_branch()
