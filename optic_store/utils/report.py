from frappe import _


def make_column(key, label=None, type="Data", options=None, width=90):
    return {
        "label": _(label or key.replace("_", " ").title()),
        "fieldname": key,
        "fieldtype": type,
        "options": options,
        "width": width,
    }
