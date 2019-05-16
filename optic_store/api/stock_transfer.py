workflow = {
    "name": "Optic Store Stock Transfer",
    "document_type": "Stock Transfer",
    "is_active": 1,
    "send_email_alert": 0,
    "workflow_state_field": "workflow_state",
    "states": [
        {
            "state": "Draft",
            "style": "Danger",
            "doc_status": "0",
            "allow_edit": "Stock User",
        },
        {
            "state": "In Transit",
            "style": "Warning",
            "doc_status": "1",
            "allow_edit": "Stock User",
        },
        {
            "state": "Received",
            "style": "Success",
            "doc_status": "1",
            "allow_edit": "Stock User",
        },
        {
            "state": "Cancelled",
            "style": "Danger",
            "doc_status": "2",
            "allow_edit": "Stock User",
        },
    ],
    "transitions": [
        {
            "state": "Draft",
            "action": "Dispatch",
            "next_state": "In Transit",
            "allowed": "Stock User",
            "allow_self_approval": 1,
            "condition": "frappe.db.get_value('Has Role', filters={'role': 'System Manager', 'parent': frappe.session.user }) or doc.owner == frappe.session.user",  # noqa
        },
        {
            "state": "In Transit",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "Stock User",
            "allow_self_approval": 1,
            "condition": "frappe.db.get_value('Has Role', filters={'role': 'System Manager', 'parent': frappe.session.user }) or doc.owner == frappe.session.user",  # noqa
        },
        {
            "state": "In Transit",
            "action": "Receive",
            "next_state": "Received",
            "allowed": "Sales User",
            "allow_self_approval": 1,
            "condition": "frappe.db.get_value('Has Role', filters={'role': 'System Manager', 'parent': frappe.session.user }) or frappe.session.user == frappe.db.get_value('Branch', doc.target_branch, 'os_user') or frappe.db.get_value('Employee', filters={'user_id': frappe.session.user}, fieldname='branch')",  # noqa
        },
    ],
}
