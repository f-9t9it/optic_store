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
                    "Branch-branch_code",
                    "Branch-disabled",
                    "Branch-os_main_col",
                    "Branch-os_user",
                    "Branch-os_sales_sec",
                    "Branch-os_sales_order_naming_series",
                    "Branch-os_sales_invoice_naming_series",
                    "Branch-os_sales_col",
                    "Branch-os_cost_center",
                    "Branch-os_target",
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
                    "Customer-old_customer_id",
                    "Customer-os_unverified_loyalty_card_no",
                    "Customer-branch",
                    "Customer-os_details_sec",
                    "Customer-os_detail_bio_col",
                    "Customer-os_short_name",
                    "Customer-os_cpr_no",
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
                    "Customer-os_loyalty_activation_date",
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
                    "Sales Order-os_item_type",
                    "Sales Order-os_insurance_sec",
                    "Sales Order-os_is_insurance",
                    "Sales Order-os_membership_no",
                    "Sales Order-os_insurance_col",
                    "Sales Order-os_policy_name",
                    "Sales Order-os_policy_no",
                    "Sales Order-os_approval_no",
                    "Sales Order-os_claim_form_no",
                    "Sales Order-os_sales_person",
                    "Sales Order-os_sales_person_name",
                    "Sales Order-orx_sec",
                    "Sales Order-orx_type",
                    "Sales Order-orx_col",
                    "Sales Order-orx_name",
                    "Sales Order-orx_html_sec",
                    "Sales Order-orx_html",
                    "Sales Order-os_orx_notes",
                    "Sales Order-os_others_sec",
                    "Sales Order-os_type_of_spectacle",
                    "Sales Order-orx_frame_size",
                    "Sales Order-orx_height_type",
                    "Sales Order-orx_height",
                    "Sales Order-os_notes",
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
                    "Sales Order Item-os_minimum_selling_rate",
                    "Sales Order Item-os_minimum_selling_2_rate",
                    "Sales Order Item-batch_no",
                    "Sales Order Item-os_spec_part",
                    "Sales Invoice-os_insurance_sec",
                    "Sales Invoice-os_is_insurance",
                    "Sales Invoice-os_membership_no",
                    "Sales Invoice-os_insurance_col",
                    "Sales Invoice-os_policy_name",
                    "Sales Invoice-os_policy_no",
                    "Sales Invoice-os_approval_no",
                    "Sales Invoice-os_claim_form_no",
                    "Sales Invoice-os_gift_card_sec",
                    "Sales Invoice-os_gift_card_entry",
                    "Sales Invoice-os_gift_cards",
                    "Sales Invoice-os_branch",
                    "Sales Invoice-os_sales_person",
                    "Sales Invoice-os_sales_person_name",
                    "Sales Invoice-orx_sec",
                    "Sales Invoice-orx_type",
                    "Sales Invoice-orx_col",
                    "Sales Invoice-orx_name",
                    "Sales Invoice-orx_html_sec",
                    "Sales Invoice-orx_html",
                    "Sales Invoice-os_orx_notes",
                    "Sales Invoice-os_others_sec",
                    "Sales Invoice-os_type_of_spectacle",
                    "Sales Invoice-orx_frame_size",
                    "Sales Invoice-orx_height_type",
                    "Sales Invoice-orx_height",
                    "Sales Invoice-os_notes",
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
                    "Sales Invoice Item-os_spec_part",
                    "Sales Invoice Payment-os_in_alt_tab",
                    "Delivery Note-os_branch",
                    "Purchase Receipt Item-os_expiry_date",
                    "Payment Entry-os_posting_time",
                    "Payment Entry-os_branch",
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
                    "Employee-emergency_phone_number-permlevel",
                    "Employee-salary_mode-permlevel",
                    "Employee-personal_email-permlevel",
                    "Employee-passport_number-permlevel",
                    "Employee-date_of_issue-permlevel",
                    "Employee-valid_upto-permlevel",
                    "Employee-place_of_issue-permlevel",
                    "Employee-blood_group-permlevel",
                    "Employee-family_background-permlevel",
                    "Employee-educational_qualification-permlevel",
                    "Employee-education-permlevel",
                    "Employee-previous_work_experience-permlevel",
                    "Employee-external_work_history-permlevel",
                    "Employee-exit-permlevel",
                    "Employee-resignation_letter_date-permlevel",
                    "Employee-relieving_date-permlevel",
                    "Employee-reason_for_leaving-permlevel",
                    "Employee-leave_encashed-permlevel",
                    "Employee-encashment_date-permlevel",
                    "Employee-exit_interview_details-permlevel",
                    "Employee-held_on-permlevel",
                    "Employee-reason_for_resignation-permlevel",
                    "Employee-new_workplace-permlevel",
                    "Employee-feedback-permlevel",
                    "Employee-lft-permlevel",
                    "Employee-rgt-permlevel",
                    "Employee-old_parent-permlevel",
                    "Customer-naming_series-options",
                    "Customer-search_fields",
                    "Item-quick_entry",
                    "Item-naming_series-options",
                    "Batch-search_fields",
                    "Batch-expiry_date-bold",
                    "Sales Order-naming_series-read_only",
                    "Sales Order-order_type-hidden",
                    "Sales Order-set_warehouse-read_only",
                    "Sales Order-po_no-hidden",
                    "Sales Order-more_info-hidden",
                    "Sales Order-printing_details-hidden",
                    "Sales Order-section_break_78-hidden",
                    "Sales Order-sales_team_section_break-hidden",
                    "Sales Order-section_break1-hidden",
                    "Sales Order-subscription_section-hidden",
                    "Sales Order Item-delivery_date-in_list_view",
                    "Sales Order Item-amount-columns",
                    "Sales Invoice-naming_series-read_only",
                    "Sales Invoice Item-cost_center-default",
                    "Sales Invoice Item-item_code-columns",
                    "Sales Invoice Item-qty-columns",
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
page_js = {"pos": "public/js/pos.js", "point-of-sale": "public/js/point_of_sale.js"}

# include js in doctype views
doctype_js = {
    "Stock Entry": "public/js/stock_entry.js",
    "Sales Order": "public/js/transaction_controller.js",
    "Sales Invoice": "public/js/transaction_controller.js",
    "Delivery Note": "public/js/transaction_controller.js",
}
doctype_list_js = {"Sales Invoice": "public/js/sales_invoice_list.js"}
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
    "Delivery Note": {
        "validate": "optic_store.doc_events.delivery_note.validate",
        "on_submit": "optic_store.doc_events.delivery_note.on_submit",
    },
    "Purchase Receipt": {
        "before_save": "optic_store.doc_events.purchase_receipt.before_validate",
        "on_submit": "optic_store.doc_events.purchase_receipt.set_batch_references",
    },
    "Sales Order": {
        "before_naming": "optic_store.doc_events.sales_order.before_naming",
        "validate": "optic_store.doc_events.sales_order.validate",
        "before_insert": "optic_store.doc_events.sales_order.before_insert",
        "before_save": "optic_store.doc_events.sales_order.before_save",
        "on_update": "optic_store.doc_events.sales_order.on_update",
        "before_cancel": "optic_store.doc_events.sales_order.before_cancel",
    },
    "Customer": {
        "before_insert": "optic_store.doc_events.customer.before_insert",
        "before_save": "optic_store.doc_events.customer.before_save",
    },
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
        "before_naming": "optic_store.doc_events.sales_invoice.before_naming",
        "validate": "optic_store.doc_events.sales_invoice.validate",
        "before_insert": "optic_store.doc_events.sales_invoice.before_insert",
        "before_save": "optic_store.doc_events.sales_invoice.before_save",
        "before_submit": "optic_store.doc_events.sales_invoice.before_submit",
        "on_submit": "optic_store.doc_events.sales_invoice.on_submit",
        "on_cancel": "optic_store.doc_events.sales_invoice.on_cancel",
    },
    "Payment Entry": {
        "validate": "optic_store.doc_events.payment_entry.validate",
        "before_insert": "optic_store.doc_events.payment_entry.before_insert",
        "before_save": "optic_store.doc_events.payment_entry.before_save",
        "on_submit": "optic_store.doc_events.payment_entry.on_submit",
        "on_cancel": "optic_store.doc_events.payment_entry.on_cancel",
    },
    "Journal Entry": {"on_cancel": "optic_store.doc_events.journal_entry.on_cancel"},
    "*": {
        "after_insert": "optic_store.api.sms.process",
        "on_update": "optic_store.api.sms.process",
        "on_submit": "optic_store.api.sms.process",
        "on_update_after_submit": "optic_store.api.sms.process",
        "on_cancel": "optic_store.api.sms.process",
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "all": ["optic_store.tasks.all"],
    "daily": [
        "optic_store.api.gift_card.write_off_expired_gift_cards",
        "optic_store.api.email_alerts.process",
    ],
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
    "erpnext.accounts.doctype.sales_invoice.pos.get_pos_data": "optic_store.api.pos.get_pos_data",  # noqa
    "erpnext.accounts.doctype.sales_invoice.pos.make_invoice": "optic_store.api.pos.make_invoice",  # noqa
    "erpnext.selling.page.point_of_sale.point_of_sale.search_serial_or_batch_or_barcode_number": "optic_store.api.sales_invoice.search_serial_or_batch_or_barcode_number",  # noqa
    "erpnext.selling.page.point_of_sale.point_of_sale.get_items": "optic_store.api.pos.get_items",  # noqa
    # TODO: when PR #18111 is merged
    "erpnext.accounts.doctype.loyalty_program.loyalty_program.get_loyalty_program_details": "optic_store.api.pos.get_loyalty_program_details",  # noqa
    "erpnext.stock.get_item_details.get_item_details": "optic_store.api.item.get_item_details",  # noqa
}

# Jinja Environment Customizations
# --------------------------------

jenv = {
    "methods": [
        "get_optical_items:optic_store.utils.helpers.get_optical_items",
        "get_amounts:optic_store.utils.helpers.get_amounts",
        "get_ref_so_date:optic_store.api.sales_invoice.get_ref_so_date",
        "get_payments:optic_store.api.sales_invoice.get_payments",
    ]
}
