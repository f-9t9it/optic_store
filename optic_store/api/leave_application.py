import frappe
from toolz import pluck


def get_salary_component_by_type(type, components):
    if type in ["type_1", "type_2"]:
        allowed_components = frappe.get_all(
            "Optical Store HR Settings Salary Component",
            filters={"parentfield": "{}_components".format(type)},
            fields="salary_component",
        )
        return [
            x
            for x in components
            if x.salary_component in pluck("salary_component", allowed_components)
        ]
    return []


def get_leave_balance(employee, date):
    from erpnext.hr.doctype.leave_application.leave_application import (
        get_leave_balance_on,
    )

    carryable_leaves = frappe.get_all("Leave Type", {"is_carry_forward": 1})
    return sum(
        [
            get_leave_balance_on(employee, leave_type, date)
            for leave_type in pluck("name", carryable_leaves)
        ]
    )
