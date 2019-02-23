# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__

app_name = "9t9it_optics"
app_version = __version__
app_title = "Optics 9T9IT"
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
                    "Sales Order-orx_sec",
                    "Sales Order-orx_type",
                    "Sales Order-orx_col",
                    "Sales Order-orx_name",
                    "Sales Order-orx_html_sec",
                    "Sales Order-orx_html",
                ],
            ]
        ],
    }
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/9t9it_optics/css/9t9it_optics.css"
# app_include_js = "/assets/9t9it_optics/js/9t9it_optics.js"

# include js, css files in header of web template
# web_include_css = "/assets/9t9it_optics/css/9t9it_optics.css"
# web_include_js = "/assets/9t9it_optics/js/9t9it_optics.js"

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
# get_website_user_home_page = "9t9it_optics.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "9t9it_optics.install.before_install"
# after_install = "9t9it_optics.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "9t9it_optics.notifications.get_notification_config"

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

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"9t9it_optics.tasks.all"
# 	],
# 	"daily": [
# 		"9t9it_optics.tasks.daily"
# 	],
# 	"hourly": [
# 		"9t9it_optics.tasks.hourly"
# 	],
# 	"weekly": [
# 		"9t9it_optics.tasks.weekly"
# 	]
# 	"monthly": [
# 		"9t9it_optics.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "9t9it_optics.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "9t9it_optics.event.get_events"
# }
