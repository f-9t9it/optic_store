# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute():
    for property in [
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
    ]:
        frappe.delete_doc_if_exists("Property Setter", property)
