from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from functools import partial
from toolz import compose, pluck, merge, concatv
from frappe import _
from itertools import groupby
from operator import itemgetter
import json
from optic_store.utils import pick, split_to_list
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    # data = sorted(data, key=lambda k: k['posting_date'])
    return columns, data


def _get_columns():
    columns = [
        make_column("posting_date", "Payment Date", type="Date", width=90),
        # make_column("posting_time", "Payment Time", type="Time", width=90),
        make_column("customer", type="Link", options="Customer",width=80),
        make_column("customer_name", width=150),
        make_column("voucher_type",width=80),
        make_column("voucher_no", type="Dynamic Link", options="voucher_type"),
        make_column("gross", "Gross", type="Currency",width=80),
        make_column("serv_discount", "Ser Disc", type="Currency",width=80),
        make_column("net", "Net", type="Currency",width=80),
        make_column("paid_amount", "Paid Amt", type="Currency",width=80),
        make_column("receipt_amount", "Receipt Amt", type="Currency",width=80),
        make_column("vat","VAT", type="Currency",width=60),
        make_column("total","Total", type="Currency",width=80),
        make_column("branch", type="Link", options="Branch",width=100),
        make_column("no_mop",label=_("NO MOP"), type="Currency", width=70),
        # make_column("sales_person", type="Link", options="Employee"),
        # make_column("sales_person_name", width=150),
    ]
    mop_list = frappe.db.sql(""" select name from `tabMode of Payment` order by name""", as_dict = 1)

    for mop in mop_list:
        name_field = mop['name'].replace(" ", "_").lower()
        columns.append({"fieldname": name_field, "label": _(mop['name']), "fieldtype": "Float", "precision":3, "width": 80})

    columns.append({ "fieldname": "receivable","label": _("Receivable"),"fieldtype": "Float", "Precision" :3, "width": 100 })
    columns.append({ "fieldname": "ins","label": _("Ins"),"fieldtype": "Data", "width": 100 })
    columns.append({ "fieldname": "insurer","label": _("Insurer"),"fieldtype": "Data", "width": 100 })
    columns.append({ "fieldname": "user","label": _("User"),"fieldtype": "Data", "width": 100 })
    return columns

def _get_filters(filters):
    modes_of_payment = split_to_list(filters.modes_of_payment)
    branches = split_to_list(filters.branches)
    si_clauses = concatv(
        ["si.docstatus = 1", "si.posting_date BETWEEN %(start_date)s AND %(end_date)s"],
        ["si.is_return = 0"] if cint(filters.hide_returns) else [],
        ["si.os_branch IN %(branches)s"] if branches else [],
        ["sip.mode_of_payment IN %(modes_of_payment)s"] if modes_of_payment else [],
    )
    pe_clauses = concatv(
        [
            "pe.docstatus = 1",
            "pe.party_type = 'Customer'",
            "pe.posting_date BETWEEN %(start_date)s AND %(end_date)s",
        ],
        ["pe.payment_type = 'Receive'"] if cint(filters.hide_returns) else [],
        ["pe.os_branch IN %(branches)s"] if branches else [],
        ["pe.mode_of_payment IN %(modes_of_payment)s"] if modes_of_payment else [],
    )
    values = merge(
        pick(["start_date", "end_date"], filters),
        {"branches": branches} if branches else {},
        {"modes_of_payment": modes_of_payment} if modes_of_payment else {},
    )
    return (
        {
            "si_clauses": " AND ".join(si_clauses),
            "pe_clauses": " AND ".join(pe_clauses),
        },
        values,
    )
def _get_data(clauses, values, keys):
    sinv_data = get_sinv(clauses, values, keys)
    if sinv_data:
        payments = get_payments(sinv_data)
        # merged_data = merge_inv_payment(sinv_data, payments)
        merged_data = sorted(merge_inv_payment(sinv_data, payments), key=lambda k: k['posting_date'])
        return merged_data
    
# def merge_inv_payment(sinv_data, payments):

# 	mop_list = frappe.db.sql(""" select REPLACE( LOWER(name), ' ', '_') as name from `tabMode of Payment` """, as_dict = 1)
# 	mops = [mop['name'] for mop in mop_list]

# 	combined_list = sinv_data + payments
# 	sorted_list = sorted(combined_list, key = lambda i: i['voucher_no'])
# 	merged_list = []
# 	for key, value in groupby(sorted_list, key = lambda i: i['voucher_no']):
# 		ls = list(value)
# 		result = {}
# 		for d in ls:
# 			result.update(d)
# 		merged_list.append(result)

# 	for key in mops:
# 		for inv in merged_list:
# 			if key not in inv:
# 				inv[key] = 0

# 	return merged_list


def get_sinv(clauses, values, keys):
    # UNION ALL for minor performance gain
    sinv_data = frappe.db.sql(
        """
            SELECT
                si.posting_date AS posting_date,
                si.posting_time AS posting_time,
                'Sales Invoice' AS voucher_type,
                si.name AS voucher_no,
                sip.mode_of_payment AS mode_of_payment,
                si.paid_amount AS paid_amount,
                0 as receipt_amount,
                si.customer AS customer,
                si.customer_name AS customer_name,
                si.os_sales_person AS sales_person,
                si.os_sales_person_name AS sales_person_name,
                si.os_branch AS branch,
                ((si.total)-IFNULL(si.discount_amount, ((si.additional_discount_percentage/100 )*si.grand_total)))as gross,
                IFNULL(si.discount_amount,((si.additional_discount_percentage / 100 ) * si.grand_total) ) as serv_discount,
                si.total as net,
                si.total_taxes_and_charges as vat,
                si.grand_total as total,
                IFNULL(si.outstanding_amount,0) as receivable,
                si.os_policy_name AS ins,
				si.os_policy_no AS insurer,
                user_name.full_name as user
            FROM `tabSales Invoice` AS si
            RIGHT JOIN `tabSales Invoice Payment` AS sip ON sip.parent = si.name
            LEFT JOIN`tabUser` user_name ON user_name.email = si.owner
            WHERE {si_clauses} 
            UNION ALL
            SELECT
                pe.posting_date AS posting_date,
                pe.os_posting_time AS posting_time,
                'Payment Entry' AS voucher_type,
                pe.name AS voucher_no,
                pe.mode_of_payment AS mode_of_payment,
                0 AS paid_amount,
                pe.paid_amount AS receipt_amount,
                pe.party AS customer,
                pe.party_name AS customer_name,
                per.sales_person AS sales_person,
                per.sales_person_name AS sales_person_name,
                pe.os_branch AS branch,
                0 as net,
                0 as serv_discount,
                0 as gross,
                0 as vat,
                pe.paid_amount AS total,
                0 as receivable,
                "" AS ins,
				"" AS insurer,
                user_name.full_name as user
            FROM `tabPayment Entry` AS pe
            LEFT JOIN`tabUser` user_name ON user_name.email = pe.owner
            RIGHT JOIN (
                SELECT
                    rjper.parent AS parent,
                    rjsi.os_sales_person AS sales_person,
                    rjsi.os_sales_person_name AS sales_person_name,
                    rjper.total_amount,
                    rjper.outstanding_amount
                FROM `tabPayment Entry Reference` AS rjper
                LEFT JOIN `tabSales Invoice` AS rjsi ON rjsi.name = rjper.reference_name
                WHERE rjper.reference_doctype = 'Sales Invoice'
            ) AS per ON per.parent = pe.name
            WHERE {pe_clauses}
            ORDER BY posting_date
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    make_row = partial(pick, keys)
    return with_report_generation_time([make_row(x) for x in sinv_data], keys)
def merge_inv_payment(sinv_data, payments):

    mop_list = frappe.db.sql(""" select REPLACE( LOWER(name), ' ', '_') as name from `tabMode of Payment` """, as_dict = 1)
    mops = [mop['name'] for mop in mop_list]

    combined_list = sinv_data + payments
    sorted_list = sorted(combined_list, key = lambda i: i['voucher_no'])
    merged_list = []
    for key, value in groupby(sorted_list, key = lambda i: i['voucher_no']):
        ls = list(value)
        result = {}
        for d in ls:
            result.update(d)
        merged_list.append(result)

    for key in mops:
        for inv in merged_list:
            if key not in inv:
                inv[key] = 0

    return merged_list
def get_payments(sinv_data):
    inv_list = tuple((inv['voucher_no']) for inv in sinv_data)
    # inv_list = tuple((inv.voucher_no) for inv in sinv_data)
    # print(inv_list)
    sip = frappe.db.sql("""SELECT
                            sip.parent as voucher_no,
                            REPLACE(LOWER(sip.mode_of_payment), ' ', '_') AS mop,
                            sip.base_amount AS paid_amount
                        FROM
                            `tabSales Invoice Payment` AS sip
                        WHERE
                            sip.parenttype = 'Sales Invoice' AND parent IN %(inv_list)s
                        """%{"inv_list": inv_list}, as_dict =1)
    pe = frappe.db.sql("""SELECT per.parent as voucher_no,
                            per.reference_name as si_no,
                            per.allocated_amount as paid_amount,
                            REPLACE( LOWER(IFNULL(pe.mode_of_payment,"NO MOP")), ' ', '_') as mop
                        FROM
                            `tabPayment Entry Reference` per
                        LEFT JOIN
                            `tabPayment Entry` pe ON pe.name = per.parent
                        WHERE
                            per.parent IN %(inv_list)s AND
                            pe.docstatus = 1
                        """%{"inv_list": inv_list}, as_dict =1)

    payments = pe + sip
    # payments = pe + sip
    grouper = itemgetter("voucher_no", "mop")
    result = []

    for key, grp in groupby(sorted(payments, key = grouper), grouper):
        temp_dict = dict(zip(["voucher_no", "mop"], key))
        temp_dict["paid_amount"] = sum(item["paid_amount"] for item in grp)
        item_dict = {
            "voucher_no" : temp_dict['voucher_no'],
            temp_dict['mop'] : temp_dict['paid_amount']
        }
        result.append(item_dict)

    return result
    # for key, grp in groupby(sorted(payments, key = grouper), grouper):
    # 	temp_dict = dict(zip(["voucher_no", "mop"], key))
    # 	temp_dict["paid_amount"] = sum(item["paid_amount"] for item in grp)
    # 	item_dict = {"voucher_no" : temp_dict['voucher_no'],temp_dict['mop'] : temp_dict['paid_amount']}
    # 	result.append(item_dict)

    # return result