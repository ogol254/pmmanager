from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from functools import wraps

def validate_session_and_scope():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_id = get_jwt_identity()
            customer_id = claims.get('customer_id')
            role = claims.get('role')

            if not user_id or not role:
                return jsonify({'error': 'Unauthorized'}), 401

            # Superadmins can see/manage everything
            if role in ("superadmin", "superadmin_readonly"):
                return fn(*args, **kwargs)

            if not customer_id:
                return jsonify({'error': 'Customer context required'}), 401

            # Check for explicit customer_id in body or params
            if request.method in ['POST', 'PUT', 'PATCH']:
                if request.is_json:
                    body = request.get_json(silent=True) or {}
                    if 'customer_id' in body and body['customer_id'] != customer_id:
                        return jsonify({'error': 'Cross-customer access forbidden'}), 403
            if 'customer_id' in kwargs and kwargs['customer_id'] != customer_id:
                return jsonify({'error': 'Cross-customer access forbidden'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
