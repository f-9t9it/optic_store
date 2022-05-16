# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from itertools import groupby
from operator import itemgetter
import json

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
			{ "fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 100 }, #ok
			{ "fieldname": "reg_no","label": _("Reg No"),"fieldtype": "Data", "width": 80 },
			{ "fieldname": "patient", "label": _("Patient Name"), "fieldtype": "Link", "options" : "Customer", "width": 100 }, #ok
			{ "fieldname": "inv_no", "label": _("Invoice No"), "fieldtype": "Link", "options":"Sales Invoice", "width": 120 },
			{ "fieldname": "gross", "label": _("Gross"), "fieldtype": "Float", "Precision" :3, "width": 80 }, #
			{ "fieldname": "serv_discount", "label": _("Serv Disc"), "fieldtype": "Float", "Precision" :3, "width": 80 },
			{ "fieldname": "net", "label": _("Net"), "fieldtype": "Float", "Precision" :3, "width": 80 }, #ok
			{ "fieldname": "receipts", "label": _("Receipts"), "fieldtype": "Link", "options":"Payment Entry", "width": 120 },
			{ "fieldname": "vat", "label": _("VAT"), "fieldtype": "Float", "Precision" :3,"width": 80 }, #ok
			{ "fieldname": "total", "label": _("Total"), "fieldtype": "Float", "Precision" :3, "width": 100 }, #ok
			{ "fieldname": "no_mop", "label": _("NO MOP"), "fieldtype": "Float", "Precision" :3, "width": 80 }
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

def get_data(filters):
	sinv_data = get_sinv(filters)
	if sinv_data:
		payments = get_payments(sinv_data)
		merged_data = merge_inv_payment(sinv_data, payments)
		return merged_data

def merge_inv_payment(sinv_data, payments):

	mop_list = frappe.db.sql(""" select REPLACE( LOWER(name), ' ', '_') as name from `tabMode of Payment` """, as_dict = 1)
	mops = [mop['name'] for mop in mop_list]

	combined_list = sinv_data + payments
	sorted_list = sorted(combined_list, key = lambda i: i['inv_no'])
	merged_list = []
	for key, value in groupby(sorted_list, key = lambda i: i['inv_no']):
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

def get_sinv(filters): 
	sinv_data = frappe.db.sql("""
								SELECT
									sinv.posting_date as date,
									sinv.name as inv_no,
									sinv.customer as patient,
									user_name.full_name as user,
									sinv.os_policy_name AS ins,
									sinv.os_policy_no AS insurer,
									sinv.total as net,
									IFNULL(sinv.discount_amount, ((sinv.additional_discount_percentage / 100 ) * sinv.grand_total) ) as serv_discount,
									(( sinv.total )  - IFNULL(sinv.discount_amount, ((sinv.additional_discount_percentage / 100 ) * sinv.grand_total) ) )as gross,
									sinv.total_taxes_and_charges as vat,
									sinv.grand_total as total,
									IFNULL(sinv.outstanding_amount,0) as receivable,
									(
										SELECT group_concat(parent)
										FROM  `tabPayment Entry Reference` pr
										WHERE pr.reference_name = sinv.name
										AND pr.docstatus = 1) AS receipts
								FROM
									`tabSales Invoice` sinv
								LEFT JOIN
									`tabUser` user_name ON user_name.email = sinv.owner
								WHERE
									sinv.posting_date BETWEEN '%(from)s' AND '%(to)s'
									AND sinv.docstatus = 1
							"""%{"from" : filters['from_date'], "to" : filters['to_date']}, as_dict = 1)

	return sinv_data

def get_payments(sinv_data):
	inv_list = tuple((inv.inv_no) for inv in sinv_data)
	sip = frappe.db.sql("""SELECT
							sip.parent as inv_no,
							REPLACE(LOWER(sip.mode_of_payment), ' ', '_') AS mop,
							sip.base_amount AS paid_amount
						FROM
							`tabSales Invoice Payment` AS sip
						WHERE
							sip.parenttype = 'Sales Invoice' AND parent IN %(inv_list)s
						"""%{"inv_list": inv_list}, as_dict =1)
	pe = frappe.db.sql("""SELECT
							per.reference_name as inv_no,
							per.allocated_amount as paid_amount,
							REPLACE( LOWER(IFNULL(pe.mode_of_payment,"NO MOP")), ' ', '_') as mop
						FROM
							`tabPayment Entry Reference` per
						LEFT JOIN
							`tabPayment Entry` pe ON pe.name = per.parent
						WHERE
							per.reference_name IN %(inv_list)s AND
							pe.docstatus = 1
						"""%{"inv_list": inv_list}, as_dict =1)

	payments = pe + sip

	grouper = itemgetter("inv_no", "mop")
	result = []

	# for key, grp in groupby(sorted(payments, key = grouper), grouper):
	# 	temp_dict = dict(zip(["inv_no", "mop"], key))
	# 	temp_dict["paid_amount"] = sum(item["paid_amount"] for item in grp)
	# 	item_dict = {
	# 		"inv_no" : temp_dict['inv_no'],
	# 		temp_dict['mop'] : temp_dict['paid_amount']
	# 	}
	# 	result.append(item_dict)

	# return result
	for key, grp in groupby(sorted(payments, key = grouper), grouper):
		temp_dict = dict(zip(["inv_no", "mop"], key))
		temp_dict["paid_amount"] = sum(item["paid_amount"] for item in grp)
		item_dict = {"inv_no" : temp_dict['inv_no'],temp_dict['mop'] : temp_dict['paid_amount']}
		result.append(item_dict)

	return result