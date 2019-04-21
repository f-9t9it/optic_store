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
    ],
    "transitions": [
        {
            "state": "Draft",
            "action": "Dispatch",
            "next_state": "In Transit",
            "allowed": "Stock User",
            "allow_self_approval": 1,
        },
        {
            "state": "In Transit",
            "action": "Receive",
            "next_state": "Received",
            "allowed": "Sales User",
            "allow_self_approval": 1,
        },
    ],
}
