// Copyright (c) 2016, 9T9IT and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Advanced Sales Report"] = {
	filters: [
		{
		  fieldname: 'from_date',
		  label: __('From Date'),
		  fieldtype: 'Date',
		  reqd: 1,
		  default: frappe.datetime.get_today(),
		},
		{
		  fieldname: 'to_date',
		  label: __('To Date'),
		  fieldtype: 'Date',
		  reqd: 1,
		  default: frappe.datetime.get_today(),
		},
	  ],
}
