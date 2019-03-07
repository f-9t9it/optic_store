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
                    "Customer-branch",
                    "Item Group-item_group_abbr",
                    "Item-manual_item_code",
                    "Sales Order-orx_sec",
                    "Sales Order-orx_type",
                    "Sales Order-orx_col",
                    "Sales Order-orx_name",
                    "Sales Order-orx_html_sec",
                    "Sales Order-orx_html",
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
                    "Sales Order-orx_sec",
                    "Sales Order-orx_type",
                    "Sales Order-orx_col",
                    "Sales Order-orx_name",
                    "Sales Order-orx_html_sec",
                    "Sales Order-orx_html",
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
    "Sales Order": {"validate": "optic_store.doc_events.sales_order.validate"},
    "Customer": {"before_naming": "optic_store.doc_events.customer.before_naming"},
    "Item": {
        "before_naming": "optic_store.doc_events.item.before_naming",
        "autoname": "optic_store.doc_events.item.autoname",
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"optic_store.tasks.all"
# 	],
# 	"daily": [
# 		"optic_store.tasks.daily"
# 	],
# 	"hourly": [
# 		"optic_store.tasks.hourly"
# 	],
# 	"weekly": [
# 		"optic_store.tasks.weekly"
# 	]
# 	"monthly": [
# 		"optic_store.tasks.monthly"
# 	]
# }

# Testing
# -------

before_tests = "optic_store.api.install.setup_defaults"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "optic_store.event.get_events"
# }
