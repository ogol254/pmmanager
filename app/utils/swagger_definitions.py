swagger_definitions = {
    'UserModel': {
        'type': 'object',
        'properties': {
            'id': {'type': 'string', 'example': '7b2f5e5e-6c0a-4f9b-8c7e-123456789abc'},
            'customer_id': {'type': 'string', 'example': 'c1a2b3c4-d5e6-7f89-0abc-123456789def'},
            'email': {'type': 'string', 'example': 'user@example.com'},
            'name': {'type': 'string', 'example': 'Jane Doe'},
            'role': {'type': 'string', 'enum': ['admin', 'manager', 'user', 'viewer'], 'example': 'user'},
            'status': {'type': 'string', 'enum': ['active', 'pending', 'suspended'], 'example': 'active'},
            'invitation_token': {'type': 'string', 'example': 'invite-xyz'},
            'last_login_at': {'type': 'string', 'format': 'date-time', 'example': '2025-04-27T22:00:00Z'},
            'created_at': {'type': 'string', 'format': 'date-time', 'example': '2025-04-27T21:00:00Z'},
            'updated_at': {'type': 'string', 'format': 'date-time', 'example': '2025-04-27T22:00:00Z'},
            'password': {'type': 'string', 'writeOnly': True, 'example': 'secret123'}
        },
        'required': ['email', 'name', 'password', 'role']
    },
    'Login': {
        'type': 'object',
        'properties': {
            'email': {'type': 'string', 'example': 'superadmin@example.com'},
            'password': {'type': 'string', 'example': 'secret123'}
        },
        'required': ['email', 'password']
    }
}
