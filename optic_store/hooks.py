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
                    "Branch-branch_code",
                    "Branch-location",
                    "Branch-main_col",
                    "Branch-warehouse",
                    "Customer-branch",
                    "Item Group-item_group_abbr",
                    "Item-manual_item_code",
                    "Item-gift_card_sec",
                    "Item-is_gift_card",
                    "Item-gift_card_col",
                    "Item-gift_card_value",
                    "Item-gift_card_validity",
                    "Brand-brand_category",
                    "Sales Order-os_order_type",
                    "Sales Order-os_branch",
                    "Sales Order-os_is_special_order",
                    "Sales Order-os_is_same_branch",
                    "Sales Order-os_sales_person",
                    "Sales Order-orx_sec",
                    "Sales Order-orx_type",
                    "Sales Order-orx_col",
                    "Sales Order-orx_name",
                    "Sales Order-orx_html_sec",
                    "Sales Order-orx_html",
                    "Sales Order-os_others_sec",
                    "Sales Order-orx_frame_size",
                    "Sales Order-orx_height_type",
                    "Sales Order-orx_height",
                    "Sales Order-os_others_col",
                    "Sales Order-orx_dispensor",
                    "Sales Order-orx_lab",
                    "Sales Order-orx_group_discount",
                    "Sales Order-os_recall_sec",
                    "Sales Order-os_recall",
                    "Sales Order-os_recall_months",
                    "Sales Order-os_recall_col",
                    "Sales Order-os_recall_reason",
                    "Sales Invoice-os_gift_card_sec",
                    "Sales Invoice-os_gift_card_entry",
                    "Sales Invoice-os_gift_cards",
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
# page_js = {"page" : "public/js/file.js"}

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
        "on_update": "optic_store.doc_events.sales_order.on_update",
    },
    "Customer": {"before_insert": "optic_store.doc_events.customer.before_insert"},
    "Item": {
        "before_naming": "optic_store.doc_events.item.before_naming",
        "autoname": "optic_store.doc_events.item.autoname",
        "validate": "optic_store.doc_events.item.validate",
        "before_save": "optic_store.doc_events.item.before_save",
    },
    "Serial No": {
        "after_insert": "optic_store.doc_events.serial_no.after_insert",
        "on_trash": "optic_store.doc_events.serial_no.on_trash",
    },
    "Sales Invoice": {
        "validate": "optic_store.doc_events.sales_invoice.validate",
        "before_submit": "optic_store.doc_events.sales_invoice.before_submit",
        "on_submit": "optic_store.doc_events.sales_invoice.on_submit",
        "on_cancel": "optic_store.doc_events.sales_invoice.on_cancel",
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
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "optic_store.event.get_events"
# }
