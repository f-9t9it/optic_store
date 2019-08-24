# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from toolz import get, merge


def process(doc, method):
    sms_template = frappe.db.exists(
        "SMS Template",
        {"disabled": 0, "ref_doctype": doc.doctype, "event": method, "auto_trigger": 1},
    )
    if not sms_template:
        return

    template = frappe.get_doc("SMS Template", sms_template)

    if not _allowed(template.condition, doc):
        return

    try:
        number = _get_number(template.num_field, doc)
        text = _get_content(template.content, doc)

        # fix for json.loads casting to int during number validation
        send_sms('"{}"'.format(number), text)

        if template.save_com:
            _make_communication(
                {
                    "subject": "SMS: {} to {}".format(template.template_name, number),
                    "reference_doctype": doc.doctype,
                    "reference_name": doc.name,
                    "phone_no": number,
                    "content": text,
                }
            )
    except Exception:
        frappe.log_error(frappe.get_traceback())


def _allowed(condition, doc):
    if not condition:
        return True
    return frappe.safe_eval(
        condition,
        eval_globals=dict(
            frappe=frappe._dict(
                db=frappe._dict(
                    get_value=frappe.db.get_value, get_list=frappe.db.get_list
                ),
                session=frappe.session,
            )
        ),
        eval_locals=doc.as_dict(),
    )


def _get_number(field, doc):
    if "." not in field:
        return get(field, doc.as_dict())

    link_field, source_fieldname = field.split(".", 1)
    meta = frappe.get_meta(doc.doctype)
    link_df = meta.get_field(link_field)
    return frappe.db.get_value(
        link_df.options, get(link_field, doc.as_dict()), source_fieldname
    )


def _get_content(template, doc):
    return frappe.render_template(template, doc.as_dict())


def _make_communication(args):
    return frappe.get_doc(
        merge(
            {
                "doctype": "Communication",
                "communication_type": "Communication",
                "communication_medium": "SMS",
            },
            args,
        )
    ).insert()
