# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__

app_name = "optic_store"
app_version = __version__
app_title = "Optic Store"
app_publisher = "9T9IT"
app_description = "ERPNext App for Optical Store"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@9t9it.com"
app_license = "MIT"

error_report_email = "support@9t9it.com"

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Employee-os_fathers_name",
                    "Employee-os_nationality",
                    "Employee-os_licenses_sec",
                    "Employee-os_cpr_no",
                    "Employee-os_cpr_expiry",
                    "Employee-os_rp_no",
                    "Employee-os_rp_expiry",
                    "Employee-os_nhra_license",
                    "Employee-os_nhra_expiry",
                    "Employee-os_licenses_col",
                    "Employee-os_sponsor_name",
                    "Employee-os_sponsor_cr",
                    "Employee-os_contract_date",
                    "Employee-os_eo_joining_date",
                    "Employee-os_lmra_joining_date",
                    "Branch-disabled",
                    "Branch-process_at_branch",
                    "Branch-main_col",
                    "Branch-branch_code",
                    "Branch-os_sales_sec",
                    "Branch-os_sales_order_naming_series",
                    "Branch-os_sales_invoice_naming_series",
                    "Branch-os_sales_col",
                    "Branch-os_cost_center",
                    "Branch-os_details_sec",
                    "Branch-warehouse",
                    "Branch-location",
                    "Branch-branch_phone",
                    "Branch-os_email",
                    "Branch-os_details_col",
                    "Branch-os_nhra_license",
                    "Branch-os_nhra_expiry",
                    "Branch-os_cr_no",
                    "Branch-os_cr_expiry",
                    "Customer-os_unverified_loyalty_card_no",
                    "Customer-branch",
                    "Customer-os_details_sec",
                    "Customer-os_detail_bio_col",
                    "Customer-os_short_name",
                    "Customer-os_crp_no",
                    "Customer-os_date_of_birth",
                    "Customer-os_occupation",
                    "Customer-os_nationality",
                    "Customer-os_permit_sms",
                    "Customer-os_permit_email",
                    "Customer-os_detail_contact_col",
                    "Customer-os_office_number",
                    "Customer-os_mobile_number",
                    "Customer-os_home_number",
                    "Customer-os_other_number",
                    "Customer-os_email",
                    "Customer-os_address",
                    "Customer-os_loyalty_col",
                    "Customer-os_loyalty_card_no",
                    "Item Group-item_group_abbr",
                    "Item-manual_item_code",
                    "Item-os_prices_sec",
                    "Item-os_minimum_selling_rate",
                    "Item-os_minimum_selling_2_rate",
                    "Item-os_wholesale_rate",
                    "Item-os_prices_col",
                    "Item-os_cost_price",
                    "Item-gift_card_sec",
                    "Item-is_gift_card",
                    "Item-gift_card_col",
                    "Item-gift_card_value",
                    "Item-gift_card_validity",
                    "Item-os_commission_sec",
                    "Item-os_has_commission",
                    "Item-os_commission_by",
                    "Item-os_commission_table_sec",
                    "Item-os_commissions",
                    "Item-os_more_info_sec",
                    "Item-os_color",
                    "Item-os_model",
                    "Item-os_size",
                    "Item-os_life_span",
                    "Item-os_more_info_col",
                    "Item-os_promotional_discount",
                    "Item-os_promotion_start_date",
                    "Item-os_promotion_end_date",
                    "Brand-brand_category",
                    "Sales Order-os_order_type",
                    "Sales Order-os_branch",
                    "Sales Order-os_is_branch_order",
                    "Sales Order-os_is_special_order",
                    "Sales Order-os_sales_person",
                    "Sales Order-orx_sec",
                    "Sales Order-orx_type",
                    "Sales Order-orx_col",
                    "Sales Order-orx_name",
                    "Sales Order-orx_html_sec",
                    "Sales Order-orx_html",
                    "Sales Order-os_others_sec",
                    "Sales Order-os_type_of_spectacle",
                    "Sales Order-orx_frame_size",
                    "Sales Order-orx_height_type",
                    "Sales Order-orx_height",
                    "Sales Order-os_others_col",
                    "Sales Order-orx_dispensor",
                    "Sales Order-orx_lab",
                    "Sales Order-os_lab_tech",
                    "Sales Order-orx_group_discount",
                    "Sales Order-os_gift_card_sec",
                    "Sales Order-os_gift_card_entry",
                    "Sales Order-os_gift_cards",
                    "Sales Order-os_recall_sec",
                    "Sales Order-os_recall",
                    "Sales Order-os_recall_months",
                    "Sales Order-os_recall_col",
                    "Sales Order-os_recall_reason",
                    "Sales Order Item-os_price_list_col",
                    "Sales Order Item-os_minimum_selling_rate",
                    "Sales Order Item-os_minimum_selling_2_rate",
                    "Sales Invoice-os_gift_card_sec",
                    "Sales Invoice-os_gift_card_entry",
                    "Sales Invoice-os_gift_cards",
                    "Sales Invoice-os_branch",
                    "Sales Invoice-os_sales_person",
                    "Sales Invoice-orx_sec",
                    "Sales Invoice-orx_type",
                    "Sales Invoice-orx_col",
                    "Sales Invoice-orx_name",
                    "Sales Invoice-orx_html_sec",
                    "Sales Invoice-orx_html",
                    "Sales Invoice-os_others_sec",
                    "Sales Invoice-os_type_of_spectacle",
                    "Sales Invoice-orx_frame_size",
                    "Sales Invoice-orx_height_type",
                    "Sales Invoice-orx_height",
                    "Sales Invoice-os_others_col",
                    "Sales Invoice-orx_dispensor",
                    "Sales Invoice-orx_lab",
                    "Sales Invoice-os_lab_tech",
                    "Sales Invoice-os_loyalty_card_no",
                    "Sales Invoice-orx_group_discount",
                    "Sales Invoice-os_recall_sec",
                    "Sales Invoice-os_recall",
                    "Sales Invoice-os_recall_months",
                    "Sales Invoice-os_recall_col",
                    "Sales Invoice-os_recall_reason",
                    "Sales Invoice Item-os_minimum_selling_rate",
                    "Sales Invoice Item-os_minimum_selling_2_rate",
                    "Delivery Note-os_branch",
                    "Payment Entry-os_gift_card",
                ],
            ]
        ],
    },
    {
        "doctype": "Property Setter",
        "filters": [
            [
                "name",
                "in",
                [
                    "Customer-naming_series-options",
                    "Customer-search_fields",
                    "Item-quick_entry",
                    "Item-naming_series-options",
                    "Sales Order-order_type-hidden",
                    "Sales Order-set_warehouse-read_only",
                    "Sales Order-po_no-hidden",
                    "Sales Order-terms_section_break-hidden",
                    "Sales Order-more_info-hidden",
                    "Sales Order-printing_details-hidden",
                    "Sales Order-section_break_78-hidden",
                    "Sales Order-sales_team_section_break-hidden",
                    "Sales Order-section_break1-hidden",
                    "Sales Order-subscription_section-hidden",
                    "Sales Invoice Item-cost_center-default",
                    "Delivery Note Item-cost_center-default",
                ],
            ]
        ],
    },
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/optic_store/css/optic_store.css"
app_include_js = "/assets/js/optic_store.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/optic_store/css/optic_store.css"
# web_include_js = "/assets/optic_store/js/optic_store.js"

# include js in page
page_js = {"pos": "public/js/pos.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "optic_store.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "optic_store.install.before_install"
# after_install = "optic_store.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "optic_store.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Delivery Note": {"validate": "optic_store.doc_events.delivery_note.validate"},
    "Sales Order": {
        "validate": "optic_store.doc_events.sales_order.validate",
        "before_insert": "optic_store.doc_events.sales_order.before_insert",
        "on_update": "optic_store.doc_events.sales_order.on_update",
    },
    "Customer": {"before_insert": "optic_store.doc_events.customer.before_insert"},
    "Item": {
        "before_naming": "optic_store.doc_events.item.before_naming",
        "autoname": "optic_store.doc_events.item.autoname",
        "validate": "optic_store.doc_events.item.validate",
        "after_insert": "optic_store.doc_events.item.after_insert",
        "before_save": "optic_store.doc_events.item.before_save",
    },
    "Serial No": {
        "after_insert": "optic_store.doc_events.serial_no.after_insert",
        "on_trash": "optic_store.doc_events.serial_no.on_trash",
    },
    "Sales Invoice": {
        "validate": "optic_store.doc_events.sales_invoice.validate",
        "before_insert": "optic_store.doc_events.sales_invoice.before_insert",
        "before_submit": "optic_store.doc_events.sales_invoice.before_submit",
        "on_submit": "optic_store.doc_events.sales_invoice.on_submit",
        "on_cancel": "optic_store.doc_events.sales_invoice.on_cancel",
    },
    "Payment Entry": {
        "validate": "optic_store.doc_events.payment_entry.validate",
        "on_submit": "optic_store.doc_events.payment_entry.on_submit",
        "on_cancel": "optic_store.doc_events.payment_entry.on_cancel",
    },
    "Journal Entry": {"on_cancel": "optic_store.doc_events.journal_entry.on_cancel"},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "all": ["optic_store.tasks.all"],
    "daily": ["optic_store.api.gift_card.write_off_expired_gift_cards"],
    # "hourly": ["optic_store.tasks.hourly"],
    # "weekly": ["optic_store.tasks.weekly"],
    # "monthly": ["optic_store.tasks.monthly"],
}

# Testing
# -------

before_tests = "optic_store.api.install.setup_defaults"

# Overriding Whitelisted Methods
# ------------------------------

override_whitelisted_methods = {
    "erpnext.accounts.doctype.sales_invoice.pos.get_pos_data": "optic_store.api.pos.get_pos_data",
    "erpnext.accounts.doctype.sales_invoice.pos.make_invoice": "optic_store.api.pos.make_invoice",
    "erpnext.selling.page.point_of_sale.point_of_sale.search_serial_or_batch_or_barcode_number": "optic_store.api.sales_invoice.search_serial_or_batch_or_barcode_number",
}
